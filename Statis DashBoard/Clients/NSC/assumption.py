import plotly.graph_objs as go
from plotly.subplots import make_subplots
import streamlit as st
import pandas as pd
import plotly.express as px
import json

# @st.cache_data
def read_excel_file(sheet_name='INCOME STATEMENT'):
    try:
        file_path = "E:/MaazProducts/Fiverr/Platform/advisors/Statis DashBoard/SourceData/NSC/Financial Statement - Copy.xlsx"
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        df = df.drop('Note', axis=1)
        return df
    except:
        st.warning("Please, select the sheet name.")

@st.cache_data
def process_sheet(df):
    df = df.transpose().reset_index()
    new_header = df.iloc[0].to_list()
    
    for i, value in enumerate(new_header):
        new_header[i] = str(value).lower().strip()
    
    df = df[1:]
    df.columns = new_header
    df.reset_index(drop=True, inplace=True)
    df = df.rename(columns={df.columns[0]: 'year'})
    
    # change from int to str
    df['year'] = df['year'].astype('int')
    return df

@st.cache_data
def temprory_dataload():
    file_path = "E:/MaazProducts/Fiverr/Platform/advisors/Statis DashBoard/SourceData/NSC/NSC - Financial Model - 310124 - MH.xlsx"
    df = pd.read_excel(file_path, sheet_name="Rev")
    df.fillna(0)
    return df

def is_not_string(item):
    return not isinstance(item, str)

def assumption_details():    
    historical_df = read_excel_file(sheet_name='INCOME STATEMENT')
    
    revenue_df = historical_df[:3:3]
    revenue_df = process_sheet(revenue_df)
    
    st.dataframe(revenue_df, hide_index=True)
    
    year_list = revenue_df['year'].tolist()
    
    st.write(year_list)


assumption_details()