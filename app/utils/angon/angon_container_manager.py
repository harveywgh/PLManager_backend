class AngonContainerManager:
    @staticmethod
    def group_by_container(df):
        containers = df["Container"].dropna().unique().tolist()
        print(f"🛆 Containers détectés : {containers}")
        return containers

    @staticmethod
    def filter_by_container(df, column_name, container_value):
        filtered = df[df[column_name] == container_value]
        print(f"🔍 Données filtrées pour container {container_value} : {len(filtered)} lignes")
        return filtered