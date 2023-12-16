import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mysql.connector import errorcode
from mysql.connector import Error
import altair as alt
from dbConnection import database_connection
from charts.charts import barChart, lineChart, scatterChart

def testing_chart(conn: str):

    year_query = f"""
                SELECT distinct(`year`) FROM advisors.sales_testing;
            """
    years = pd.read_sql_query(year_query, conn)

    year_list = years.year.to_list()

    selected_year = st.selectbox("Select the year", year_list)
    
    query = f"""
                SELECT * FROM advisors.sales_testing where `year` = {selected_year}
            """

    sales_data = pd.read_sql_query(query, conn)

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
                    column_selection_for_condition = [selected_column_x, selected_column_y]
                    column_name = condition_column[0].selectbox("Select the column for the condition", column_selection_for_condition)

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
            st.error(e.msg)


conn = database_connection()
st.write('')
# testing_chart(conn)
