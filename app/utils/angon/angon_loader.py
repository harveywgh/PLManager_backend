import pandas as pd

class AngonLoader:
    @staticmethod
    def load_excel_file(file_path):
        df = pd.read_excel(file_path, sheet_name="Sheet1", dtype=str)
        print(f"📅 [AngonLoader] Chargement réussi : {len(df)} lignes")
        return df