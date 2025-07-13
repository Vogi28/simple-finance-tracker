from datetime import datetime, timedelta
import json
import os
import pandas as pd
import streamlit as st
from Modules.SessionStateHandler import SessionStateHandler as ssh
import time
from Modules.TransactionHandler import TransactionHandler as th


@st.cache_data
def define_start_end_date(df: pd.DataFrame):
    start_date = None
    end_date = None
    for idx, row in df.iterrows():
        date = datetime.strptime(
            row["Transaction date"].lower().strip(), "%d.%m.%Y"
        ).date()
        if start_date is None or date < start_date:
            start_date = date

        if end_date is None or date > end_date:
            end_date = date

    return [start_date, end_date]


def save_file(uploaded_file, path: str):
    path = path + uploaded_file.name
    if not os.path.exists(path):
        f = open(path, "wb")
        f.write(uploaded_file.getvalue())
        st.rerun()


def sidebar_file_selector(folder_path: str):
    files = os.listdir(folder_path)
    selected_file = st.sidebar.selectbox(
        "Previous files", files, index=None, placeholder=""
    )

    if selected_file is not None:
        selected_file = folder_path + selected_file

    return selected_file


def clear_old_files(TRANSACTIONS_PATH: str, n: int):
    files = os.listdir(TRANSACTIONS_PATH)
    if files != []:
        for file in files:
            path = TRANSACTIONS_PATH + file
            time_of_creation = time.ctime(os.path.getctime(path))
            dateObj = datetime.strptime(time_of_creation, "%a %b %d %H:%M:%S %Y")

            if (datetime.now() - dateObj) > timedelta(days=n):
                os.remove(path)


def add_new_category(
    new_category: str, add_button: bool, session_handler: ssh, categories_file: str
):
    if add_button and new_category:
        if new_category not in st.session_state.categories:
            session_handler.categories[new_category] = []
            session_handler.save_categories(categories_file)
            st.success(f"New category {new_category} added")
            time.sleep(1)
            st.rerun()


def initialize_state(CATEGORIES_FILE) -> ssh:
    if "categories" not in st.session_state:
        st.session_state.categories = {"Uncategorized": []}

    if os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE, "r") as f:
            st.session_state.categories = json.load(f)
        session_handler = ssh(st.session_state.categories)

    return session_handler
