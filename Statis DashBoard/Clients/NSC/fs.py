import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
import plotly.express as px

import plotly.graph_objects as go

class FinancialStatment:
    def __init__(self):
        self.df = pd.read_excel("E:\\MaazProducts\\Fiverr\\Platform\\advisors\\Statis DashBoard\\SourceData\\NSC\\Financial Statement.xlsx", None)
        # df_BALANCESHEET = pd.read_excel("E:\\MaazProducts\\Fiverr\\Platform\\advisors\\Statis DashBoard\\SourceData\\NSC\\Financial Statement.xlsx", sheet_name="BALANCESHEET")
        self.df_INCOMESTATEMENT = pd.read_excel("E:\\MaazProducts\\Fiverr\\Platform\\advisors\\Statis DashBoard\\SourceData\\NSC\\Financial Statement.xlsx", sheet_name="INCOME STATEMENT")
        # df_CASHFLOWSTATEMENT = pd.read_excel("../../SourceData/NSC/Financial Statement.xlsx", sheet_name="CASHFLOW STATEMENT")
        # df_Supplemental = pd.read_excel("../../SourceData/NSC/Financial Statement.xlsx", sheet_name="Supp. schd. of non-cash info.")

    # Streamlit app
    def INCOMESTATEMENT_Charts(self):
        st.title('Financial Analysis Dashboard')

        # Revenue Analysis
        st.header("Revenue Analysis")
        
        # Remove column 'Note'
        self.df_INCOMESTATEMENT.drop('Note', axis=1, inplace=True)

        self.df_INCOMESTATEMENT = self.df_INCOMESTATEMENT.transpose().reset_index()
        new_header = self.df_INCOMESTATEMENT.iloc[0]

        # Take the data less the header row
        self.df_INCOMESTATEMENT = self.df_INCOMESTATEMENT[1:]

        # Set the new header
        self.df_INCOMESTATEMENT.columns = new_header
        self.df_INCOMESTATEMENT.reset_index(drop=True, inplace=True)
        self.df_INCOMESTATEMENT.rename(columns={"INCOME STATEMENT": "Year"}, inplace=True)

        revenue_df = self.df_INCOMESTATEMENT

        # Plot with Plotly for interactivity
        revenue_chart = px.bar(revenue_df, x='Year', y='Revenues', color='Revenues',
                            labels={'Amount': 'Revenues'}, title='Annual Revenues',
                            hover_data=['Revenues'])
        revenue_chart.update_layout(yaxis_title="Revenues", xaxis_title="Year")
        st.plotly_chart(revenue_chart, use_container_width=True)

        ####

        # Gross Profit Analysis
        st.header("Gross Profit Analysis")
        # gross_profit_df = revenue_df[revenue_df['INCOME STATEMENT'] == 'Gross profit']

        # Plot with Plotly
        gross_profit_chart = px.bar(revenue_df, x='Year', y='Gross profit',
                                    title="Gross Profit Over the Years")
        st.plotly_chart(gross_profit_chart, use_container_width=True)

        ####
        # Selling and Marketing Expenses Analysis
        st.header("Selling and Marketing Expenses Analysis")

        # Plot with Plotly for interactivity
        selling_marketing_chart = px.bar(revenue_df, x='Year', y='Selling and marketing', color='Selling and marketing',
                            labels={'Amount': 'Selling and marketing'}, title='Annual Selling and marketing',
                            hover_data=['Selling and marketing'])
        selling_marketing_chart.update_layout(yaxis_title="Selling and marketing", xaxis_title="Year")
        st.plotly_chart(selling_marketing_chart, use_container_width=True)

    def customChart(self, call_count):
        
        dash_container = "container"+str(call_count)
        dash_container = st.container()
        for i in range(call_count):
            unique_key = f"selectbox_{call_count}_{i}"
            with dash_container:
                
                sheet_name_list = list(self.df.keys())
                sheet_name_list.insert(0, "")
                self.df = pd.read_excel("E:\\MaazProducts\\Fiverr\\Platform\\advisors\\Statis DashBoard\\SourceData\\NSC\\Financial Statement.xlsx", None)
                sheetName = st.selectbox("Select the Sheet Name", sheet_name_list, key=unique_key+"sheetName")
                
                if sheetName:
                    df = pd.read_excel("E:\\MaazProducts\\Fiverr\\Platform\\advisors\\Statis DashBoard\\SourceData\\NSC\\Financial Statement.xlsx", sheet_name=sheetName)
                    
                    # Remove column 'Note'
                    df.drop('Note', axis=1, inplace=True)

                    df = df.transpose().reset_index()
                    new_header = df.iloc[0]

                    # Take the data less the header row
                    df = df[1:]

                    # Set the new header
                    df.columns = new_header
                    df.reset_index(drop=True, inplace=True)
                    # df.rename(columns={sheetName: "Year"}, inplace=True)
                    df = df.rename(columns={df.columns[0]: 'Year'})

                    columns = st.columns([3, 3, 3])
                    xaxis = columns[0].selectbox("Select x-axis", df.columns.to_list(), key=unique_key+"xaxis")
                    yaxis = columns[1].selectbox("Select y-axis", df.columns.to_list(), key=unique_key+"yaxis", on_change=FinancialStatment.customChart(self, 0))
                    title = columns[2].text_input("Define your title", key=unique_key+"title")

                    if xaxis and yaxis:
                        # Plot with Plotly for interactivity
                        revenue_chart = px.bar(df, x=xaxis, y=yaxis,
                                            title=title,
                                            hover_data=[yaxis])
                        revenue_chart.update_layout(yaxis_title=yaxis, xaxis_title=xaxis)
                        st.plotly_chart(revenue_chart, use_container_width=True)