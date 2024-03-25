import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mysql.connector import errorcode
from mysql.connector import Error
import altair as alt
from DataBase import dbConnection as db
import seaborn as sns
import plotly.express as px

import requests
from requests_toolbelt import MultipartEncoder
import json


# Function to load data
@st.cache_data
def load_data():
    conn = db.database_connection()
    query = f"""
                SELECT * FROM advisors.nsc_tb;
            """
    data = pd.read_sql_query(query, conn)
    return data

# Load your data
data = load_data()

def chart_with_gpt():
    # Data Preparation for In-depth Analysis
    # First, we'll clean and prepare the data for a comprehensive analysis.

    # Step 1: Handling the 'Year' column by separating the year and quarter
    # Extracting year and quarter into separate columns
    data['Extracted_Year'] = data['Year'].apply(lambda x: int(str(x)[:4]) if isinstance(x, str) else x)
    data['Quarter'] = data['Year'].apply(lambda x: str(x)[5:] if isinstance(x, str) and 'Q' in str(x) else None)

    # Step 2: Grouping data for various analyses
    # Group by Year for yearly analysis
    yearly_grouped = data.groupby('Extracted_Year').agg({'Ending Balance': ['sum', 'mean', 'median', 'std']})
    yearly_grouped.columns = ['Total Balance', 'Average Balance', 'Median Balance', 'Std Dev Balance']

    # Group by Level 1 categories (e.g., Assets, Liabilities)
    category_grouped = data.groupby(['Extracted_Year', 'L1']).agg({'Ending Balance': 'sum'}).reset_index()

    # Group by Quarter
    quarterly_grouped = data[data['Quarter'].notnull()].groupby(['Extracted_Year', 'Quarter']).agg({'Ending Balance': 'sum'}).reset_index()

    # Preparing data for visualizations
    # Visualization 1: Yearly Total Balances
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=yearly_grouped, x=yearly_grouped.index, y='Total Balance')
    plt.title('Yearly Total Balances')
    plt.xlabel('Year')
    plt.ylabel('Total Balance')
    plt.xticks(yearly_grouped.index)
    plt.grid(True)
    # st.pyplot(plt)
    st.pyplot(plt)

    # Visualization 2: Yearly Average, Median, and Std Dev of Balances
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=yearly_grouped, x=yearly_grouped.index, y='Average Balance', label='Average Balance')
    sns.lineplot(data=yearly_grouped, x=yearly_grouped.index, y='Median Balance', label='Median Balance')
    sns.lineplot(data=yearly_grouped, x=yearly_grouped.index, y='Std Dev Balance', label='Std Dev Balance')
    plt.title('Yearly Average, Median, and Std Dev of Balances')
    plt.xlabel('Year')
    plt.ylabel('Balance')
    plt.xticks(yearly_grouped.index)
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)

    # Visualization 3: Category-wise Total Balances per Year
    plt.figure(figsize=(12, 6))
    sns.barplot(x='Extracted_Year', y='Ending Balance', hue='L1', data=category_grouped)
    plt.title('Category-wise Total Balances per Year')
    plt.xlabel('Year')
    plt.ylabel('Total Balance')
    st.pyplot(plt)

    # Visualization 4: Quarterly Total Balances (for years with quarters)
    plt.figure(figsize=(12, 6))
    sns.barplot(x='Extracted_Year', y='Ending Balance', hue='Quarter', data=quarterly_grouped)
    plt.title('Quarterly Total Balances')
    plt.xlabel('Year')
    plt.ylabel('Total Balance')
    st.pyplot(plt)

import requests

def download_file(url, local_filename):
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()  # Raises a HTTPError if the response status code is 4XX/5XX
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
        print(f"File successfully downloaded and saved as {local_filename}")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
    except requests.exceptions.RequestException as e:
        # For handling exceptions that aren't under HTTPError
        print(f"Error downloading the file: {e}")


