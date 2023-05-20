"""
    Authors: Dario Di Meo, Leonardo Alberto Anania
    Description: Streamlit dashboard for 2nd homework of the 2022/2023 Big Data cource
"""

# External module
import streamlit as st
from pymongo import MongoClient
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from streamlit_echarts import st_echarts


# Python native modules
import json
import time

# Streamlit page config
st.set_page_config(
    # layout='wide',
    page_icon='📈',
    page_title='Dashboard Big Data'
)

st.title("📈 Topic piu' finanziati in relazione al numero di progetti")

st.write("Topic piu' finanziati rappresentato come un bubble chart in cui sull'asse x abbiamo la somma cumulativa dei fondi stanziati e sull'asse y il numero di progetti")

# Mongo connection
uri = st.secrets.DB_URI
client = MongoClient(uri)
db = client.federicoii
collection = db.grants_collection

# Load dati
units_of_assestment = list(collection.distinct("Units of Assessment"))
units_selected = ["B11 Computer Science and Informatics", "B12 Engineering", "B08 Chemistry", "A01 Clinical Medicine"]


# Sidebar select units
units_selected = st.sidebar.multiselect(
    'Scegli il Topic',
    units_of_assestment,
    default=["B11 Computer Science and Informatics", "B12 Engineering", "B08 Chemistry", "A01 Clinical Medicine"],
    )


res = [list(collection.aggregate([
    {
        "$match":{
            "Units of Assessment":unit
        }
    },
    {
         "$group" :{
            "_id" : {
                "Start Year":"$Start Year",
                "Units of Assessment":unit
            },
            "sum":{
                "$sum":"$Funding Amount in EUR"
            },
            "count":{
                "$count":{}
            }
        } 
    },
    {
        "$sort": {"_id": 1}
    }
])) for unit in units_selected]

# st.write(res)
df = pd.DataFrame(
    columns=["Start Year", "Unit of Assessment", "count", "sum"]
)


for unit in res:
    for year in unit:
        df.loc[len(df)] = [year['_id']['Start Year'], year['_id']['Units of Assessment'], year['count'], year['sum']]
df = df.fillna(value=0)

# Generazione di tutte le possibili combinazioni di anno e topic
combinations = pd.MultiIndex.from_product([df['Start Year'].unique(), df['Unit of Assessment'].unique()], names=['Start Year', 'Unit of Assessment'])

# Utilizzo di reindex per ottenere un DataFrame con tutte le combinazioni
df = df.set_index(['Start Year', 'Unit of Assessment']).reindex(combinations, fill_value=0).reset_index()
df = df.sort_values(by='Start Year')
df['sum'] = df.groupby('Unit of Assessment')['sum'].cumsum()
df['count'] = df.groupby('Unit of Assessment')['count'].cumsum()

# Stampa del DataFrame risultante
# st.write(df_all_combinations)

# Generazione del bubble chart utilizzando Plotly Express
fig = px.scatter(
    df,
    x='sum',
    y='count',
    size='sum',
    size_max=30, 
    animation_frame='Start Year', 
    animation_group='Unit of Assessment', 
    range_x=[0, df['sum'].max()+50_000_000],
    range_y=[0, df['count'].max()+20],
    color="Unit of Assessment",
    width=1000,
    height=700,
)

# Aggiunta di etichette agli assi
fig.update_layout(
    xaxis_title='sum',
    yaxis_title='count',
    title='Bubble Chart'
)
# Mostra il grafico animato
st.plotly_chart(fig)

mongo = '''
res = list(collection.aggregate([
    {
        "$match":{
            "Units of Assessment":unit
        }
    },
    {
         "$group" :{
            "_id" : {
                "Start Year":"$Start Year",
                "Units of Assessment":unit
            },
            "count":{
                "$count":{}
            }
        } 
    },
    {
        "$sort": {"_id": 1}
    }
]))
'''
cypher = '''
MATCH (f:Funder)-[r:FINANCE]-(p:Project)-[r2:THEMATIC]-(u:UnitOfAssessment)
WHERE u.code="b11"
RETURN p.start_year,u.name,count(*)
'''
with st.expander("Query con MongoDB"):
    st.code(mongo)
with st.expander("Query con Cypher"):
    st.code(cypher, language='cypher')