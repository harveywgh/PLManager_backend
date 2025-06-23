import pandas as pd

class UnifruittiLoader:
    @staticmethod
    def load_excel_file(file_path):
        """
        Charge le fichier Excel à partir de la ligne 14 et retourne un DataFrame.
        """
        df = pd.read_excel(file_path, sheet_name="Packing Data", dtype=str, skiprows=13)
        print(f"📥 [UnifruittiLoader] Chargement réussi : {len(df)} lignes")
        return df
