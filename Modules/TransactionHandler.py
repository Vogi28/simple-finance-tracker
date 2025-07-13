import pandas as pd
import streamlit as st
from Modules.SessionStateHandler import SessionStateHandler


class TransactionHandler:
    @st.cache_data  # 👈 Add the caching decorator
    def load_transactions(_self, file, _handler: SessionStateHandler):
        try:
            df = pd.read_csv(file)
            df.columns = [col.strip() for col in df.columns]
            return _self.categorize_transactions(df, _handler)
        except Exception as e:
            return f"Error processing file: {str(e)}"

    @st.cache_data
    def categorize_transactions(_self, df: pd.DataFrame, _handler: SessionStateHandler):
        df["Category"] = "Uncategorized"
        for category, keywords in _handler.categories.items():
            if category == "Uncategorized" or not keywords:
                continue

            lowered_keywords = [keyword.lower().strip() for keyword in keywords]

            for idx, row in df.iterrows():
                description = row["Description"].lower().strip()
                for lowered_keyword in lowered_keywords:
                    if lowered_keyword in description:
                        df.at[idx, "Category"] = category
                        break

        return df
