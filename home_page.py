import os

import plotly.express as px
import streamlit as st

import Modules.method_helper as method_helper
from Modules.TransactionHandler import TransactionHandler as th

CATEGORIES_FILE = os.getcwd() + "/categories.json"

# load data
st.set_page_config(
    page_title="Finance Tracker",
    layout="wide",
    page_icon=":material/account_balance:",
)

session_handler = method_helper.initialize_state(CATEGORIES_FILE)


@st.dialog(title="Category list is empty. Import category from statement?", width="small")
def popup(df) -> None:
    no = st.button("No")
    yes = st.button("Yes")
    if yes:
        with st.spinner("Importing category from statement"):
            method_helper.import_default_category(df, session_handler, CATEGORIES_FILE)
        st.rerun()
    if no:
        st.session_state.not_import_default_category = True
        st.rerun()


def main():
    st.title("Dashboard")

    f = method_helper.sidebar_file_selector()

    uploaded_file = st.file_uploader(label="Upload your transaction file", type={"CSV"})

    if uploaded_file is not None or f is not None:
        tr_handler = th()
        if f is None:
            method_helper.save_file_in_session(uploaded_file)

        df = tr_handler.load_transactions(uploaded_file or f, session_handler)
        # if categories file is new and empty, ask if user want to import the one from the statement
        if len(session_handler.categories) <= 1 and st.session_state.not_import_default_category == False:
            popup(df)

        if isinstance(df, str):
            st.error(df)

        if df is not None:
            [start_date, end_date] = method_helper.define_start_end_date(df)
            session_handler.set_debits_df(df[df["Debit/Credit"] == "Debit"].copy())
            session_handler.convert_Trans_date_str_to_date_obj()

            tab = st.tabs(["Expenses (Debits)"])
            with tab[0]:

                with st.expander("Click to view your statement"):
                    new_category = st.text_input("New category name")
                    add_button = st.button("Add category")
                    method_helper.add_new_category(
                        new_category, add_button, session_handler, CATEGORIES_FILE
                    )

                    st.subheader(
                        f"Transactions from {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"
                    )

                    total_expenses = session_handler.debits_df["Amount"].sum()
                    st.metric("Total expenses", f"{total_expenses:,.2f} CHF")

                    edited_df = st.data_editor(
                        session_handler.debits_df[
                            [
                                "Transaction date",
                                "Amount",
                                "Currency",
                                "Description",
                                "Merchant",
                                "Category",
                            ]
                        ],
                        column_config={
                            "Transaction date": st.column_config.DateColumn(
                                "Transaction date", format="DD/MM/YYYY"
                            ),
                            "Amount": st.column_config.NumberColumn(
                                "Amount", format="%.2f"
                            ),
                            "Category": st.column_config.SelectboxColumn(
                                "Category",
                                options=list(session_handler.categories.keys()),
                            ),
                        },
                        hide_index=True,
                        use_container_width=True,
                        key="category_editor",
                    )

                    save_button = st.button("Apply changes", type="primary")
                    if save_button:
                        for idx, row in edited_df.iterrows():
                            new_category = row["Category"]
                            if (
                                    new_category
                                    == session_handler.debits_df.at[idx, "Category"]
                            ):
                                continue

                            description = row["Description"]
                            session_handler.debits_df.at[idx, "Category"] = new_category
                            if session_handler.add_keyword_to_category(
                                    new_category, description, CATEGORIES_FILE
                            ):
                                st.success(f"Changes applied for {description}")

                st.subheader(
                    f"Expense summary from {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}",
                    divider=True,
                )
                col1, col2 = st.columns(2)

                category_totals = (
                    session_handler.debits_df.groupby("Category")["Amount"]
                    .sum()
                    .reset_index()
                )

                category_totals = category_totals.sort_values("Amount", ascending=False)
                col1.dataframe(
                    category_totals,
                    column_config={
                        "Amount": st.column_config.NumberColumn(
                            "Amount", format="%.2f CHF"
                        )
                    },
                    use_container_width=True,
                    hide_index=True,
                )

                fig = px.pie(
                    category_totals,
                    values="Amount",
                    names="Category",
                )

                col2.plotly_chart(fig)
        st.session_state.categories = session_handler.categories


if __name__ == "__main__":
    main()
