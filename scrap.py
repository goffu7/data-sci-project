import requests
import xml.etree.ElementTree as ET
import pandas as pd

# ฟังก์ชันดึงข้อมูลจาก DBLP API
def fetch_data_from_dblp(start_index, num_results):
    url = f"https://dblp.org/search/publ/api?q=machine+learning&start={start_index}&count={num_results}&format=xml"
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Request failed for start index {start_index}")
        return None

# ฟังก์ชันในการแปลง XML เป็น DataFrame
def parse_dblp_xml(xml_data):
    tree = ET.ElementTree(ET.fromstring(xml_data))
    root = tree.getroot()
    
    records = []
    
    for hit in root.findall('.//hit'):
        title = hit.find('.//title').text if hit.find('.//title') is not None else None
        authors = [author.text for author in hit.findall('.//author')] if hit.findall('.//author') else []
        venue = hit.find('.//venue').text if hit.find('.//venue') is not None else None
        publisher = hit.find('.//publisher').text if hit.find('.//publisher') is not None else None
        entry_type = hit.find('.//type').text if hit.find('.//type') is not None else None
        
        records.append({
            'title': title,
            'authors': ', '.join(authors),  # รวมชื่อผู้เขียนเป็นคอมมา
            'venue': venue,
            'publisher': publisher,
            'entry_type': entry_type
        })
    
    return pd.DataFrame(records)

# ตัวอย่างการดึงข้อมูล 100 บทความ
xml_data = fetch_data_from_dblp(0, 1000)

if xml_data:
    df = parse_dblp_xml(xml_data)
    print(df.head())  # แสดงข้อมูลแรก 5 บรรทัด
    df.to_csv('dblp_papers2.csv', index=False)  # บันทึกเป็นไฟล์ CSV
