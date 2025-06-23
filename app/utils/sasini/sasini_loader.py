import pandas as pd

class SasiniLoader:
    @staticmethod
    def load_all_sheets(file_path):
        """
        Charge toutes les feuilles Excel et retourne un dictionnaire : {nom_feuille: DataFrame}
        Chaque feuille représente un container distinct.
        """
        all_dfs = pd.read_excel(file_path, sheet_name=None, dtype=str)
        print(f"📥 [SasiniLoader] Feuilles chargées : {list(all_dfs.keys())}")
        return all_dfs
