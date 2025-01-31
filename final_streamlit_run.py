import streamlit as st
from streamlit_run import main_page
from rag_streamlit import rag_streamlit
from streamlit_option_menu import option_menu

st.set_page_config(page_title="LMS Chatbot", layout="wide")

with st.sidebar:
    selected_page = option_menu(
        "SELECT PAGE",
        ("LMS DATA RETRIEVER","MULTI MODEL RAG"),
        icons=["house","track-list"]
    )

if selected_page == "LMS DATA RETRIEVER":
    main_page()
if selected_page == "MULTI MODEL RAG":
    rag_streamlit()