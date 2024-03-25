import plotly.graph_objs as go
from plotly.subplots import make_subplots
import streamlit as st
import pandas as pd
import plotly.express as px
import json

# filePathfs = "E:/MaazProducts/Fiverr/Platform/advisors/Statis DashBoard/SourceData/NSC/Financial Statement.xlsx"

@st.cache_data
def read_excel_file(file_path, sheet_name=None):
    file_path = "E:/MaazProducts/Fiverr/Platform/advisors/Statis DashBoard/SourceData/NSC/Financial Statement - Copy.xlsx"
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df = df.drop('Note', axis=1)
    return df

@st.cache_data
def process_sheet(df):
    
    try:
        df = df.drop('Select', axis=1)
        df = df.drop('BASE', axis=1)
    except:
        pass
    
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
def read_assumption_file():
    filePath_assumption = "E:/MaazProducts/Fiverr/Platform/advisors/Statis DashBoard/SourceData/NSC/Assumption.xlsx"
    df_assumption = pd.read_excel(filePath_assumption)
    
    new_column_position = 2  # Position after 'A'
    new_column_name = 'Select'
    new_column_values = True

    df_assumption.insert(loc=new_column_position, column=new_column_name, value=new_column_values)

    df_assumption['Select'] = True
    # df_assumption.at[0, 'Select'] = True
    
    df_assumption = st.data_editor(df_assumption, hide_index=True)
    df_assumption = df_assumption[df_assumption['Select'] == True]
    
    return df_assumption


def is_crnt(df_assumption, predicted_year):
            
    df_fs = read_excel_file(file_path='', sheet_name='INCOME STATEMENT')
    df_fs = process_sheet(df_fs)
    
    year_fs = df_fs['year'].to_list()
    last_year = year_fs[-1]
    df_fs_last_year = df_fs[df_fs['year'] == last_year]
    
    new_row_list = []
    
    for no_year in range(predicted_year):
        new_row = {}
        df_assumption_last_year = df_assumption[df_assumption['year'] == last_year]
        df_assumption_current_year = df_assumption[df_assumption['year'] == last_year + 1]
        
        if not df_assumption_last_year.empty and not df_assumption_current_year.empty:
            
            for i in df_fs.columns.to_list():
                if i == 'year':
                    value = last_year + 1
                else:
                    value = 0
                    
                if no_year == 0:    
                    if i in df_assumption_last_year.columns.to_list():
                        
                        if i == 'revenue' or i == 'general and administrative expenses':
                            value = (1 + df_assumption_current_year[i].values[0]) * df_fs_last_year[i].values[0]
                        
                        elif i == 'selling and marketing expenses':
                            value =  -1 + df_assumption_current_year[i].values[0] * df_fs_last_year[i].values[0]
                        
                    elif i == 'cost of revenues':
                        value = -1 * (1 - df_assumption_current_year['gp margin'].values[0]) * df_fs_last_year[i].values[0]
                        
                            
                else:
                    if i in list(new_row_list[-1].keys()):
                        
                        if i == 'revenue' or i == 'general and administrative expenses':
                            value = (1 + df_assumption_current_year[i].values[0]) * new_row_list[-1][i]
                            
                        
                        elif i == 'selling and marketing expenses':
                            value =  -1 + df_assumption_current_year[i].values[0] * new_row_list[-1][i]
                        
                        elif i == 'cost of revenues':
                            value = -1 * (1 + df_assumption_current_year['gp margin'].values[0]) * new_row_list[-1][i]
                
                new_row[i] = value
        else:
            break
        
        last_year = last_year + 1
        new_row['gross profit'] = new_row['revenue'] + new_row['cost of revenues']
        new_row['profit from operations'] = new_row['gross profit'] + new_row['selling and marketing expenses'] + new_row['general and administrative expenses']
        new_row_list.append(new_row)
    
    # print(new_row_list)
    # Assuming 'new_row_list' and 'df_fs' are defined earlier in your code
    df = pd.DataFrame(new_row_list)

    # Concatenate df_fs with the new DataFrame. Ensure that the indexes are ignored to avoid duplicate indexes.
    df = pd.concat([df_fs, df], ignore_index=True)

    # Fill NaN values with 0
    df = df.fillna(0)
    
    df['year'] = df['year'].astype('str')
    df_copy = df.rename(columns={df.columns[0]: 'components'})
    
    # Now, transpose the DataFrame
    df_copy = df_copy.transpose().reset_index()

    new_header = df_copy.iloc[0].to_list()

    for i, value in enumerate(new_header):
        new_header[i] = str(value).lower().strip()

    df_copy = df_copy[1:]
    df_copy.columns = new_header
    df_copy.set_index(df_copy.columns[0], inplace=True)
    # Assuming st.write is a method from Streamlit to display the DataFrame
    st.write(df_copy)

def is_conn(df_assumption, predicted_year):
    
    # df_assumption = process_sheet(df_assumption)
    
    df_fs = read_excel_file(file_path='', sheet_name='INCOME STATEMENT')
    df_fs = process_sheet(df_fs)
    
    year_fs = df_fs['year'].to_list()
    last_year = year_fs[-1]
    df_fs_last_year = df_fs[df_fs['year'] == last_year]
    
    new_row_list = []
    
    for no_year in range(predicted_year):
        new_row = {}
        df_assumption_last_year = df_assumption[df_assumption['year'] == last_year]
        df_assumption_current_year = df_assumption[df_assumption['year'] == last_year + 1]
        
        if not df_assumption_last_year.empty and not df_assumption_current_year.empty:
            
            for i in df_fs.columns.to_list():
                if i == 'year':
                    value = last_year + 1
                else:
                    value = 0
                new_row[i] = value
        else:
            break
        
        last_year = last_year + 1
        new_row['gross profit'] = new_row['revenue'] + new_row['cost of revenues']
        new_row['profit from operations'] = new_row['gross profit'] + new_row['selling and marketing expenses'] + new_row['general and administrative expenses']
        new_row_list.append(new_row)
    
    # Assuming 'new_row_list' and 'df_fs' are defined earlier in your code
    df = pd.DataFrame(new_row_list)

    # Concatenate df_fs with the new DataFrame. Ensure that the indexes are ignored to avoid duplicate indexes.
    df = pd.concat([df_fs, df], ignore_index=True)

    # Fill NaN values with 0
    df = df.fillna(0)
    
    df['year'] = df['year'].astype('str')
    df_copy = df.rename(columns={df.columns[0]: 'components'})
    
    # Now, transpose the DataFrame
    df_copy = df_copy.transpose().reset_index()

    new_header = df_copy.iloc[0].to_list()

    for i, value in enumerate(new_header):
        new_header[i] = str(value).lower().strip()

    df_copy = df_copy[1:]
    df_copy.columns = new_header
    df_copy.set_index(df_copy.columns[0], inplace=True)
    # Assuming st.write is a method from Streamlit to display the DataFrame
    st.write(df_copy)

def main():
    
    df_assumption = read_assumption_file()
    st.dataframe(df_assumption)
    if not df_assumption.empty:
        predicted_year = st.text_input('How many years of prediction do you need?')
        
        if predicted_year:
            
            predicted_year = int(predicted_year)
            df_assumption = process_sheet(df_assumption)
            
            ######
            st.divider()
            st.subheader("IS-Crnt")
            is_crnt(df_assumption, predicted_year)
            
            # ######
            # st.divider()
            # st.subheader("IS-Conn")
            # is_conn(df_assumption, predicted_year)