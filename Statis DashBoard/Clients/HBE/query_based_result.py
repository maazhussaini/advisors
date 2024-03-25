import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mysql.connector import errorcode
from mysql.connector import Error
import altair as alt
from DataBase.dbConnection import database_connection
from charts.charts import barChart, lineChart, scatterChart

def fetchingData() -> pd.DataFrame:
    try:
        conn = database_connection()
    except:
        st.warning("DataBase Couldn't connect")
    if conn:
        sales_data = pd.DataFrame()
        custom_query = st.text_area("Write your query here...")
        if custom_query:
            try:
                sales_data = pd.read_sql_query(custom_query, conn)
                st.write(sales_data)
                # custom_chart(sales_data)
                three_column_query(sales_data)
                # st.write(sales_data)
                # return sales_data
            except Error as e:
                st.error(e.msg)

def custom_chart(sales_data: pd.DataFrame):
    if not sales_data.empty:
        try:

            with st.container():
                selection_column = st.columns([2, 2, 2])

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

                    condition_column = st.columns([2, 2, 2])
                    column_name = condition_column[0].selectbox("Select the column for the condition", selected_column_list)

                    operator_column = condition_column[1].selectbox("Select the operator", ["", "<", "==", ">"])

                    value_column = condition_column[2].text_input("Write the value")

            
            if selected_column_x and selected_column_y:
                chart_tab, data_tab = st.tabs(["📈 Chart", "🗃 Data"])

                with chart_tab:
                    chart_tab.subheader(select_chart)

                    if select_chart == 'Bar Chart':
                        if barChart(selected_data, selected_column_x, selected_column_y):
                            st.balloons()
                    elif select_chart == 'Line Chart':
                        if lineChart(selected_data, selected_column_x, selected_column_y):
                            st.balloons()
                    elif select_chart == 'Scatter Chart':
                        if scatterChart(selected_data, selected_column_x, selected_column_y):
                            st.balloons()
                
                with data_tab:
                    data_tab.subheader("Data")
                    
                    if column_name and operator_column and value_column:

                        try:
                            value_column = float(value_column)
                        except:
                            value_column = str(value_column)
                        
                        if operator_column == "<":
                            selected_data = selected_data[selected_data[column_name] < value_column]
                        if operator_column == "==":
                            selected_data = selected_data[selected_data[column_name] == value_column]
                        if operator_column == ">":
                            selected_data = selected_data[selected_data[column_name] > value_column]
                        
                        st.dataframe(selected_data, use_container_width=True)
                    else:
                        st.dataframe(selected_data, use_container_width=True)
                    
                    # if not selected_data.empty:
                    #     showData = st.checkbox("Show Data", value=True)
                    #     if showData:
                    #         st.dataframe(selected_data, use_container_width=True)


        except Error as e:
            st.error(e.msg)

def three_column_query(sales_data: pd.DataFrame):
    if not sales_data.empty:
        try:

            with st.container():
                selection_column = st.columns([2, 2, 2])

                # First Column Choice        
                selected_column_list = sales_data.columns.to_list()
                selected_column_list.insert(0, '')
                selected_column_x = selection_column[0].selectbox('Select column for x-axis', selected_column_list)
                
                # Second Column Choice
                if selected_column_x:
                    selected_column_list_2 = selected_column_list.copy()
                    selected_column_list_2.remove(selected_column_x)

                    selected_column_y = selection_column[1].selectbox('Select column for y-axis', selected_column_list_2)

                if selected_column_x and selected_column_y:

                    selected_data = sales_data[[selected_column_x, selected_column_y]]

                    chart_option = ['', 'Bar Chart', 'Line Chart', 'Scatter Chart']
                    select_chart = selection_column[2].selectbox("Select the Chart", chart_option)

                    condition_column = st.columns([2, 2, 2])
                    column_name = condition_column[0].selectbox("Select the column for the condition", selected_column_list)

                    operator_column = condition_column[1].selectbox("Select the operator", ["", "<", "==", ">"])

                    value_column = condition_column[2].text_input("Write the value")

            
            if selected_column_x and selected_column_y:
                chart_tab, data_tab = st.tabs(["📈 Chart", "🗃 Data"])

                with chart_tab:
                    chart_tab.subheader(select_chart)

                    if select_chart == 'Bar Chart':
                        barChart(selected_data, selected_column_x, selected_column_y)
                        st.balloons()
                        
                    elif select_chart == 'Line Chart':
                        if lineChart(selected_data, selected_column_x, selected_column_y):
                            st.balloons()
                    elif select_chart == 'Scatter Chart':
                        scatterChart(selected_data, selected_column_x, selected_column_y)
                        st.balloons()
                
                with data_tab:
                    data_tab.subheader("Data")
                    
                    if column_name and operator_column and value_column:

                        try:
                            value_column = float(value_column)
                        except:
                            value_column = str(value_column)
                        
                        if operator_column == "<":
                            selected_data = selected_data[selected_data[column_name] < value_column]
                        if operator_column == "==":
                            selected_data = selected_data[selected_data[column_name] == value_column]
                        if operator_column == ">":
                            selected_data = selected_data[selected_data[column_name] > value_column]
                        
                        st.dataframe(selected_data, use_container_width=True)
                    else:
                        st.dataframe(selected_data, use_container_width=True)


        except Error as e:
            print(e.msg)
