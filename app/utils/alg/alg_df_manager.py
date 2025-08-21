import pandas as pd

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
        
    @staticmethod
    def regroup_by_pallet_and_caliber(df):
        sum_cols = ["Nett Weight", "No Cartons"]

        for col in sum_cols:
            if col in df.columns:
                df[col] = (
                    df[col].astype(str)
                        .str.replace(",", ".", regex=False)
                        .str.strip()
                        .replace("", "0")
                        .astype(float)
                )

        if "Barcode" not in df.columns or "Count Code" not in df.columns:
            raise ValueError("❌ Colonnes 'Barcode' et 'Count Code' requises pour le regroupement.")

        # 🔹 On repère les lignes qui ont des doublons parfaits (même Barcode + Count Code)
        key_cols = ["Barcode", "Count Code"]
        duplicate_keys = df.duplicated(subset=key_cols, keep=False)

        df_to_group = df[duplicate_keys].copy()
        df_to_keep = df[~duplicate_keys].copy()

        # 🔹 On regroupe celles qui peuvent l’être
        grouped = df_to_group.groupby(key_cols, as_index=False).agg(
            {col: "sum" if col in sum_cols else "first" for col in df.columns if col != "Nb of pallets"}
        )
        grouped["Nb of pallets"] = 1.0  

        # 🔹 On reconstitue le DataFrame complet
        final_df = pd.concat([df_to_keep, grouped], ignore_index=True)

        return final_df

