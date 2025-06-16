import pandas as pd
import os

class AlgLoader:
    @staticmethod
    def load_excel_file(file_path, sheet_name="Sheet1", header=0):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Le fichier spécifié n'existe pas : {file_path}")

        if file_path.endswith(".xlsx"):
            engine = "openpyxl"
        elif file_path.endswith(".xls"):
            engine = "xlrd"
        else:
            raise ValueError("Format de fichier non pris en charge. Utilisez .xlsx ou .xls.")

        try:
            dataframe = pd.read_excel(file_path, sheet_name=sheet_name, header=header, engine=engine)
            return dataframe
        except Exception as e:
            raise ValueError(f"Erreur lors du chargement du fichier '{file_path}' avec la feuille '{sheet_name}': {e}")
