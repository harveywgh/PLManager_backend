class HnpDataframeManager:
    @staticmethod
    def normalize_columns(df):
        """
        Nettoie les noms de colonnes (trim et corrections spécifiques).
        """
        df.columns = [str(col).strip() for col in df.columns]
        if "Container n° (ABCD1234567)" in df.columns:
            df.rename(columns={"Container n° (ABCD1234567)": "Container n°"}, inplace=True)



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
            "Net weight per pallet (kg)",
            "Quantity"
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
        for col in ["Pallet Ref. Nr.", "Size", "Grade"]:
            if col not in df.columns:
                raise ValueError(f"❌ Colonne manquante : {col}")

        # 🔹 Agrégation avec regroupement par Pallet Ref, Quantity, et Grade
        grouped_df = df.groupby(["Pallet Ref. Nr.", "Size", "Grade"], as_index=False).agg(
            {col: "sum" if col in sum_cols else "first" for col in df.columns if col != "Pallet Size"}
        )

        # 🔹 Calcul de Pallet Size basé uniquement sur Quantity
        total = grouped_df.groupby("Pallet Ref. Nr.")["Quantity"].transform("sum")
        grouped_df["Pallet Size"] = grouped_df["Quantity"] / total
        grouped_df["Pallet Size"] = grouped_df["Pallet Size"].round(5)

        return grouped_df




