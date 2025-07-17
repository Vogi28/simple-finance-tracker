import streamlit as st

st.title("Get a year overview of your finances")

uploaded_files = st.file_uploader(
    "Upload your statements", type=["csv"], accept_multiple_files=True
)
