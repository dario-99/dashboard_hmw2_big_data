"""
    Authors: Dario Di Meo, Leonardo Alberto Anania
    Description: Streamlit dashboard for 2nd homework of the 2022/2023 Big Data cource
"""

# External module
import streamlit as st
from pymongo import MongoClient
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import pandas as pd

# Python native modules
import time
import json

# Streamlit page config
st.set_page_config(
    # layout='wide',
    page_icon='📈',
    page_title='Dashboard Big Data'
)

@st.cache_data 
def load_data(units):
    elem = []
    for unit in units:
        elem += list(collection.find({"Units of Assessment" : unit}))
    return elem


st.title("📈 Topic piu' finanziati")

st.write("Topic piu' finanziati all' andare del tempo, per far partire l'animazione selezionare le units of assessment nella sidebar e in seguito far partire l'animazione con il tasto play")

# Mongo connection
uri = st.secrets.DB_URI
client = MongoClient(uri)
db = client.federicoii
collection = db.grants_collection

units_of_assestment = list(collection.distinct("Units of Assessment"))

units_selected = ["B11 Computer Science and Informatics", "B12 Engineering", "B08 Chemistry", "A01 Clinical Medicine"]


units_selected = st.sidebar.multiselect(
    'Scegli il Topic',
    units_of_assestment,
    default=["B11 Computer Science and Informatics", "B12 Engineering", "B08 Chemistry", "A01 Clinical Medicine"],
)

data = load_data(units_selected)
df = pd.DataFrame(data)
df = df.fillna(value=0)
df = df.explode('Units of Assessment')
df = df[df['Units of Assessment'].isin(units_selected)]

# st.write(df)
df_grouped = df.groupby(['Start Year', 'Units of Assessment'])['Funding Amount in EUR'].sum().unstack(fill_value=0).stack().reset_index()


df_grouped['cumsum'] = df_grouped.groupby(['Units of Assessment'])[0].cumsum()

fig = px.bar(
    df_grouped,
    x='Units of Assessment',
    y='cumsum',
    animation_frame='Start Year',
    animation_group='Units of Assessment',
    range_y=[0,df_grouped['cumsum'].max()],
    color='Units of Assessment',
    width=1000,
    height=700,
)
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
            "sum":{
                "$sum":"$Funding Amount in EUR"
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
RETURN p.start_year,u.name,sum(toInteger(r.funding_amount_in_eur))
'''
with st.expander("Query con MongoDB"):
    st.code(mongo)
with st.expander("Query con Cypher"):
    st.code(cypher, language='cypher')
    st.image("assets/q1.PNG")
