import pandas as pd

class CpfDataframeManager:
    @staticmethod
    def normalize_columns(df):
        df.columns = [str(col).strip() for col in df.columns]

    @staticmethod
    def validate_columns(df, column_mapping):
        expected = {col for cols in column_mapping.values() for col in cols}
        missing = [col for col in expected if col not in df.columns]
        if missing:
            print(f"⚠️ Colonnes manquantes dans CPF : {missing}")

    @staticmethod
    def add_missing_columns(df, column_mapping):
        for cols in column_mapping.values():
            for col in cols:
                if col not in df.columns:
                    print(f"➕ Ajout colonne absente : {col}")
                    df[col] = ""

    @staticmethod
    def regroup_by_pallet_and_caliber(df):
        numeric_cols = ["CASES"]  # NE PAS inclure NET WEIGHT ici
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(",", ".").astype(float)

        df["NET WEIGHT"] = df["NET WEIGHT"].astype(str).str.replace(",", ".").astype(float)

        grouped_df = df.groupby(["PALLET", "SIZE", "NET WEIGHT"], as_index=False).agg({
            col: "sum" if col in numeric_cols else "first"
            for col in df.columns
        })

        return grouped_df


