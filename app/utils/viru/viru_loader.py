import pandas as pd
from .viru_df_manager import ViruDataframeManager


class ViruLoader:
    @staticmethod
    def load_excel_file(file_path):
        """
        Charge le fichier Excel complet sans l’analyser.
        """
        df = pd.read_excel(file_path, header=None, dtype=str)
        return df

    @staticmethod
    def extract_metadata(df):
        """
        Extrait les métadonnées des cellules spécifiques.
        """
        metadata = {
            "Exporter Name": df.iloc[3, 1],       # B4
            "Exporter Ref": df.iloc[4, 1],        # B5
            "Container No": df.iloc[5, 1],        # B6
            "Shipping line": df.iloc[7, 1],       # B8
            "Vessel Name": df.iloc[8, 1],         # B9
            "Port of departure": df.iloc[9, 1],   # B10
            "Port of arrival": df.iloc[10, 1],    # B11
            "ETD": df.iloc[5, 4],                 # E6 
            "ETA": df.iloc[6, 4],                 # E7 
        }
        print("📌 Métadonnées VIRU :", metadata)
        return metadata

    @staticmethod
    def extract_table(file_path):
        """
        Charge uniquement le tableau avec en-têtes en ligne 15, data à partir de ligne 17 (index 16).
        """
        df = pd.read_excel(file_path, header=14, skiprows=[15], dtype=str)
        ViruDataframeManager.normalize_columns(df)
        print(f"📊 [ViruLoader] Tableau extrait : {len(df)} lignes")
        return df

