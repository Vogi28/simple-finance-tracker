import streamlit as st

home_page = st.Page("home_page.py", title="Home", icon=":material/home:", default=True)
compare_page = st.Page(
    "compare.py", title="Compare finance", icon=":material/difference:"
)

pg = st.navigation([home_page, compare_page], position="top")
pg.run()
