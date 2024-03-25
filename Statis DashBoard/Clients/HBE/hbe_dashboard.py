import streamlit as st # streamlit package
import numpy as np
import pandas as pd
from millify import millify # shortens values (10_000 ---> 10k)
from streamlit_extras.metric_cards import style_metric_cards # beautify metric card with css
import plotly.graph_objects as go
import altair as alt
from DataBase.dbConnection import database_connection

"""
    Here are some KPIs to consider:

    What are the total sales?
    How much profit was made?
    How many distinct orders did the store receive?
    What are the top 10 products by sales?
    What are the top 10 products by profit?
    What are the sales trends for different product categories over the year?

"""

# Cache the dataset for better performance
# @st.cache_data(ttl=3600)
def metricCard(conn: str):
    
    query = """
    SELECT 
        `year`,
        count(`invoice no.`) as total_order,
        SUM(`selling price`) AS total_selling_price,
        SUM(`item net amount`) AS total_item_net_amount,
        SUM(`item net amount`) - SUM(`selling price`) AS profit,
        ((SUM(`item net amount`) - SUM(`selling price`)) / SUM(`selling price`) * 100) AS profit_percentage
    FROM 
        advisors.sales_testing 
    WHERE
        `year` NOT LIKE "%Q%"
    GROUP BY 
        `year`;
    """

    df = pd.read_sql_query(query, conn)
    # st.dataframe(df)

    # creates the container for page title
    dash_1 = st.container()

    with dash_1:
        st.markdown("<h2 style='text-align: center;'>Sales Dashboard</h2>", unsafe_allow_html=True)
        st.write("")


    # creates the container for metric card
    dash_2 = st.container()

    with dash_2:
        # get kpi metrics
        total_sales = df['total_selling_price'].sum()
        total_profit = df['profit'].sum()
        total_orders = df['total_order'].sum()

        col1, col2, col3 = st.columns(3)
        # create column span
        col1.metric(label="Sales", value= "$"+millify(total_sales, precision=2))
        
        col2.metric(label="Profit", value= "$"+millify(total_profit, precision=2))
        
        col3.metric(label="Orders", value=millify(total_orders, precision=2))
        
        # this is used to style the metric card
        style_metric_cards(border_left_color="#DBF227")

def top10SellingProducts(conn: str):
    
    query = """
            SELECT 
                `item description`, sum(`item quantity`) as total_quantity, sum(`selling price`) as selling_price
            FROM
                advisors.sales_testing
            GROUP BY
                `item description`
            ORDER BY
                selling_price desc, total_quantity asc
            LIMIT 10;
            """
    df = pd.read_sql_query(query, conn)

    # creates the container for charts
    dash_3 = st.container()

    with dash_3:
        col1, col2, col3 = st.columns([1, 12, 1])
        
        with col2:
            chart = alt.Chart(df).mark_bar(opacity=0.9,color="#9FC131").encode(
                x='selling_price:Q',
                y=alt.Y('item description:N', sort='-x'),
                color='total_quantity'
            )
            chart = chart.properties(title="Top 10 Selling Products" )

            
            st.altair_chart(chart,use_container_width=True)

def top10ProfitableProducts(conn: str):
    
    query = """
            SELECT 
                `item description`, sum(`item quantity`) as total_quantity, sum(`item net amount`) as net_amount
            FROM
                advisors.sales_testing
            GROUP BY
                `item description`
            ORDER BY
                net_amount desc, total_quantity asc
            LIMIT 10;
            """
    df = pd.read_sql_query(query, conn)

    # creates the container for charts
    dash_3 = st.container()

    with dash_3:
        col1, col2, col3 = st.columns([1, 12, 1])
        
        with col2:
            chart = alt.Chart(df).mark_bar(opacity=0.9,color="#9FC131").encode(
                x='net_amount:Q',
                y=alt.Y('item description:N', sort='-x'),
                color='total_quantity'
            )
            chart = chart.properties(title="Top 10 Profitable Products" )

            st.altair_chart(chart,use_container_width=True)

