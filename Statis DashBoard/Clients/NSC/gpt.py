import plotly.graph_objs as go
from plotly.subplots import make_subplots
import streamlit as st
import pandas as pd
import plotly.express as px

# filePathfs = "E:/MaazProducts/Fiverr/Platform/advisors/Statis DashBoard/SourceData/NSC/Financial Statement.xlsx"

@st.cache_data
def read_excel_file(file_path, sheet_name=None):
    file_path = "E:/MaazProducts/Fiverr/Platform/advisors/Statis DashBoard/SourceData/NSC/Financial Statement - Copy.xlsx"
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    try:
        df = df.drop('Note', axis=1)
    except:
        pass
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
    
    return df_assumption

def is_crnt():
    
    df_assumption = read_assumption_file()
    
    df_assumption = st.data_editor(df_assumption, hide_index=True)
    df_assumption = df_assumption[df_assumption['Select'] == True]
    
    if not df_assumption.empty:
        predicted_year = st.text_input('How many years of prediction do you need?')
        
        if predicted_year:
            st.divider()
            st.subheader("IS-Crnt")
            
    
    predicted_year = int(predicted_year)
    df_assumption = process_sheet(df_assumption)
    
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
    
    return df, df_copy

def is_conn(df_assumption, predicted_year):
    
    df_assumption = process_sheet(df_assumption)
    
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


def workingCapital(is_crnt_df):
    workingCapital_df = read_excel_file(file_path='', sheet_name='WC')
    is_crnt_df = is_crnt_df.reset_index()
    
    last_year = workingCapital_df.columns.to_list()[-1]
    
    st.dataframe(workingCapital_df, hide_index=True)
    # st.dataframe(is_crnt_df, hide_index=True)
    
    revenue = is_crnt_df.loc[:0, : str(last_year)]
    st.dataframe(revenue, hide_index=True)
    
    # key_indicators_df = pd.DataFrame()
    key_indicators_list = []
    key_indicators_dict = {}
    flag = False
    
    workingCapital_dict = workingCapital_df.to_dict(orient='records')
    checklist = revenue.columns.to_list()
    checklist = checklist[1:]
    
    for i in workingCapital_dict:
        flag = False
        key_indicators_dict = {}
        
        for j, k in i.items():
            
            if i['Notes'] == "Sales":
                key_indicators_dict[j] = k
                
                if str(j) in checklist:
                    try:
                        value = int(k) / int(revenue[str(j)].to_list()[0]) * 365
                        key_indicators_dict[j] = int(value)
                    except Exception as e:
                        pass
            
            elif i['Notes'] == "COGS":
                key_indicators_dict[j] = k
                
                if str(j) in checklist:
                    try:
                        value = int(k) / (-1 * int(revenue[str(j)].to_list()[0])) * 365
                        key_indicators_dict[j] = int(value)
                    except Exception as e:
                        pass
            else:
                key_indicators_dict[j] = k
                
                if str(j) in checklist:
                    try:
                        value = 0
                        key_indicators_dict[j] = int(value)
                    except Exception as e:
                        pass

        key_indicators_list.append(key_indicators_dict)
    
    key_indicators_df = pd.DataFrame(key_indicators_list)
    st.dataframe(key_indicators_df)
    

def balanceSheet():
    df = read_excel_file(file_path='', sheet_name='BALANCESHEET')
    st.dataframe(df, hide_index=True)

def main():
    
    is_crnt_df, is_crnt_df_copy = is_crnt()
    
    workingCapital(is_crnt_df_copy)
    
    # balanceSheet()
    # is_crnt_df = pd.DataFrame()
    # df_assumption = pd.DataFrame()
    
    # df_assumption = read_assumption_file()
    
    # if not df_assumption.empty:
    #     predicted_year = st.text_input('How many years of prediction do you need?')
        
    #     if predicted_year:
    #         st.divider()
    #         st.subheader("IS-Crnt")
            
    #         predicted_year = int(predicted_year)
            
    #         # is_crnt_df, is_crnt_df_copy = is_crnt(df_assumption, predicted_year)
    #         is_crnt(df_assumption, predicted_year)
        
            # if not is_crnt_df.empty:
            #     st.divider()
            #     st.subheader("IS-Con")
            #     scenario = st.selectbox("Select Scenario: ", [1, 2, 3])
        
            #     if scenario == 1 or scenario == 2:
            #         st.dataframe(is_crnt_df_copy)
            #     else:
            #         is_conn(df_assumption, predicted_year)