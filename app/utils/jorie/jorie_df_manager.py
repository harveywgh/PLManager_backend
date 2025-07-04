class JorieDataframeManager:
    @staticmethod
    def normalize_columns(df):
        """
        Nettoie les noms de colonnes (trim et corrections spécifiques).
        """
        df.columns = [str(col).strip() for col in df.columns]
        if "ContainerNumber" in df.columns:
            df.rename(columns={"ContainerNumber": "Container n°"}, inplace=True)




    @staticmethod
    def validate_columns(df, column_mapping):
        """
        Vérifie que toutes les colonnes attendues existent.
        """
        expected_columns = {col for cols in column_mapping.values() for col in cols}
        missing = [col for col in expected_columns if col not in df.columns]
        if missing:
            print(f"⚠️ Colonnes manquantes détectées : {missing}")

    @staticmethod
    def add_missing_columns(df, column_mapping):
        """
        Ajoute les colonnes manquantes avec valeurs vides.
        """
        for csv_field, excel_columns in column_mapping.items():
            for col in excel_columns:
                if col not in df.columns:
                    print(f"➕ Ajout colonne absente : {col}")
                    df[col] = ""
                    
    
    @staticmethod
    def regroup_by_pallet_and_caliber(df):
        sum_cols = [
            "Mass",
            "CtnQty",
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
        for col in ["PalletId", "SizeCount", "Grade", "Mark"]:
            if col not in df.columns:
                raise ValueError(f"❌ Colonne manquante : {col}")

        # 🔹 Agrégation
        grouped_df = df.groupby(["PalletId", "SizeCount", "Grade", "Mark"], as_index=False).agg(
            {col: "sum" if col in sum_cols else "first" for col in df.columns if col != "PltQty"}
        )

        # 🔹 Calcul de Nb of pallets basé uniquement sur Quantity per grower
        if "CtnQty" not in grouped_df.columns:
            raise ValueError("❌ 'Quantity per grower' est requis pour calculer 'Nb of pallets'.")

        total = grouped_df.groupby("PalletId")["CtnQty"].transform("sum")
        grouped_df["PltQty"] = grouped_df["CtnQty"] / total
        grouped_df["PltQty"] = grouped_df["PltQty"].round(5)

        return grouped_df











