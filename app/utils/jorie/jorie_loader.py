import pandas as pd

class JorieLoader:
    @staticmethod
    def load_excel_file(file_path):
        """
        Charge le fichier Excel à partir de la ligne 14 et retourne un DataFrame.
        """
        df = pd.read_excel(file_path, dtype=str)
        print(f"📥 [JorieLoader] Chargement réussi : {len(df)} lignes")
        return df
