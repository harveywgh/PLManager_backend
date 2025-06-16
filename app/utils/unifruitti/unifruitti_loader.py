import pandas as pd

class UnifruittiLoader:
    @staticmethod
    def load_excel_file(file_path):
        """
        Charge le fichier Excel et retourne un DataFrame.
        """
        df = pd.read_excel(file_path, sheet_name=0, dtype=str)
        print(f"📥 [UnifruittiLoader] Chargement réussi : {len(df)} lignes")
        return df