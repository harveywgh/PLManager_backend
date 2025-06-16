class CpfContainerManager:
    @staticmethod
    def group_by_container(df):
        containers = df["CONTAINER NUMBER"].dropna().unique().tolist()
        print(f"📦 Containers CPF : {containers}")
        return containers

    @staticmethod
    def filter_by_container(df, column_name, container_value):
        filtered = df[df[column_name] == container_value]
        print(f"🔍 Container CPF {container_value} : {len(filtered)} lignes")
        return filtered
    
    @staticmethod
    def regroup_by_pallet_and_caliber(df):
        sum_cols = ["CASES", "NET WEIGHT", "Nb of pallets"]

        # Nettoyage
        for col in sum_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(",", ".").astype(float)

        # Regroupement
        grouped = df.groupby(["PALLET", "SIZE"], as_index=False).agg(
            lambda x: x.iloc[0] if x.name not in sum_cols else x.sum()
        )

        # Optionnel : recalcul de la répartition des palettes si tu veux plus tard
        return grouped

