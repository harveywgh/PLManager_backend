from app.utils.shalimar.shalimar_calculations import ShalimarCalculations


class ShalimarDataframeManager:
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
            "Net weight",
            "Boxes per pallet",
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
        for col in ["Pallet Number", "Size/Caliber"]:
            if col not in df.columns:
                raise ValueError(f"❌ Colonne manquante : {col}")

        # 🔹 Agrégation
        grouped_df = df.groupby(["Pallet Number", "Size/Caliber"], as_index=False).agg(
            {col: "sum" if col in sum_cols else "first" for col in df.columns if col != "Nb of pallets"}
        )

        # 🔹 Calcul de Nb of pallets basé uniquement sur Boxes per pallet
        if "Boxes per pallet" not in grouped_df.columns:
            raise ValueError("❌ 'Boxes per pallet' est requis pour calculer 'Nb of pallets'.")

        total = grouped_df.groupby("Pallet Number")["Boxes per pallet"].transform("sum")
        grouped_df["Nb of pallets"] = grouped_df["Boxes per pallet"] / total
        grouped_df["Nb of pallets"] = grouped_df["Nb of pallets"].round(5)

        return grouped_df
    
    @staticmethod
    def normalize_net_weight(df):
        """
        Nettoie et normalise la colonne 'Net weight' :
        - Remplace les virgules par des points
        - Supprime les chaînes vides ou non numériques
        - Convertit en float
        - Arrondit à l’unité
        """
        if "Net weight" not in df.columns:
            print("⚠️ Colonne 'Net weight' absente.")
            return

        df["Net weight"] = (
            df["Net weight"]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .str.extract(r"(\d+(?:\.\d+)?)")[0]  # Garde uniquement le nombre
            .fillna("0")
            .astype(float)
            .round()
            .astype(int)
        )
    
    @staticmethod
    def compute_packaging_type(df):
        """
        Crée 'Packaging type' : 'COLIS XKG' basé sur le poids par boîte.
        Si non numérique → 'COLIS KG'.
        """
        def build_packaging(value):
            weight_val = ShalimarCalculations._extract_numeric(value)
            return f"COLIS {int(weight_val)}KG" if weight_val is not None else "COLIS KG"

        if "Weight per box" not in df.columns:
            print("⚠️ Colonne 'Weight per box' absente pour créer 'Packaging type'")
            df["Packaging type"] = "COLIS KG"
        else:
            df["Packaging type"] = df["Weight per box"].apply(build_packaging)
        