def convert_pdf_files_to_excel():
    pdf_file_path = st.file_uploader("Upload only .pdf file.", type="pdf", accept_multiple_files=False)
    if pdf_file_path:
        st.write(pdf_file_path)

        excel_endpoint_url = 'https://api.pdfrest.com/excel'
 
        # The /excel endpoint can take a single PDF file or id as input.
        # This sample demonstrates converting a PDF to an Excel document.
        mp_encoder_excel = MultipartEncoder(
            fields={
                'file': ('NSC Fnst Dec 2018 (English).pdf', open("E:/MaazProducts/Fiverr/Platform/Source Data Files/IPD - NSC/Source Data Files - AFS PDF/NSC Fnst Dec 2018 (English).pdf", 'rb'), 'application/pdf'),
                'output' : 'example_excel_out',
            }
        )
        
        # Let's set the headers that the Excel endpoint expects.
        # Since MultipartEncoder is used, the 'Content-Type' header gets set to 'multipart/form-data' via the content_type attribute below.
        headers = {
            'Accept': 'application/json',
            'Content-Type': mp_encoder_excel.content_type,
            'Api-Key': '37be3a1c-605e-4bac-9be7-364205d48cb6'
        }
        
        st.write("Sending POST request to excel endpoint...")
        response = requests.post(excel_endpoint_url, data=mp_encoder_excel, headers=headers)
        
        st.write("Response status code: " + str(response.status_code))
        
        if response.ok:
            response_json = response.json()
            
            # response_json = json.dumps(response_json, indent = 2)
            st.write(response_json)
            st.write(type(response_json))
            # Example usage
            url = response_json['outputUrl']  # Replace with the actual URL
            local_filename = 'localfile.xlsx'  # Replace with your desired local filename
            download_file(url, local_filename)
            
            
        else:
            st.write(response.text)


# Streamlit app layout
def NSC_insights():
    st.title('Financial Dashboard')
    
    convert_pdf_files_to_excel()
    
    chart_with_gpt()
    # Sidebar filters
    st.sidebar.header('Filters')
    year = st.sidebar.multiselect('Select Year', sorted(data['Year'].unique()))
    account = st.sidebar.multiselect('Select Description', sorted(data['Description'].unique()))

    # Filter data based on selection
    filtered_data = data
    if year:
        filtered_data = filtered_data[filtered_data['Year'].isin(year)]
    if account:
        filtered_data = filtered_data[filtered_data['Description'].isin(account)]

    # Time Series Analysis
    st.subheader('Time Series Analysis')
    timeSeries_charts, timeSeries_data = st.tabs(["📈 Chart", "🗃 Data"])

    with timeSeries_charts:
        if not year:
            st.write('Please select at least one year.')
        else:
            time_series_plot(filtered_data)
    
    with timeSeries_data:
        if not year:
            st.write('Please select at least one year.')
        else:
            st.dataframe(filtered_data)

    # Visualizations for Different Levels
    st.subheader('L1 Category Breakdown')
    categorical_plot(filtered_data, 'L1')
    
    st.subheader('L2 Category Breakdown')
    categorical_plot(filtered_data, 'L2', chart_type='pie')

    st.subheader('L3 Category Breakdown')
    categorical_plot(filtered_data, 'L3', chart_type='treemap')

    # Display Data Table
    st.subheader('Account-Level Details')
    st.dataframe(filtered_data)

    # Summary Statistics
    st.subheader('Summary Statistics')
    st.write(filtered_data.describe())

# Function to plot time series with Plotly
def time_series_plot(data):
    agg_data = data.groupby(['Year', 'Description']).agg({'Ending Balance': 'sum'}).reset_index()
    fig = px.line(agg_data, x='Year', y='Ending Balance', color='Description')
    st.plotly_chart(fig, use_container_width=True)

# Function to plot categorical breakdown with different chart types
def categorical_plot(data, category, chart_type='bar'):
    agg_data = data.groupby(category).agg({'Ending Balance': 'sum'}).reset_index()
    
    if chart_type == 'bar':
        chart = alt.Chart(agg_data).mark_bar().encode(
            x=category,
            y='Ending Balance',
            color=category
        )
    elif chart_type == 'pie':
        st.dataframe(agg_data)
        fig = px.pie(agg_data, names=category, values='Ending Balance')
        st.plotly_chart(fig, use_container_width=True)
        return
    elif chart_type == 'treemap':
        fig = px.treemap(agg_data, path=[category], values='Ending Balance')
        st.plotly_chart(fig, use_container_width=True)
        return

    st.altair_chart(chart, use_container_width=True)