def sales_per_branch(conn: str):
    

    query = """
        select
            `branch`, `year`, sum(`selling price`) as selling_price
        FROM
            advisors.sales_testing
        WHERE
            `year` not like "%Q%"
        GROUP BY
            `branch`, `year`;
    """
    df = pd.read_sql_query(query, conn)

    dash_4 = st.container()

    with dash_4:

        custom_colors = {'J01': '#005C53', 'R01': '#9FC131', 'D01': '#042940'}


        chart = alt.Chart(df).mark_bar(point=True).encode(
            y=alt.Y('selling_price:Q', stack='zero', axis=alt.Axis(format='~s') ),
            x=alt.X('year:N'),
            color='branch'
            # color=alt.Color('branch:N', scale=alt.Scale(domain=list(custom_colors.keys()), range=list(custom_colors.values())))
        )

        # text = alt.Chart(df).mark_text(dx=-15, dy=30, color='white').encode(
        #      y=alt.Y('selling_price:Q', stack='zero', axis=alt.Axis(format='~s') ),
        #     x=alt.X('year:N'),
        #     detail='branch:N',
        #     text=alt.Text('selling_price:Q', format='~s')
        #   )

        # chart = bars + text

        chart = chart.properties(title="Sales trends for Branch Categories over the years" )

        st.altair_chart(chart,use_container_width=True)

def sales_per_salesman(year: int, conn: str):
    

    query = f"""
        select 
            `sales man code`, count(`invoice no.`) as 'SalesPerSalesman', sum(`selling price`) as 'Selling Price',
            GROUP_CONCAT(`item description` SEPARATOR ', ') AS 'Item Name'
        FROM advisors.sales_testing
        WHERE `year` = {year} and `invoice type` = "SALES" and `invoice no.` not in (SELECT `return ref.inv.#` FROM advisors.sales_testing WHERE `invoice type` = "RETURN" GROUP BY `return ref.inv.#`)
        GROUP BY `sales man code`;
    """

    df = pd.read_sql_query(query, conn)

    dash = st.container()

    with dash:

        chart_tab, data_tab = st.tabs(["Chart", "Data"])
        with chart_tab:
            chart = alt.Chart(df).mark_bar(opacity=0.9, color="#9FC131").encode(
                x='sales man code:N',  # 'sales man code' is treated as nominal
                y=alt.Y('Selling Price:Q', sort='-y'),  # Sort by 'Selling Price' in descending order
                color='SalesPerSalesman:Q'  # Assuming this is a quantitative measure
            )

            chart = chart.properties(
                title=f"Sales Per Salesman in {year}",
                width=600  # You can adjust the width as needed
            )
            st.altair_chart(chart, use_container_width=True)

        with data_tab:
            st.dataframe(df)

def item_returns(year: int, conn: str):

    query = f"""
        SELECT
            GROUP_CONCAT(`item description` SEPARATOR ', ') AS 'Item Name', `sales man code`, sum(`item net amount`) as net_amount
        FROM advisors.sales_testing
        WHERE `invoice type` = 'RETURN' and `year` = {year}
        GROUP BY `sales man code`
        ORDER BY net_amount, `sales man code`;
    """

    df = pd.read_sql_query(query, conn)

    dash = st.container()

    with dash:

        chart_tab, data_tab = st.tabs(["Chart", "Data"])
        
        with chart_tab:
            chart = alt.Chart(df).mark_rect(point=True).encode(
                        x=alt.X('sales man code:N', stack='zero', axis=alt.Axis(format='~s')),  # 'sales man code' is treated as nominal
                        y=alt.Y('net_amount:Q', sort='-y'),  # Sort by 'Selling Price' in descending order
                        color='net_amount:Q'  # Assuming this is a quantitative measure
                    )
            st.altair_chart(chart, use_container_width=True)
        
        with data_tab:
            st.dataframe(df)

def main(year: int):
    conn = database_connection()
    metricCard(conn)
    top10SellingProducts(conn)
    top10ProfitableProducts(conn)
    sales_per_branch(conn)
    sales_per_salesman(year=year, conn=conn)
    item_returns(year=year, conn=conn)