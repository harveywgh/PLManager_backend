from ...utils.southern_fruit_alliance.southern_fruit_alliance_loader import SFALoader
from ...utils.southern_fruit_alliance.southern_fruit_alliance_df_manager import SFADataframeManager
from ...utils.southern_fruit_alliance.southern_fruit_alliance_container_manager import ContainerManager
from ...utils.csv_manager import CSVManager
import pandas as pd
import os


class BaseSFAService:
    def __init__(self, pl_column_mapping):
        self.pl_column_mapping = pl_column_mapping

    def process_file(self, file_path, output_dir):
        """
        Processus principal pour gérer le fichier Excel et générer les CSV.
        """
        dataframe = self._prepare_dataframe(file_path)
        if dataframe is None or dataframe.empty:
            print("❌ ERREUR: Fichier vide ou illisible !")
            return None

        containers = self._group_containers(dataframe)
        if not isinstance(containers, list):
            print(f"❌ ERREUR: `_group_containers` ne retourne pas une liste valide: {type(containers)}")
            return None

        generated_files = []

        for index, container in enumerate(containers, start=1):
            container_dataframe = self._filter_container(dataframe, container)
            
            if not isinstance(container_dataframe, pd.DataFrame):
                print(f"❌ ERREUR: `_filter_container` a retourné un type incorrect: {type(container_dataframe)}")
                continue

            output_file = self._process_container(container_dataframe, output_dir, index, len(containers) == 1)
            if output_file:
                generated_files.append(output_file)

        if not generated_files:
            print("❌ ERREUR: Aucun fichier CSV généré !")
            return None

        print(f"✅ Fichiers générés : {generated_files}")
        return generated_files

    def _prepare_dataframe(self, file_path):
        dataframe = SFALoader.load_excel_file(file_path)

        if dataframe.empty:
            print("❌ ERREUR: Le fichier Excel est vide ou non lisible !")
            return None

        print("📌 Aperçu des données chargées :", dataframe.head())

        SFADataframeManager.normalize_columns(dataframe)
        SFADataframeManager.validate_columns(dataframe, self.pl_column_mapping)
        SFADataframeManager.add_missing_columns(dataframe, self.pl_column_mapping)

        return dataframe

    def _group_containers(self, dataframe):
        """
        Grouper les conteneurs présents dans le DataFrame.
        """
        containers = ContainerManager.group_by_container(dataframe)

        # Correction : s'assurer que la sortie est bien une liste
        if not isinstance(containers, list):
            containers = list(containers)

        return containers

    def _filter_container(self, dataframe, container):
        """
        Filtre les données pour un conteneur spécifique.
        """
        filtered = ContainerManager.filter_by_container(dataframe, "Container No", container)

        if not isinstance(filtered, pd.DataFrame):
            print(f"❌ ERREUR: `_filter_container` ne retourne pas un DataFrame mais {type(filtered)}")
            return pd.DataFrame()  # Retourne un DataFrame vide si problème

        return filtered

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
        Extraction des données d'un conteneur. À implémenter dans une classe dérivée.
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

        # 🔒 Nettoyage du nom de fichier pour éviter les séparateurs
        safe_ref = exporter_ref.replace("/", "-").replace("\\", "-")

        return os.path.join(subfolder, f"PL_{safe_ref}_{index}.csv")

    def _write_to_csv(self, output_csv_path, extracted_data):
        """
        Écrit les données extraites dans un fichier CSV.
        """
        if not extracted_data:
            print(f"⚠️ Aucune donnée à écrire dans {output_csv_path}, fichier non généré.")
            return None

        try:
            CSVManager.write_csv(output_csv_path, extracted_data)
        except Exception as e:
            print(f"❌ ERREUR: Impossible d'écrire le fichier CSV ({e})")
            return None

        print(f"✅ CSV généré avec succès : {output_csv_path}")
        return output_csv_path
