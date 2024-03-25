import streamlit as st
import pandas as pd


def barChart(selected_data: pd.DataFrame, selected_column_x: str, selected_column_y: str, colored="#ffaa0088"):
    return st.bar_chart(selected_data, x=selected_column_x, y=selected_column_y, color=colored, use_container_width=True)

def lineChart(selected_data: pd.DataFrame, selected_column_x: str, selected_column_y: str):
    return st.line_chart(selected_data, x=selected_column_x, y=selected_column_y, use_container_width=True)

def scatterChart(selected_data: pd.DataFrame, selected_column_x: str, selected_column_y: str, colored="#ffaa0088"):
    return st.scatter_chart(selected_data, x=selected_column_x, y=selected_column_y, color=colored, use_container_width=True)