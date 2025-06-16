from ...utils.safpro.safpro_loader import SafproLoader
from ...utils.safpro.safpro_df_manager import SafproDataframeManager
from ...utils.safpro.safpro_container_manager import SafproContainerManager
from ...utils.csv_manager import CSVManager
import os



class BaseSafproService:
    def __init__(self, pl_column_mapping):
        self.pl_column_mapping = pl_column_mapping

    def process_file(self, file_path, output_dir):
        """
        Processus principal pour gérer le fichier Excel et générer les CSV.
        Retourne une liste des fichiers générés.
        """
        dataframe = self._prepare_dataframe(file_path)
        containers = self._group_containers(dataframe)

        generated_files = []

        for index, container in enumerate(containers, start=1):
            container_dataframe = self._filter_container(dataframe, container)
            output_csv_path = self._process_container(container_dataframe, output_dir, index, len(containers) == 1)
            
            if output_csv_path:  
                generated_files.append(output_csv_path)

        print(f"✅ DEBUG: Fichiers générés = {generated_files}")
        return generated_files  # ✅ Retourne la liste des fichiers générés

    def _prepare_dataframe(self, file_path):
        """
        Chargement et préparation du DataFrame.
        """
        dataframe = SafproLoader.load_excel_file(file_path)
        SafproDataframeManager.normalize_columns(dataframe)
        SafproDataframeManager.validate_columns(dataframe, self.pl_column_mapping)
        SafproDataframeManager.add_missing_columns(dataframe, self.pl_column_mapping)
        return SafproDataframeManager.regroup_by_pallet_and_caliber(dataframe)

    def _group_containers(self, dataframe):
        """
        Grouper les conteneurs présents dans le DataFrame.
        """
        return SafproContainerManager.group_by_container(dataframe)

    def _filter_container(self, dataframe, container):
        """
        Filtre les données pour un conteneur spécifique.
        """
        return SafproContainerManager.filter_by_container(dataframe, "Container n°", container)

    def _process_container(self, container_dataframe, output_dir, index, single_container):
        """
        Traite un conteneur et génère un fichier CSV correspondant.
        Retourne le chemin du fichier généré.
        """
        extracted_data = self._extract_data(container_dataframe)
        exporter_ref = self._get_exporter_ref(container_dataframe)
        full_exporter_ref = exporter_ref if single_container else f"{exporter_ref}_{index}"

        for row in extracted_data:
            row["Exporter Ref"] = full_exporter_ref

        output_csv_path = self._generate_csv_filename(output_dir, exporter_ref, index)
        self._write_to_csv(output_csv_path, extracted_data)
        return output_csv_path



    def _extract_data(self, container_dataframe):
        """
        Extraction des données d'un conteneur. (À implémenter dans la classe dérivée.)
        """
        raise NotImplementedError("La méthode _extract_data doit être implémentée dans une classe dérivée.")

    def _get_exporter_ref(self, container_dataframe):
        """
        Récupère la référence de l'exportateur pour nommer le fichier.
        """
        return container_dataframe["Exporter ref"].dropna().iloc[0] if "Exporter ref" in container_dataframe.columns else "Unknown"

    def _generate_csv_filename(self, output_dir, exporter_ref, index):
        """
        Génère le nom du fichier CSV.
        """
        fournisseur = self.csv_settings.get("Fournisseur", "Générique")
        subfolder = os.path.join(output_dir, fournisseur)
        os.makedirs(subfolder, exist_ok=True)
        return os.path.join(subfolder, f"PL_{exporter_ref}_{index}.csv")

    def _write_to_csv(self, output_csv_path, extracted_data):
        """
        Écrit les données extraites dans un fichier CSV.
        """
        if not extracted_data:
            print("⚠️ Aucune donnée extraite ! Vérifie ton extraction.")
            return
        clean_data = []
        for row in extracted_data:
            clean_row = {key.strip(): value for key, value in row.items()}
            clean_data.append(clean_row)

        CSVManager.write_csv(output_csv_path, clean_data)
        print(f"✅ CSV généré : {output_csv_path}")


