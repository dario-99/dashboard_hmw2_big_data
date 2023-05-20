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

st.title("💸 Fondi ricevuti per anno")

st.write("Fondi ricevuti per anno nei progetti della Federico II")

df = pd.read_csv("dataset/5_fondi_ricevuti_per_anno.txt", sep='\t')

count_anno_chart = px.bar(df, x='anno', y='fondi', color='fondi', color_continuous_scale='Inferno')
st.plotly_chart(count_anno_chart)

mongo = '''
res = list(collection.aggregate([
    {
        "$group" :{
            "_id" : {
                "Anno":"$Start Year",
            },
            "sum": {
                "$sum":"$Funding Amount in EUR"
            } 
        },
    },
    {
            "$sort": {"_id": 1}
    }
]))
'''
cypher = '''
MATCH (p:Project)-[r:FINANCE]-(f:Funder)
RETURN p.start_year,sum(toFloat(r.funding_amount_in_eur))
'''
with st.expander("Query con MongoDB"):
    st.code(mongo)
with st.expander("Query con Cypher"):
    st.code(cypher, language='cypher')