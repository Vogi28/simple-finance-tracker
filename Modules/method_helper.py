import json
import os
import time
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from Modules.SessionStateHandler import SessionStateHandler as ssh

category_column: str|None = None

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
    new_category: str, add_button: bool, session_handler: ssh, categories_file: str, rerun: bool = True
):
    if add_button and new_category:
        if new_category not in st.session_state.categories:
            session_handler.categories[new_category] = []
            session_handler.save_categories(categories_file)
            st.success(f"New category {new_category} added")
            time.sleep(1)

            if rerun:
                st.rerun()


def initialize_state(path_categories_file) -> ssh:
    if "categories" not in st.session_state:
        st.session_state.categories = {"Uncategorized": []}

    if "temp_files" not in st.session_state:
        st.session_state.temp_files = {}

    if "not_import_default_category" not in st.session_state:
        st.session_state.not_import_default_category = False

    if os.path.exists(path_categories_file):
        with open(path_categories_file, "r") as f:
            st.session_state.categories = json.load(f)
        session_handler = ssh(st.session_state.categories)
    else:
        with open(path_categories_file, "x") as f:
            f.write('{"Uncategorized": []}')

        with open(path_categories_file, "r") as f:
            st.session_state.categories = json.load(f)
        session_handler = ssh(st.session_state.categories)

    return session_handler


def import_default_category(df: pd.DataFrame, session_handler, categories_file) -> None:
    found_category_column = False
    df.columns = [col.strip() for col in df.columns]
    for column_name in df.columns:
        if "category" in column_name.lower():
            found_category_column = True
            column_old_name = column_name
            category_column = column_name.lower().strip().replace(" ", "_")
            break
    if found_category_column:
        df.columns = [category_column if column_name == column_old_name else column_name for column_name in df.columns]
    if not found_category_column:
        raise Exception("No default category column found")

    add_category_with_keyword(categories_file, category_column, df, session_handler)

def load_new_categories_with_keywords(df: pd.DataFrame, session_handler: ssh, categories_file: str) -> None:
    if category_column is None:
        import_default_category(df, session_handler, categories_file)

    add_new_category(category_column, True, session_handler, categories_file, False)


def add_category_with_keyword(categories_file, category_column, df, session_handler):
    for idx, row in df.iterrows():
        category = row[category_column].lower().strip()
        add_new_category(category, True, session_handler, categories_file, False)
        session_handler.save_categories(categories_file)
        description = row["Description"].lower().strip()
        session_handler.add_keyword_to_category(category, description, categories_file)