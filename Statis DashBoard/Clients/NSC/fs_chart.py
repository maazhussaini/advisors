import plotly.graph_objs as go
from plotly.subplots import make_subplots
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

filePath = "E:\\MaazProducts\\Fiverr\\Platform\\advisors\\Statis DashBoard\\SourceData\\NSC\\Financial Statement.xlsx"

@st.cache_data
def read_excel_file(file_path, sheet_name=None):
    return pd.read_excel(file_path, sheet_name=sheet_name)

@st.cache_data
def process_sheet(df):
    df = df.drop('Note', axis=1)
    df = df.transpose().reset_index()
    new_header = df.iloc[0]
    df = df[1:]
    df.columns = new_header
    df.reset_index(drop=True, inplace=True)
    df = df.rename(columns={df.columns[0]: 'Year'})
    return df

def displayChart(df: pd.DataFrame, xaxis: str, yaxis: list, title=""):
    # Ensure that yaxis has exactly 2 elements for dual-axis chart
    if len(yaxis) == 2:
        # Create subplot with 1 row and 1 column, and a secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add bar chart for the first y-axis metric
        fig.add_trace(
            go.Bar(x=df[xaxis], y=df[yaxis[0]], name=yaxis[0]),
            secondary_y=False,
        )

        # Add line chart for the second y-axis metric
        fig.add_trace(
            go.Scatter(x=df[xaxis], y=df[yaxis[1]], name=yaxis[1], mode='lines+markers'),
            secondary_y=True,
        )

        # Set titles, axis labels, and layout
        fig.update_layout(
            title_text=title,
        )

        fig.update_xaxes(title_text=xaxis)

        # Set the title for the primary y-axis
        fig.update_yaxes(title_text=yaxis[0], secondary_y=False)
        # Set the title for the secondary y-axis and format as a percentage
        fig.update_yaxes(title_text=yaxis[1], secondary_y=True, tickformat=".0%")

        # To display the figure in Streamlit, uncomment the line below:
        return fig
    else:
        # Create subplot with 1 row and 1 column, and a secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add bar chart for the first y-axis metric
        fig.add_trace(
            go.Bar(x=df[xaxis], y=df[yaxis[0]], name=yaxis[0]),
            secondary_y=False,
        )

        # Add line chart for the second y-axis metric
        fig.add_trace(
            go.Scatter(x=df[xaxis], y=df[yaxis[0]], name=yaxis[0], mode='lines+markers'),
            secondary_y=True,
        )

        # Set titles, axis labels, and layout
        fig.update_layout(
            title_text=title,
        )

        fig.update_xaxes(title_text=xaxis)

        # Set the title for the primary y-axis
        fig.update_yaxes(title_text=yaxis[0], secondary_y=False)
        # Set the title for the secondary y-axis and format as a percentage
        fig.update_yaxes(title_text=yaxis[0], secondary_y=True)

        # To display the figure in Streamlit, uncomment the line below:
        return fig

def customChart(call_count, file_path):
    if 'charts' not in st.session_state:
        st.session_state.charts = []

    sheet_data = read_excel_file(file_path)  # Assuming this function returns a dictionary of DataFrame
    dash_container = st.container()

    for i in range(call_count):
        unique_key = f"unique_key_{call_count}_{i}"

        title_key = unique_key+"title"

        if title_key not in st.session_state:
            st.session_state.title_key = ""

        with dash_container:
            sheet_name_list = list(sheet_data.keys())
            sheet_name_list.insert(0, "")
            sheetName = st.selectbox("Select the Sheet Name", sheet_name_list, key=unique_key + "sheetName")

            if sheetName:
                df = read_excel_file(file_path, sheet_name=sheetName)
                df = process_sheet(df)
                axis = df.columns.to_list()
                axis.insert(0, "")
                
                chart_form = st.form("my-form", clear_on_submit=True, border=False)

                # with chart_form:
                columns = chart_form.columns([3, 3, 3])
                xaxis = columns[0].selectbox("Select x-axis", axis, key=unique_key + "xaxis")
                yaxis = columns[1].multiselect("Select y-axis", axis, max_selections=2,key=unique_key + "yaxis")
                title = columns[2].text_input("Define your title", value=st.session_state.title_key, key=title_key)

                if chart_form.form_submit_button("Generate Chart"):

                    chart = displayChart(df, xaxis, yaxis, title)

                    yaxis.insert(0, xaxis)

                    chartMetaData = {"Chart": chart, "Data": df[yaxis]}
                    st.session_state.charts.append(chartMetaData)

                # Display all charts stored in the session state
                if 'charts' in st.session_state:

                    for i, chartmetadata in enumerate(st.session_state.charts):
                        unique_key = f"unique_key_{call_count}_{i}"
                        tab_chart, tab_data, tab_comments = st.tabs(["Chart", "Data", "Comments"])


                        with tab_chart:
                            if st.plotly_chart(chartmetadata["Chart"], use_container_width=True):
                                st.session_state.title_key = ""
                        
                        with tab_data:
                            st.dataframe(chartmetadata["Data"])
                        
                        with tab_comments:    
                            comments = st.text_area("Write your comments here", key=unique_key)
                            chartmetadata['Comments'] = comments

                            comment_container = st.container()

                            with comment_container:
                                st.write(chartmetadata['Comments'])


# customChart(1, filePath)