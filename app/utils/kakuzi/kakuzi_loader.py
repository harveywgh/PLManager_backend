import pandas as pd

class KakuziLoader:
    @staticmethod
    def load_excel_file(file_path):
        """
        Charge les feuilles à partir de la 3e (index 1) du fichier Excel.
        Chaque feuille correspond à un conteneur.
        """
        all_sheets = pd.read_excel(file_path, sheet_name=None, header=None, dtype=str)
        sheet_names = list(all_sheets.keys())[1:] 
        dfs = {name: all_sheets[name] for name in sheet_names}
        print(f"📥 [KakuziLoader] {len(dfs)} feuilles chargées (1 feuille = 1 container, à partir de la 3ᵉ)")
        return dfs
