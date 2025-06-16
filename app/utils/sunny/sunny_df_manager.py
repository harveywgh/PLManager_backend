import pandas as pd

class SunnyDataframeManager:
    @staticmethod
    def add_missing_columns(dataframe, column_mapping):
        """
        Ajoute les colonnes manquantes dans le DataFrame en fonction du mappage fourni.
        Les colonnes manquantes sont ajoutées avec des valeurs vides.
        """
        for columns in column_mapping.values():
            for column in columns:
                if column not in dataframe.columns:
                    dataframe[column] = ""

    @staticmethod
    def validate_columns(dataframe, column_mapping):
        """
        Valide et ajoute automatiquement les colonnes manquantes dans le DataFrame.
        Si une colonne est absente, elle est ajoutée avec une chaîne vide.
        """
        dataframe.columns = dataframe.columns.str.strip()

        for columns in column_mapping.values():
            for column in columns:
                if column not in dataframe.columns:
                    dataframe[column] = ""

    @staticmethod
    def normalize_columns(dataframe):
        """
        Normalise les colonnes du DataFrame en supprimant les espaces en début et fin des noms de colonnes.
        """
        dataframe.columns = dataframe.columns.str.strip()
