
"""
    Authors: Dario Di Meo, Leonardo Alberto Anania
    Description: Streamlit dashboard for 2nd homework of the 2022/2023 Big Data cource
"""

# External module
import streamlit as st
import numpy as np

# Python native modules
import json

# Streamlit page config
st.set_page_config(
    # layout='wide',
    page_icon='📈',
    page_title='Dashboard Big Data'
)

# Introduction page
st.title("📜🎉 800 anni Federico II")

st.subheader(
    "In questa dashboard inseriremo alcuni grafici relativi ai fondi istanziati dall'unione europea per la Federico II. Nella sidebar si possono trovare i vari grafici disponibili."
)
st.image('assets/Logo.png')

st.write(" Per effetturare le seguenti query abbiamo caricato il dataset su mongoDB e su Neo4j, Il codice per caricare i dataset sui due database è visualizzabile nei menu' a tendina qui' sotto.")

mongo = '''
from pymongo import MongoClient
import pandas as pd
import json
import numpy as np

# Loading grants file with pandas
grants = pd.read_excel('grant.xlsx')

db = client.federicoii
collection = db.grants_collection

obj = []

for idx, row in enumerate(grants.iterrows()):
    row = row[1]
    obj.append(
        {
            "Grant ID":row["Grant ID"],
            "Title":row["Title"],
            "Funding Amount in EUR":row["Funding Amount in EUR"],
            "Start Year":row["Start Year"],
            "End Year":row["End Year"],
            "Country of Research organization":[r.strip() for r in str(row["Country of Research organization"]).split(';')] if not pd.isnull(row["Country of Research organization"]) else [],
            "Funder":row["Funder"],
            "Fields of Research":[r.strip() for r in str(row["Fields of Research (ANZSRC 2020)"]).split(';')] if not pd.isnull(row["Fields of Research (ANZSRC 2020)"]) else [],
            "Units of Assessment":[r.strip() for r in str(row["Units of Assessment"]).split(';')] if not pd.isnull(row["Units of Assessment"]) else [],
            "Sustainable Development Goals":[r.strip() for r in str(row["Sustainable Development Goals"]).split(';')] if not pd.isnull(row["Sustainable Development Goals"])  else [],
        }
    )
collection.insert_many(obj)
'''
cypher = '''
import numpy as np
import pandas as pd
from neo4j import GraphDatabase

df = pd.read_csv('hmw1.csv',sep=';',header=0); df.head()
graph = GraphDatabase.driver(SECRET);

# Estrazione delle Informazioni dal csv
reserch_projects = df[['Grant ID','Title translated','Start Year','End Year']]; 
themes = df['Fields of Research (ANZSRC 2020)'].str.split(';').explode().str.strip().str.lower().unique();
funders = df['Funder'].str.lower().unique(); 
researchers = df['Researchers'].str.split(',').explode().str.strip().str.lower().unique(); 
research_organizzations = df['Research Organization - standardized'].str.split(';').explode().str.strip().str.lower().unique(); 
countries = df['Country of Research organization'].str.split(';').explode().str.strip().str.lower().unique();
unitOfAssessment = df['Units of Assessment'].str.split(";").explode().str.strip().str.lower().unique(); 
goals = df['Sustainable Development Goals'].str.split(';').explode().str.strip().str.lower().unique(); 

# Creazione dei Nodi
session = graph.session()

ths = np.char.split(themes.astype(str),maxsplit=1); 
units = np.char.split(unitOfAssessment.astype(str),maxsplit=1); 
gls = np.char.split(goals.astype(str),maxsplit=1)

code_ths = [item[0] if item != ['nan'] else np.nan for item in ths]; 
code_units = [item[0] if item != ['nan'] else np.nan for item in units]; 
code_gls = [item[0] if item != ['nan'] else np.nan for item in gls]

text_ths = [item[1] if item != ['nan'] else np.nan for item in ths]; 
text_units = [item[1] if item != ['nan'] else np.nan for item in units]; 
text_gls = [item[1] if item != ['nan'] else np.nan for item in gls]

for code, name in zip(code_ths,text_ths): session.run(f"CREATE (N:Theme {{name:'{name}', code:'{code}'}})")
for code, name in zip(code_units,text_units): session.run(f"CREATE (N:UnitOfAssessment {{name:'{name}', code:'{code}'}})")
for code, name in zip(code_gls,text_gls): session.run(f"CREATE (N:Goal {{name:'{name}', code:'{code}'}})")
for country in countries: session.run(f"CREATE (N:Country {{name:'{country}'}})")
for funder in funders: session.run(f'CREATE (N:Funder {{name:"{funder}"}})')
for researcher in researchers: session.run(f'CREATE (N:Researcher {{name_surname:"{researcher}"}})')
for research_organizzation in research_organizzations: 
   try: session.run(f'CREATE (N:ResearcherOrganizzation {{name:"{research_organizzation}"}})')
   except: session.run(f"CREATE (N:ResearcherOrganizzation {{name:'{research_organizzation}'}})")
for i, row in reserch_projects.iterrows(): #1176
   try: 
     session.run(f'CREATE (N:Project {{grant_id:"{row["Grant ID"]}",title:"{row["Title translated"]}",start_year:"{row["Start Year"]}",end_year:"{row["End Year"]}"}})')
   except: 
     session.run(f"CREATE (N:Project {{grant_id:'{row['Grant ID']}',title:'{row['Title translated']}',start_year:'{row['Start Year']}',end_year:'{row['End Year']}'}})")

# Creazione degli Archi
for _,row in df.iterrows(): 
    # Ricercatore -Partecitpa-> Projects 
    if(type(row['Researchers']) != float):
        for researcher in row['Researchers'].split(", "):
            session.run(f'match(r:Researcher{{name_surname:"{researcher.lower()}"}}),(p:Project{{grant_id: "{row["Grant ID"]}"}}) create(r)-[w:PARTICIPATE]->(p) return type(w)')
    else: session.run(f"match(r:Researcher{{name_surname:'nan'}}),(p:Project{{grant_id: '{row['Grant ID']}'}}) create(r)-[w:PARTICIPATE]->(p) return type(w)")

    # Organizzazioni_di_ricerca -Associato->  Projects
    for researcher_organizzation in set(row['Research Organization - standardized'].split("; ")):
        try: session.run(f'match(ro:ResearcherOrganizzation{{name:"{researcher_organizzation.lower()}"}}),(p:Project{{grant_id: "{row["Grant ID"]}"}}) create(ro)-[w:ASSOCIATED]->(p) return type(w)')
        except: session.run(f"match(ro:ResearcherOrganizzation{{name:'{researcher_organizzation.lower()}'}}),(p:Project{{grant_id: '{row['Grant ID']}'}}) create(ro)-[w:ASSOCIATED]->(p) return type(w)")

    # Funder_group -Finanzia{funding_amount_in_eur}-> Project
    try: session.run(f'match(f:Funder{{name:"{row["Funder"].lower()}"}}),(p:Project{{grant_id: "{row["Grant ID"]}"}}) create(f)-[w:FINANCE{{funding_amount_in_eur: "{row["Funding Amount in EUR"]}"}}]->(p) return type(w)')
    except: session.run(f"match(f:Funder{{name:'{row['Funder'].lower()}'}}),(p:Project{{grant_id: '{row['Grant ID']}'}}) create(f)-[w:FINANCE{{funding_amount_in_eur: '{row['Funding Amount in EUR']}'}}]->(p) return type(w)")

    # Project -Localizzato-> Country_of_research 
    for country in row['Country of Research organization'].split("; "): 
        session.run(f'match(p:Project{{grant_id: "{row["Grant ID"]}"}}),(c:Country{{name:"{country.lower()}"}}) create(p)-[w:LOCALIZED]->(c) return type(w)')
    
    # Project -Argomento-> Theme
    if(type(row['Fields of Research (ANZSRC 2020)']) != float):
       for unit in row['Fields of Research (ANZSRC 2020)'].split("; "):
           session.run(f'match(p:Project{{grant_id: "{row["Grant ID"]}"}}),(t:Theme{{code:"{unit.split(" ")[0].lower()}"}}) create(p)-[w:TOPIC]->(t) return type(w)')
    else: session.run(f'match(p:Project{{grant_id: "{row["Grant ID"]}"}}),(t:Theme{{code:"nan"}}) create(p)-[w:TOPIC]->(t) return type(w)')

    # Project -Tematica-> Units_of_Assestment 
    if(type(row['Units of Assessment']) != float):
        for unit in row['Units of Assessment'].split("; "):
            session.run(f'match(p:Project{{grant_id: "{row["Grant ID"]}"}}),(u:UnitOfAssessment{{code:"{unit.split(" ")[0].lower()}"}}) create(p)-[w:THEMATIC]->(u) return type(w)')
    else: session.run(f'match(p:Project{{grant_id: "{row["Grant ID"]}"}}),(u:UnitOfAssessment{{code:"nan"}}) create(p)-[w:THEMATIC]->(u) return type(w)')

    # Project -Scopo-> Sustainable_Development_Goals 
    if(type(row['Sustainable Development Goals']) != float):
        for goal in row['Sustainable Development Goals'].split("; "): 
            session.run(f'match(p:Project{{grant_id: "{row["Grant ID"]}"}}),(g:Goal{{code:"{goal.split(" ")[0].lower()}"}}) create(p)-[w:PURPOSE]->(g) return type(w)')
    else: session.run(f'match(p:Project{{grant_id: "{row["Grant ID"]}"}}),(g:Goal{{code:"nan"}}) create(p)-[w:PURPOSE]->(g) return type(w)')
'''
with st.expander("Caricamento dei dati su MongoDB"):
    st.code(mongo)
with st.expander("Caricamento dei dati su Neo4J"):
    st.code(cypher)