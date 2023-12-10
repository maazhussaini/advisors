import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mysql.connector import errorcode
from mysql.connector import Error
import altair as alt
from dbConnection import database_connection
from charts.charts import barChart, lineChart, scatterChart


st.title('HBE Data')

def custom_chart(conn):
    selected_data = pd.DataFrame()
    custom_query = st.text_area("Write your query here...")
    if custom_query:
        try:
            selection_column = st.columns([2, 2, 2])

            sales_data = pd.read_sql_query(custom_query, conn)

            # First Column Choice        
            selected_column_list = sales_data.columns.to_list()
            selected_column_list.insert(0, '')
            selected_column_x = selection_column[0].selectbox('Select columns for the x-axis', selected_column_list)
            
            
            # Second Column Choice
            if selected_column_x:
                selected_column_list_2 = selected_column_list.copy()
                selected_column_list_2.remove(selected_column_x)
                
            
                selected_column_y = selection_column[1].selectbox('Select columns for the y-axis', selected_column_list_2)
            
            if selected_column_x and selected_column_y:
                selected_data = sales_data[[selected_column_x, selected_column_y]]
                

                chart_option = ['', 'Bar Chart', 'Line Chart', 'Scatter Chart']
                select_chart = selection_column[2].selectbox("Select the Chart", chart_option)

                if select_chart == 'Bar Chart':
                    if barChart(selected_data, selected_column_x, selected_column_y):
                        st.balloons()
                elif select_chart == 'Line Chart':
                    if lineChart(selected_data, selected_column_x, selected_column_y):
                        st.balloons()
                elif select_chart == 'Scatter Chart':
                    if scatterChart(selected_data, selected_column_x, selected_column_y):
                        st.balloons()
                
                if not selected_data.empty:
                    showData = st.checkbox("Show Data")
                    if showData:
                        st.dataframe(selected_data, use_container_width=True)


        except Error as e:
            st.error(e.msg)

conn = database_connection()
st.write('')
custom_chart(conn)


# st.write('')
# years_query = """SELECT distinct(`year`) as 'year' FROM advisors.sales_testing;"""
# years_data = pd.read_sql_query(years_query, conn)
# years_data = years_data['year'].to_list()
# years_data.insert(0, '')
# selected_year = st.selectbox('Select Year', years_data)
# if selected_year:
#     st.write(selected_year)