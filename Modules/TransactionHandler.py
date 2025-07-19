import pandas as pd

from Modules.SessionStateHandler import SessionStateHandler


class TransactionHandler:

    def load_transactions(_self, file, _handler: SessionStateHandler):
        try:
            df = pd.read_csv(file)
            df.columns = [col.strip() for col in df.columns]
            return _self.categorize_transactions(df, _handler)
        except Exception as e:
            return f"Error processing file: {str(e)}"

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

    def merge_df(
        _self, df1: pd.DataFrame, df2: pd.DataFrame, merge_on: str
    ) -> pd.DataFrame:
        return pd.merge(
            df1,
            df2,
            on=merge_on,
            suffixes=("_file1", "_file2"),
        )
