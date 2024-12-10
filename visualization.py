import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import community.community_louvain as community_louvain
import itertools
import plotly.express as px
import seaborn as sns

# โหลดไฟล์ CSV
df = pd.read_csv('final_data.csv')

# แสดงเฉพาะคอลัมน์ที่ต้องการ
columns_to_display = ['title', 'subject_area', 'subject_abbrev', 'affiliation', 'country', 'city', 'index_term']
st.write(df[columns_to_display])

# สร้างฮิสโตแกรมแสดงข้อมูล 20 ตัวที่สำคัญที่สุด
fig, ax = plt.subplots(figsize=(20, 8))  # ขยายความกว้างของฮิสโตแกรม
top_20_affiliations = df['affiliation'].value_counts().nlargest(20)
top_20_affiliations.plot(kind='bar', ax=ax)
ax.set_title('Histogram Affiliation (Top 20)', fontsize=14)
ax.set_xlabel('Affiliation', fontsize=12)
ax.set_ylabel('Count', fontsize=12)
ax.tick_params(axis='x', labelsize=15)  # ลดขนาดตัวอักษรของแกน x
ax.tick_params(axis='y', labelsize=15)  # ลดขนาดตัวอักษรของแกน y
st.pyplot(fig)

# df = df.dropna(subset=['affiliation', 'index_term'])  # ลบแถวที่มี NaN
# df = df[df['affiliation'].str.strip() != '']  # ลบค่าว่างใน affiliation
# df['index_term'] = df['index_term'].fillna('Unknown')  # แทนที่ NaN ใน index_term

# # เลือกเฉพาะ top 10 affiliations
# top_affiliations = df['affiliation'].value_counts().nlargest(30).index
# filtered_df = df[df['affiliation'].isin(top_affiliations)]

# # สร้างกราฟ
# graph = nx.Graph()

# # ใช้เฉพาะ 1 index_term ต่อ affiliation
# for _, row in filtered_df.iterrows():
#     affiliation = row['affiliation']
#     index_terms = str(row['index_term']).split(';')[:2]  # ใช้ 1 term แรก
#     for term in index_terms:
#         term = term.strip()
#         if term:  # เช็คว่า term ไม่ว่าง
#             graph.add_edge(affiliation, term)

# # ลบโหนดที่ไม่มีชื่อ
# graph.remove_nodes_from([node for node in graph.nodes if not node or pd.isna(node)])

# # กรองโหนดที่มี degree > 2
# filtered_nodes = [node for node, degree in graph.degree() if degree > 2]
# graph = graph.subgraph(filtered_nodes)

# # ใช้ Kamada-Kawai Layout
# pos = nx.kamada_kawai_layout(graph)

# # แบ่ง community
# partition = community_louvain.best_partition(graph)

# # กำหนดสีตาม community
# colors = [partition[node] for node in graph.nodes]

# # แสดงกราฟ
# plt.figure(figsize=(20, 15))  # ปรับขนาดกราฟ
# nx.draw_networkx_edges(graph, pos, alpha=0.5, edge_color="gray")
# nx.draw_networkx_nodes(
#     graph, pos, node_color=colors, cmap=plt.cm.tab10, node_size=300
# )

# # แสดง label เฉพาะโหนดที่สำคัญ (degree > 3)
# labels = {node: node for node, degree in graph.degree() if degree > 3}
# nx.draw_networkx_labels(graph, pos, labels, font_size=8)

# plt.title('Simplified Graph with Reduced Nodes and Edges', fontsize=16)
# st.pyplot(plt)

# สร้าง Pie chart สำหรับแสดงจำนวนของ listings ตามประเทศ
fig_pie = px.pie(df, names='country', title='Number of Listings by Country')
st.plotly_chart(fig_pie)

# scattering plot

# กรองข้อมูลที่มี NaN ในคอลัมน์ affiliation หรือ index_term
df['index_terms_list'] = df['index_term'].fillna('').apply(lambda x: str(x).split(';'))

# คำนวณจำนวน Index Terms ทั้งหมดของแต่ละ affiliation
affiliation_data = (
    df.groupby('affiliation')['index_terms_list']
    .apply(lambda x: sum(len(terms) for terms in x))
    .reset_index()
    .rename(columns={'index_terms_list': 'total_index_terms'})
)

# คำนวณจำนวน Occurrences ของแต่ละ affiliation
affiliation_data['occurrences'] = df['affiliation'].value_counts().reindex(affiliation_data['affiliation']).values

# คัดเฉพาะ top 15 affiliations ตามจำนวน Occurrences
top_affiliations = affiliation_data.nlargest(15, 'occurrences')

# สร้างกราฟ
plt.figure(figsize=(12, 8))
sns.scatterplot(
    data=top_affiliations,
    x='occurrences',
    y='total_index_terms',
    hue='affiliation',
    palette='tab10',
    s=200,
    alpha=0.8
)

# ตกแต่งกราฟ
plt.title('Affiliation Collaboration: Total Index Terms by Affiliation', fontsize=16)
plt.xlabel('Number of Occurrences (Affiliation)', fontsize=12)
plt.ylabel('Total Number of Index Terms', fontsize=12)
plt.legend(title='Affiliation', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(alpha=0.3)

# แสดงผล
plt.tight_layout()
st.pyplot(plt)
