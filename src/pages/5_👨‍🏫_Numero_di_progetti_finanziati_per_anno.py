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

st.title("👨‍🏫 Numero di progetti finanziati per anno")

st.write("Grafico che mostra il numero di progetti finanziati per anno della Federico II")

df = pd.read_csv("dataset/3_numero_progetti_finanziati_per_anno.txt", sep='\t')

count_anno_chart = px.bar(df, x='anno', y='count', color='count', color_continuous_scale='Inferno')
st.plotly_chart(count_anno_chart)

mongo = '''
res = list(collection.aggregate([
    {
        "$group" :{
            "_id" : {
                "Anno":"$Start Year",
            },
            "count": {
                "$count":{}
            } 
        },
    },
    {
            "$sort": {"_id": 1}
    }
]))
'''
cypher = '''
MATCH (p:Project)
RETURN p.start_year,count(*)
ORDER BY p.start_year ASC
'''
with st.expander("Query con MongoDB"):
    st.code(mongo)
with st.expander("Query con Cypher"):
    st.code(cypher, language='cypher')
    st.image("assets/q5.PNG")
