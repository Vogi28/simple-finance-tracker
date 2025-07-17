import streamlit as st

home_page = st.Page("home_page.py", title="Home", icon=":material/home:", default=True)
compare_page = st.Page(
    "compare.py", title="Compare finance", icon=":material/difference:"
)
graph_page = st.Page(
    "graph_page.py", title="Year overview", icon=":material/analytics:"
)

pg = st.navigation([home_page, compare_page, graph_page], position="top")
pg.run()
