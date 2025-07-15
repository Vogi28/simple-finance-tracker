import Modules.method_helper as method_helper
import os
import plotly.graph_objects as go
import streamlit as st
from Modules.TransactionHandler import TransactionHandler as th


CATEGORIES_FILE = os.getcwd() + "/categories.json"

session_handler = method_helper.initialize_state(CATEGORIES_FILE)

tr_handler = th()


def load_csv_file(file):
    return tr_handler.load_transactions(file, session_handler)


# Streamlit app
st.title("Compare Bank Statement Expenses by Category")

# File uploaders for the two CSV files
file1 = st.file_uploader("Upload First Bank Statement (CSV)", type=["csv"])
file2 = st.file_uploader("Upload Second Bank Statement (CSV)", type=["csv"])

# Display the expense categories and their sums for both files
if file1 is not None and file2 is not None:
    df1 = load_csv_file(file1)
    df2 = load_csv_file(file2)

    # copy only the expenses
    df1_debits = df1[df1["Debit/Credit"] == "Debit"].copy()
    df2_debits = df2[df2["Debit/Credit"] == "Debit"].copy()

    # Assuming each CSV has columns 'category' and 'amount'
    if {"Category", "Amount"}.issubset(df1_debits.columns) and {
        "Category",
        "Amount",
    }.issubset(df2_debits.columns):
        category_amount1 = df1_debits.groupby("Category")["Amount"].sum().reset_index()
        category_amount2 = df2_debits.groupby("Category")["Amount"].sum().reset_index()

        # Merge the two dataframes on 'category' and add a column for file2
        merged_df = tr_handler.merge_df(category_amount1, category_amount2, "Category")

        merged_df["Category"] = merged_df["Category"]

        st.write("Comparison of Expenses by Category")
        st.dataframe(merged_df)

        # Create the Figure with go because cound't find a way to make comparison with px
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=merged_df["Category"].tolist(),
                y=merged_df["Amount_file1"].tolist(),
                name="Bank Statement 1",
                marker_color="indianred",
            )
        )

        fig.add_trace(
            go.Bar(
                x=merged_df["Category"].tolist(),
                y=merged_df["Amount_file2"].tolist(),
                name="Bank Statement 2",
                marker_color="lightsalmon",
            )
        )
        fig.update_layout(
            dict(
                barcornerradius=15,
            ),
            barmode="group",
            xaxis_tickangle=-45,
            plot_bgcolor="white",
        )

        st.plotly_chart(fig)

    else:
        st.error("CSV files must contain 'Category' and 'Amount' columns.")
else:
    st.warning("Please upload both CSV files to compare expenses by category.")
