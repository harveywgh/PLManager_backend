class IngophaseContainerManager:
    @staticmethod
    def group_by_container(df):
        """
        Retourne la liste des containers uniques.
        """
        if "ContainerNumber" in df.columns:
            containers = df["ContainerNumber"].dropna().unique().tolist()
        else:
            print("⚠️ Colonne 'ContainerNumber' absente, traitement avec un seul conteneur par défaut.")
            containers = ["DEFAULT"]
        print(f"📦 Containers détectés : {containers}")
        return containers

    @staticmethod
    def filter_by_container(df, column_name, container_value):
        """
        Filtre le DataFrame pour un container donné.
        """
        if column_name in df.columns:
            filtered = df[df[column_name] == container_value]
        else:
            filtered = df.copy()
        print(f"🔍 Données filtrées pour container {container_value} : {len(filtered)} lignes")
        return filtered
