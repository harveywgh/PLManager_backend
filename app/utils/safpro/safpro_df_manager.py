class SafproDataframeManager:
    @staticmethod
    def add_missing_columns(dataframe, column_mapping):
        """
        Ajoute les colonnes manquantes dans le DataFrame en fonction du mappage fourni.
        Les colonnes manquantes sont ajoutées avec des valeurs vides.
        """
        for csv_field, excel_columns in column_mapping.items():
            if csv_field not in dataframe.columns:
                dataframe[csv_field] = ""  # Ajout avec des valeurs vides

    @staticmethod
    def validate_columns(dataframe, column_mapping):
        """
        Valide et ajoute automatiquement les colonnes manquantes dans le DataFrame.
        Si une colonne est absente, elle est ajoutée avec une chaîne vide.
        """
        dataframe.columns = dataframe.columns.str.strip()  # Normalisation des noms de colonnes

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
        sum_cols = [
            "Net weight per pallet (kg)",
            "Cartons",
        ]

        # 🔹 Conversion propre
        for col in sum_cols:
            if col in df.columns:
                df[col] = (
                    df[col].astype(str)
                        .str.replace(",", ".", regex=False)
                        .str.strip()
                        .replace("", "0")
                        .astype(float)
                )

        # 🔹 Validation
        for col in ["Pallet n°", "Size/caliber/count"]:
            if col not in df.columns:
                raise ValueError(f"❌ Colonne manquante : {col}")

        # 🔹 Agrégation
        grouped_df = df.groupby(["Pallet n°", "Size/caliber/count"], as_index=False).agg(
            {col: "sum" if col in sum_cols else "first" for col in df.columns if col != "Nb of pallets"}
        )

        # 🔹 Calcul de Nb of pallets basé uniquement sur Quantity per grower
        if "Cartons" not in grouped_df.columns:
            raise ValueError("❌ 'Cartons' est requis pour calculer 'Nb of pallets'.")

        total = grouped_df.groupby("Pallet n°")["Cartons"].transform("sum")
        grouped_df["Nb of pallets"] = grouped_df["Cartons"] / total
        grouped_df["Nb of pallets"] = grouped_df["Nb of pallets"].round(6)

        return grouped_df
