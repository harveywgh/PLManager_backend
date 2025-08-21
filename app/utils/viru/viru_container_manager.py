class ViruContainerManager:
    @staticmethod
    def group_by_container(df):
        """
        Retourne la liste des containers uniques.
        """
        container_col = "Container No"
        if container_col not in df.columns:
            raise ValueError(f"❌ Colonne manquante : {container_col}")
        containers = df[container_col].dropna().unique().tolist()
        print(f"📦 Containers détectés : {containers}")
        return containers


    @staticmethod
    def filter_by_container(df, column_name, container_value):
        """
        Filtre le DataFrame pour un container donné.
        """
        filtered = df[df[column_name] == container_value]
        print(f"🔍 Données filtrées pour container {container_value} : {len(filtered)} lignes")
        return filtered
