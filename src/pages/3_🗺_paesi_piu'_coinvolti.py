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
import os

# Streamlit page config
st.set_page_config(
    # layout='wide',
    page_icon='📈',
    page_title='Dashboard Big Data'
)

st.title("🗺 Paesi con piu' collaborazioni")

st.write("Vediamo i paesi che hanno collaborato di piu' con la federico II")

df = pd.read_csv("dataset/6_countries_coinvolti_fix.txt", sep='\t')

df['lon'].astype('float')
df['lat'].astype('float')
fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        zoom=0.5,
        size='count',
        color='count',
        color_continuous_scale='Bluered',
        hover_name="country"
    )
fig.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig)

mongo = '''
res = list(collection.aggregate([
    {
        "$unwind":{
            "path": "$Country of Research organization"
        }
    },
    {
        "$match":{
            "Country of Research organization": {"$ne":"Italy"}
        }
    },
    {
         "$group" :{
            "_id" : {
                "Country":"$Country of Research organization",
            },
            "count":{
                "$count":{}
            }
        } 
    },
    {
        "$sort": {"count": -1}
    }
]))
'''
cypher = '''
MATCH (c:Country WHERE c.name <> "italy")-[r:LOCALIZED]-(p:Project)
RETURN c,count(r) as num 
ORDER BY num DESC
'''
with st.expander("Query con MongoDB"):
    st.code(mongo)
with st.expander("Query con Cypher"):
    st.code(cypher, language='cypher')