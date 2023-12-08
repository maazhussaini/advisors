import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector as sql
from mysql.connector import errorcode
from mysql.connector import Error
import altair as alt
import json


def database_connection():
    f = open("config.json")
    configData = json.load(f)
    conn = sql.connect(host=configData['dbConnection']['host'],
                   user=configData['dbConnection']['user'],
                   password=configData['dbConnection']['password'],
                   database=configData['dbConnection']['dbName'])
    return conn

st.title('HBE Data')

def custom_chart(conn):
    selected_data = pd.DataFrame()
    custom_query = st.text_area("Write your query here...")
    if custom_query:
        try:

            sales_data = pd.read_sql_query(custom_query, conn)

            # First Column Choice
            selected_column_list = sales_data.columns.to_list()
            selected_column_list.insert(0, '')
            selected_column1 = st.selectbox('Select columns for the chart', selected_column_list)


            # Second Column Choice
            selected_column_list_2 = selected_column_list.copy()
            selected_column_list_2.remove(selected_column1)
            selected_column2 = st.selectbox('Select columns for the chart', selected_column_list_2)
            
            selected_data = sales_data[[selected_column1, selected_column2]]

            if st.bar_chart(selected_data, x=selected_column1, y=selected_column2):
                st.balloons()


        except Error as e:
            st.error(e.msg)
        if not selected_data.empty:
            showData = st.checkbox("Show Data")
            if showData:
                st.dataframe(selected_data, use_container_width=True)
        
conn = database_connection()
st.write('')
st.write('')

years = ["", 2018, 2019, 2020, 2021, 2022, 2023]
selected_year = st.selectbox('Select columns for the chart', years)
if selected_year:
    pass

custom_chart(conn)