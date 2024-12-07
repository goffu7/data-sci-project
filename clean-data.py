import os
import glob
import json
import pandas as pd
from hashlib import sha256

all_papers = []
all_keywords = []
all_subjects = []
organization_data = []

for file_year in range(2018, 2024):
    print(f"Processing year: {file_year}",end="  ")
    folder_path = f"res\\{file_year}"  # Update this to your folder path
    json_files = glob.glob(os.path.join(folder_path, "*"))

    for file in json_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract relevant data
        bib = data.get("abstracts-retrieval-response", {}).get("item", {}).get("bibrecord", {})
        title = bib.get("head", {}).get("citation-title", None)
        process_info = data.get("abstracts-retrieval-response", {}).get("authkeywords", {})
        author_keywords = process_info.get("author-keyword", []) if isinstance(process_info, dict) else []
        subject_area = data.get("abstracts-retrieval-response", {}).get("subject-areas", {}).get("subject-area", [])
        subject_area = subject_area if isinstance(subject_area, list) else []

        if not title:
            continue

        # Generate a unique ID for the paper
        paper_id = sha256(title.encode('utf-8')).hexdigest()

        # Add paper details to the main table
        all_papers.append({"paper_id": paper_id, "year": file_year, "title": title})

        # Add keywords to the keyword table
        for keyword in author_keywords:
            if isinstance(keyword, dict):
                all_keywords.append({"paper_id": paper_id, "keyword": keyword.get("$", "")})

        # Add subjects to the subject table
        for subject in subject_area:
            all_subjects.append({
                "paper_id": paper_id,
                "subject_area": subject.get("$", ""),
                "subject_code": subject.get("@code", ""),
                "subject_abbrev": subject.get("@abbrev", ""),
            })
    
        
        head = bib.get("head", {})
        
        # Get author-group from head
        author_groups = head.get("author-group", [])
        
        # Skip if author-group is empty
        for author_group in author_groups:
            # Ensure author_group is a dictionary, otherwise skip it
            if not isinstance(author_group, dict):
                continue

            affiliation = author_group.get("affiliation", {})
            
            # Skip if no affiliation found
            if not affiliation:
                continue

            country = affiliation.get("country", "")
            organizations = affiliation.get("organization", [])
            
            # Ensure organizations is a list
            if not isinstance(organizations, list):
                organizations = [organizations]

            chulalongkorn_found = False  # Flag to check if Chulalongkorn is present in the organizations

            # Check if "Chulalongkorn University" is present in the list of organizations
            for org in organizations:
                organization_name = org.get("$", "") if isinstance(org, dict) else org
                
                # Check if "Chulalongkorn University" is mentioned
                if organization_name and(  "Chulalongkorn University" in organization_name):
                    chulalongkorn_found = True
                else:
                    chulalongkorn_found = False
            
            # If Chulalongkorn University is found, save all other organizations in the list
            if chulalongkorn_found:
                for org in organizations:
                    organization_name = org.get("$", "") if isinstance(org, dict) else org
                    # Add other organizations if they aren't Chulalongkorn University
                    if "Chulalongkorn University" != organization_name:
                        organization_data.append({
                            "paper_id": paper_id,
                            "organization": organization_name,
                            "country": country
                        })




# Convert to DataFrames
df_papers = pd.DataFrame(all_papers).drop_duplicates()
df_keywords = pd.DataFrame(all_keywords).drop_duplicates()
df_subjects = pd.DataFrame(all_subjects).drop_duplicates()
df_organizations = pd.DataFrame(organization_data).drop_duplicates()

# Save to CSV or process further
print("Paper Details:")
print(df_papers.shape)

print("\nKeywords:")
print(df_keywords.shape)

print("\nSubjects:")
print(df_subjects.shape)

print("\nOrganizations:")
print(df_organizations.shape)


# Merge papers with keywords on 'paper_id'
papers_keywords = pd.merge(df_papers, df_keywords, on="paper_id", how="inner")

# Merge the resulting DataFrame with subjects on 'paper_id'
papers_keywords_subjects = pd.merge(papers_keywords, df_subjects, on="paper_id", how="inner")

papers_keywords_subjects_org = pd.merge(papers_keywords_subjects, df_organizations, on="paper_id", how="inner")

print("Final DataFrame Shape:", papers_keywords_subjects_org.shape)
print(papers_keywords_subjects_org)

# Save to CSV
papers_keywords_subjects_org.to_csv("final_data.csv", index=False)
