import streamlit as st
from Clients.NSC import NSC
from Clients import HBE


client_selection = st.selectbox("Select the Client",["","NSC", "HBE"], placeholder="Choose an option")

if client_selection == "NSC":
    ## For NSC Client
    NSC.NSC_insights()

if client_selection == "HBE":
    pass
