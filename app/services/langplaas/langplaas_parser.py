import pandas as pd
import os

from .langplaas_metadata import (
    _load_sheet,
    extract_container_number,
    extract_pol,
    extract_pod,
    extract_vessel,
    extract_eta,
    extract_etd,
    extract_seal_no
)

class LangplaasParser:
    @staticmethod
    def extract_dataframe(file_path, sheet_name="Sheet1"):
        # Charger la feuille Excel
        sheet = _load_sheet(file_path, sheet_name)

        # Lire le tableau sans header (on va les fixer nous-mêmes)
        raw_df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, engine="openpyxl", skiprows=27)

        # Définir manuellement les vrais noms de colonnes dans l'ordre
        true_columns = [
            "Pallet Number", "GGN", "PUC", "Orch.", "Comm.", "Var.", "Class",
            "Count", "Brand", "Inventory", "TM", "Packing", "Ctns.", "Pallets",
            "Actual Gross Weight", "Actual Nett Weight", "Temptale No."
        ]

        # Ajuste à la bonne longueur en coupant ou complétant selon ton fichier
        raw_df = raw_df.iloc[:, :len(true_columns)]
        raw_df.columns = true_columns

        # Injecter les métadonnées
        raw_df["Container No."] = extract_container_number(sheet)
        raw_df["P.O.L"] = extract_pol(sheet)
        raw_df["P.O.D"] = extract_pod(sheet)
        raw_df["Vessel"] = extract_vessel(sheet)
        raw_df["ETA"] = extract_eta(sheet)
        raw_df["ETD"] = extract_etd(sheet)
        raw_df["Seal No."] = extract_seal_no(sheet)

        # Debug : vérifie les colonnes détectées
        print("📌 Colonnes réelles après nettoyage :")
        for col in raw_df.columns:
            print(f"   → '{col}'")

        return raw_df
