class GHDataframeManager:
    @staticmethod
    def normalize_columns(df):
        """
        Nettoie les noms de colonnes (strip).
        """
        df.columns = [str(col).strip() for col in df.columns]

    @staticmethod
    def validate_columns(df, column_mapping):
        """
        Vérifie que toutes les colonnes attendues sont présentes.
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
        # Colonnes à regrouper (valeurs numériques à additionner)
        sum_cols = ["Net weight per pallet (kg)", "Cartons per pallet", "Nb of pallets"]
        
        # On remplace les virgules par des points et convertit en float pour les agrégations
        for col in sum_cols:
            df[col] = df[col].astype(str).str.replace(",", ".").astype(float)

        grouped_df = df.groupby(["Pallet n°", "Size"], as_index=False).agg({
            "Net weight per pallet (kg)": "sum",
            "Cartons per pallet": "sum",
            "Nb of pallets": "sum",
            # toutes les autres colonnes : garde la première occurrence
            # ou ajoute ici toutes les colonnes à conserver
        })

        # Optionnel : correction du total de palette
        grouped_df["Nb of pallets"] = grouped_df.groupby("Pallet n°")[
            "Nb of pallets"].transform(lambda x: round(x / x.sum(), 3))


        return grouped_df
