class AlgContainerManager:
    @staticmethod
    def group_by_container(df, container_column="Container No"):
        """
        Retourne une liste des conteneurs uniques.
        """
        if container_column not in df.columns:
            raise ValueError(f"La colonne '{container_column}' est introuvable dans les données.")
        return df[container_column].dropna().unique()

    @staticmethod
    def filter_by_container(df, container_column, container):
        """
        Filtre les données pour un conteneur spécifique.
        """
        return df[df[container_column] == container]
