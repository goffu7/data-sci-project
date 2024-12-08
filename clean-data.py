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
    
        
        
        # Get author-group from head
        affiliations = data.get("abstracts-retrieval-response", {}).get("affiliation",[])
        chulalongkorn_found = False
        # Skip if author-group is empty
        for affiliation in affiliations:
            if not isinstance(affiliation, dict):
                continue
            country = affiliation.get("affiliation-country", "")
            affiliation_name = affiliation.get("affilname", [])

            # Check if "Chulalongkorn University" is mentioned
            if affiliation_name and(  "Chulalongkorn University" == affiliation_name):
                chulalongkorn_found = True
            else:
                chulalongkorn_found = False

        for affiliation in affiliations:
            if not isinstance(affiliation, dict):
                continue
            country = affiliation.get("affiliation-country", "")
            affiliation_name = affiliation.get("affilname", [])

            if chulalongkorn_found and affiliation_name is not "Chulalongkorn University" :
                organization_data.append({
                    "paper_id": paper_id,
                    "affiliation": affiliation_name,
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
