import json
from datetime import datetime


class SessionStateHandler:
    def __init__(self, categories: dict) -> None:
        self.categories = categories

    def save_categories(
            self,
            categories_file: str,
    ) -> bool:
        try:
            with open(categories_file, "w") as f:
                json.dump(self.categories, f)
        except OSError:
            return False

        return True

    def add_keyword_to_category(
            self, category: str, keyword: str, category_file: str
    ) -> bool:
        keyword = keyword.strip()
        if keyword and keyword not in self.categories[category]:
            self.categories[category].append(keyword)
            return self.save_categories(category_file)

        return False

    def convert_Trans_date_str_to_date_obj(self) -> None:
        for idx, row in self.debits_df.iterrows():
            date = datetime.strptime(
                row["Transaction date"].lower().strip(), "%d.%m.%Y"
            ).date()
            self.debits_df.at[idx, "Transaction date"] = date

        return None

    def set_debits_df(self, data_frame) -> None:
        self.debits_df = data_frame

        return None
