class SunnyContainerManager:
    @staticmethod
    def group_by_container(dataframe):
        """
        Grouper les données en fonction du numéro de conteneur.
        """
        return dataframe["Container"].unique()

    @staticmethod
    def filter_by_container(dataframe, column_name, container):
        """
        Filtre les données pour un conteneur spécifique.
        """
        return dataframe[dataframe[column_name] == container]

