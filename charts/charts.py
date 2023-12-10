import streamlit as st
import pandas as pd


def barChart(selected_data, selected_column_x, selected_column_y):
    st.write('')
    st.write('')
    st.write('')
    return st.bar_chart(selected_data, x=selected_column_x, y=selected_column_y, color=selected_column_x, use_container_width=True)

def lineChart(selected_data, selected_column_x, selected_column_y):
    st.write('')
    st.write('')
    st.write('')

    return st.line_chart(selected_data, x=selected_column_x, y=selected_column_y, use_container_width=True)

def scatterChart(selected_data, selected_column_x, selected_column_y):
    st.write('')
    st.write('')
    st.write('')
    return st.scatter_chart(selected_data, x=selected_column_x, y=selected_column_y, color=selected_column_y, use_container_width=True)