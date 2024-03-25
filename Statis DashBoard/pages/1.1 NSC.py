import streamlit as st
from Clients.NSC import fs
from Clients.NSC import fs_chart
from Clients.NSC import gpt, testing

# st.set_page_config(page_title="NSC Financial Statement Data", page_icon="📊")
filePath = "E:\\MaazProducts\\Fiverr\\Platform\\advisors\\Statis DashBoard\\SourceData\\NSC\\Financial Statement.xlsx"


st.title('NSC Financial Statement Data')
# financialState = fs.FinancialStatment()
# financialState.INCOMESTATEMENT_Charts()
# fs_chart.customChart(1, filePath)
gpt.main()
# testing.main()