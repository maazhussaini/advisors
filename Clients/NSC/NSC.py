import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mysql.connector import errorcode
from mysql.connector import Error
import altair as alt
# from ...DataBase import dbConnection as db
from DataBase import dbConnection as db
import seaborn as sns
import plotly.express as px

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


# Streamlit app layout
def NSC_insights():
    st.title('Financial Dashboard')
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
