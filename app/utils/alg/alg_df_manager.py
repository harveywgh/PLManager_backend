class AlgDataframeManager:
    @staticmethod
    def add_missing_columns(dataframe, column_mapping):
        """
        Ajoute les colonnes manquantes dans le DataFrame en fonction du mappage fourni.
        Les colonnes manquantes sont ajoutées avec des valeurs vides.
        """
        for csv_field, excel_columns in column_mapping.items():
            if csv_field not in dataframe.columns:
                dataframe[csv_field] = ""

    @staticmethod
    def validate_columns(dataframe, column_mapping):
        """
        Valide et ajoute automatiquement les colonnes manquantes dans le DataFrame.
        Si une colonne est absente, elle est ajoutée avec une chaîne vide.
        """
        dataframe.columns = dataframe.columns.str.strip()

        for csv_field, excel_columns in column_mapping.items():
            if not any(col in dataframe.columns for col in excel_columns):
                dataframe[csv_field] = ""

    @staticmethod
    def normalize_columns(dataframe):
        """
        Normalise les colonnes du DataFrame en supprimant les espaces en début et fin des noms de colonnes.
        """
        dataframe.columns = dataframe.columns.str.strip()
