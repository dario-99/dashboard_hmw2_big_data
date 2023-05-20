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

st.title("❤ Top finanziatori della federico II")

st.write("I finanziatori che hanno donato piu' soldi alla ricerca nei progetti in cui è coinvolta la Federico II")

df = pd.read_csv("dataset/8_top_finanziatori.txt", sep='\t')

num_funders = st.slider(min_value=2, max_value=len(df), label='numero di finanziatori', step=1, value=10)
campi_chart = px.bar(df[:num_funders], x='funder', y='funds', color='funds')
st.plotly_chart(campi_chart)

mongo = '''
res = list(collection.aggregate([
    {
        "$match": {
            "Funding Amount in EUR": { "$ne": "NaN" }
        }
    },
    {
         "$group" :{
            "_id" : {
                "Funders":"$Funder",
            },
            "fondi": {
                    "$sum": {
                        "$cond": [
                            { "$eq": ["$Funding Amount in EUR", "NaN"] },
                            0,
                            { "$ifNull": ["$Funding Amount in EUR", 0] }
                        ]
                    }
                }
            } 
        },
        {
            "$sort": {"fondi": -1}
        }
]))
'''
cypher = '''
MATCH (f:Funder)-[r:FINANCE]-(p:Project)
RETURN f,sum(toFloat(r.funding_amount_in_eur))as funds
ORDER BY funds DESC
'''
with st.expander("Query con MongoDB"):
    st.code(mongo)
with st.expander("Query con Cypher"):
    st.code(cypher, language='cypher')