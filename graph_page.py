import calendar
import os

import plotly.express as px
import streamlit as st

import Modules.method_helper as method_helper
from Modules.TransactionHandler import TransactionHandler as th

CATEGORIES_FILE = os.getcwd() + "/categories.json"

session_handler = method_helper.initialize_state(CATEGORIES_FILE)

tr_handler = th()

st.title("Get a year overview of your finances")

uploaded_files = st.file_uploader(
    "Upload your statements", type=["csv"], accept_multiple_files=True
)

i = 1
if uploaded_files is not None:
    dfs = {}
    for uploaded_file in uploaded_files:
        df = tr_handler.load_transactions(uploaded_file, session_handler)
        method_helper.load_new_categories_with_keywords(df, session_handler, CATEGORIES_FILE)
        tr_handler.categorize_transactions(df, session_handler)

        [start_date, end_date] = method_helper.define_start_end_date(df)
        df_debits = df[df["Debit/Credit"] == "Debit"].copy()

        category_totals = df_debits.groupby("Category")["Amount"].sum().reset_index()
        category_totals = category_totals.sort_values("Amount", ascending=False)

        dfs[end_date.month] = category_totals

    dfs_sorted = {k: v for k, v in sorted(dfs.items())}

    for k, df_sorted in dfs_sorted.items():
        fig = px.pie(
            df_sorted,
            values="Amount",
            names="Category",
            color_discrete_sequence=px.colors.sequential.RdBu,
        )

        st.subheader(calendar.month_name[k])
        st.plotly_chart(fig)
