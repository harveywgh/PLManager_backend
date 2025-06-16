import pandas as pd
import os

class CpfLoader:
    @staticmethod
    def load_excel_file(file_path):
        """
        Tente de charger le fichier CPF avec xlrd, sinon fallback vers openpyxl.
        """
        try:
            print(f"🔍 Tentative de lecture avec l'engine : xlrd (.xls)")
            return pd.read_excel(file_path, sheet_name="Manifest", header=2, dtype=str, engine="xlrd")

        except Exception as e1:
            print(f"⚠️ xlrd a échoué : {e1}")
            print(f"🔄 Tentative de lecture avec openpyxl (.xlsx)")
            try:
                return pd.read_excel(file_path, sheet_name="Manifest", header=2, dtype=str, engine="openpyxl")
            except Exception as e2:
                print(f"❌ Les deux tentatives ont échoué : {e2}")
                return pd.DataFrame()
