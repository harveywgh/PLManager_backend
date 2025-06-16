import pandas as pd
import os

class SFALoader:
    @staticmethod
    def load_excel_file(file_path, sheet_name="Data", header=0):
        """
        Charge un fichier Excel (.xlsx ou .xls) et retourne un DataFrame.

        :param file_path: Chemin du fichier Excel.
        :param sheet_name: Nom de la feuille à charger.
        :param header: Ligne d'en-tête du fichier Excel.
        :return: pandas.DataFrame contenant les données du fichier Excel.
        :raises ValueError: Si le chargement échoue ou si l'extension n'est pas supportée.
        :raises FileNotFoundError: Si le fichier n'existe pas.
        """
        # Vérifier si le fichier existe
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Le fichier spécifié n'existe pas : {file_path}")

        # Déterminer le moteur en fonction de l'extension
        if file_path.endswith(".xlsx"):
            engine = "openpyxl"
        elif file_path.endswith(".xls"):
            engine = "xlrd"
        else:
            raise ValueError("Format de fichier non pris en charge. Utilisez .xlsx ou .xls.")

        try:
            # Charger le fichier Excel
            dataframe = pd.read_excel(file_path, sheet_name=sheet_name, header=header, engine=engine)
            return dataframe
        except Exception as e:
            raise ValueError(f"Erreur lors du chargement du fichier '{file_path}' avec la feuille '{sheet_name}': {e}")
