import streamlit as st
from Clients.HBE import hbe_dashboard

st.set_page_config(page_title="HBE Data", page_icon="📊")
hbe_dashboard.main(2018)