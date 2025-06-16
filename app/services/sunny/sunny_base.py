from ...utils.sunny.sunny_loader import SunnyLoader
from ...utils.sunny.sunny_df_manager import SunnyDataframeManager
from ...utils.sunny.sunny_container_manager import SunnyContainerManager
from ...utils.csv_manager import CSVManager
import os


class BaseSunnyService:
    def __init__(self, pl_column_mapping):
        self.pl_column_mapping = pl_column_mapping

    def process_file(self, file_path, output_dir):
        """
        Processus principal pour gérer le fichier Excel et générer les CSV.
        """
        dataframe = self._prepare_dataframe(file_path)
        if dataframe is None:
            print("❌ ERREUR: Impossible de traiter le fichier (fichier vide ou erreur de lecture)")
            return None

        containers = self._group_containers(dataframe)

        generated_files = []

        for index, container in enumerate(containers, start=1):
            container_dataframe = self._filter_container(dataframe, container)
            output_csv_path = self._process_container(container_dataframe, output_dir, index, len(containers) == 1)

            if output_csv_path:
                generated_files.append(output_csv_path)

        # Filtrer les fichiers valides uniquement
        generated_files = [file for file in generated_files if file is not None]

        if not generated_files:
            print("❌ ERREUR: Aucun fichier valide généré.")
            return None

        print(f"✅ Fichiers générés: {generated_files}")
        return generated_files


    def _prepare_dataframe(self, file_path):
        dataframe = SunnyLoader.load_excel_file(file_path)

        if dataframe is None or dataframe.empty:  # Vérification renforcée
            print("❌ ERREUR: Le fichier Excel est vide ou non lisible !")
            return None

        print("📌 Aperçu des données chargées :", dataframe.head())

        SunnyDataframeManager.normalize_columns(dataframe)
        SunnyDataframeManager.validate_columns(dataframe, self.pl_column_mapping)
        SunnyDataframeManager.add_missing_columns(dataframe, self.pl_column_mapping)

        return dataframe



    def _group_containers(self, dataframe):
        """
        Grouper les conteneurs présents dans le DataFrame.
        """
        return SunnyContainerManager.group_by_container(dataframe)

    def _filter_container(self, dataframe, container):
        """
        Filtre les données pour un conteneur spécifique.
        """
        return SunnyContainerManager.filter_by_container(dataframe, "Container", container)

    
    def _process_container(self, container_dataframe, output_dir, index, single_container):
        """
        Traite un conteneur et génère un fichier CSV correspondant.
        """
        if container_dataframe is None or container_dataframe.empty:
            print(f"⚠️ Conteneur {index}: Aucun enregistrement trouvé, le fichier CSV ne sera pas généré.")
            return None

        print(f"📌 Traitement du conteneur {index}...")

        extracted_data = self._extract_data(container_dataframe)
        if not extracted_data:
            print(f"⚠️ Conteneur {index}: Aucune donnée extraite, fichier CSV non généré.")
            return None  

        exporter_ref = self._get_exporter_ref(container_dataframe)
        full_exporter_ref = exporter_ref if single_container else f"{exporter_ref}_{index}"

        for row in extracted_data:
            row["Exporter Ref"] = full_exporter_ref

        output_csv_path = self._generate_csv_filename(output_dir, exporter_ref, index)

        try:
            self._write_to_csv(output_csv_path, extracted_data)
        except Exception as e:
            print(f"❌ ERREUR: Échec de l'écriture du fichier {output_csv_path}. Raison: {e}")
            return None  

        if not os.path.exists(output_csv_path) or os.path.getsize(output_csv_path) == 0:
            print(f"❌ ERREUR: Le fichier {output_csv_path} est vide ou n'a pas été correctement généré.")
            return None

        print(f"✅ CSV généré avec succès : {output_csv_path}")
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
        if "Ref nr" not in container_dataframe.columns:
            print("⚠️ 'Ref nr' non trouvé dans les colonnes, valeur par défaut utilisée.")
            return "Unknown"

        return container_dataframe["Ref nr"].dropna().iloc[0] if not container_dataframe["Ref nr"].dropna().empty else "Unknown"


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
        if not extracted_data or len(extracted_data) == 0:
            print(f"⚠️ Aucune donnée à écrire dans {output_csv_path}, fichier non généré.")
            return None

        try:
            # ❌ Supprime le paramètre 'encoding'
            CSVManager.write_csv(output_csv_path, extracted_data)
        except Exception as e:
            print(f"❌ ERREUR: Impossible d'écrire le fichier CSV ({e})")
            return None

        if not os.path.exists(output_csv_path) or os.path.getsize(output_csv_path) == 0:
            print(f"❌ ERREUR: Le fichier {output_csv_path} est vide ou n'a pas été correctement généré.")
            return None

        print(f"✅ CSV généré avec succès : {output_csv_path}")
        return output_csv_path



