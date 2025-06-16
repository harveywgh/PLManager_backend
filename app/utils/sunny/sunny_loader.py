import pandas as pd
import openpyxl
import os

class SunnyLoader:
    @staticmethod
    def load_excel_file(file_path, sheet_name=None, header=0):
        """
        Charge un fichier Excel (.xlsx ou .xls) et retourne un DataFrame.

        :param file_path: Chemin du fichier Excel.
        :param sheet_name: Nom de la feuille à charger. Si None, charge la première feuille.
        :param header: Ligne d'en-tête du fichier Excel.
        :return: pandas.DataFrame contenant les données du fichier Excel.
        :raises ValueError: Si le chargement échoue ou si l'extension n'est pas supportée.
        :raises FileNotFoundError: Si le fichier n'existe pas.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Le fichier spécifié n'existe pas : {file_path}")

        if file_path.endswith(".xlsx"):
            engine = "openpyxl"
        elif file_path.endswith(".xls"):
            engine = "xlrd"
        else:
            raise ValueError("Format de fichier non pris en charge. Utilisez .xlsx ou .xls.")

        try:
            # Charger les noms des feuilles disponibles
            excel_file = pd.ExcelFile(file_path, engine=engine)
            
            # Utiliser la première feuille si sheet_name n'est pas spécifié
            if sheet_name is None:
                sheet_name = excel_file.sheet_names[0]
                print(f"Aucun nom de feuille spécifié. Chargement de la première feuille : {sheet_name}")

            dataframe = pd.read_excel(excel_file, sheet_name=sheet_name, header=header)
            return dataframe

        except Exception as e:
            raise ValueError(f"Erreur lors du chargement du fichier '{file_path}' avec la feuille '{sheet_name}': {e}")
