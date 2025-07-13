from datetime import datetime, timedelta
import json
import os
import pandas as pd
from Modules.SessionStateHandler import SessionStateHandler as ssh
import streamlit as st
import time


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


def save_file_in_session(uploaded_file):
    if uploaded_file.name not in st.session_state.temp_files:
        st.session_state.temp_files[uploaded_file.name] = uploaded_file
        st.rerun()


def sidebar_file_selector():
    selected_file = None
    if st.session_state.temp_files != {}:
        # TODO find a solution to display name of the file
        selected_file = st.sidebar.selectbox(
            label="Temporary files",
            options=list(st.session_state.temp_files.values()),
            index=None,
            placeholder="",
        )

    return selected_file


# Only for local saving
def clear_old_files(TRANSACTIONS_PATH: str, n: int):
    if os.path.exists(TRANSACTIONS_PATH):
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

    if "temp_files" not in st.session_state:
        st.session_state.temp_files = {}

    if os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE, "r") as f:
            st.session_state.categories = json.load(f)
        session_handler = ssh(st.session_state.categories)
    else:
        with open(CATEGORIES_FILE, "x") as f:
            f.write('{"Uncategorized": []}')

        with open(CATEGORIES_FILE, "r") as f:
            st.session_state.categories = json.load(f)
        session_handler = ssh(st.session_state.categories)

    return session_handler
