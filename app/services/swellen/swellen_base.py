from ...utils.swellen.swellen_loader import SwellenLoader
from ...utils.swellen.swellen_df_manager import SwellenDataframeManager
from ...utils.swellen.swellen_container_manager import SwellenContainerManager
from ...utils.csv_manager import CSVManager
import os
import pandas as pd


class BaseSwellenService:
    def __init__(self, pl_column_mapping):
        self.pl_column_mapping = pl_column_mapping

    def process_file(self, file_path, output_dir):
        dataframe = self._prepare_dataframe(file_path)
        containers = self._group_containers(dataframe)

        generated_files = []
        for index, container in enumerate(containers, start=1):
            container_df = self._filter_container(dataframe, container)
            output_csv = self._process_container(container_df, output_dir, index, len(containers) == 1)
            if output_csv:
                generated_files.append(output_csv)

        print(f"✅ Fichiers générés = {generated_files}")
        return generated_files

    def _prepare_dataframe(self, file_path):
        dataframe = SwellenLoader.load_excel_file(file_path)
        SwellenDataframeManager.validate_columns(dataframe, self.pl_column_mapping)
        SwellenDataframeManager.add_missing_columns(dataframe, self.pl_column_mapping)
        dataframe = SwellenDataframeManager.regroup_by_pallet_and_caliber(dataframe)
        return dataframe

    def _group_containers(self, dataframe):
        return SwellenContainerManager.group_by_container(dataframe)

    def _filter_container(self, dataframe, container):
        return SwellenContainerManager.filter_by_container(dataframe, "ContainerNumber", container)

    def _process_container(self, container_df, output_dir, index, single_container):
        extracted_data = self._extract_data(container_df)
        exporter_ref = self._get_exporter_ref(container_df)
        full_ref = exporter_ref if single_container else f"{exporter_ref}_{index}"

        for row in extracted_data:
            row["Exporter Ref"] = full_ref

        output_path = self._generate_csv_filename(output_dir, exporter_ref, index)
        self._write_to_csv(output_path, extracted_data)
        return output_path

    def _extract_data(self, container_df):
        raise NotImplementedError()
    

    def _get_exporter_ref(self, container_df):
        """
        Récupère la référence de l'exportateur pour nommer le fichier.
        Si non trouvée, utilise le numéro de conteneur. Sinon 'Unknown'.
        """
        voyage_vals = container_df.get("Document Number", pd.Series()).dropna()
        if not voyage_vals.empty:
            return str(voyage_vals.iloc[0]).strip()

        # 2️⃣ Sinon utilise "Container n°"
        container_vals = container_df.get("ContainerNumber", pd.Series()).dropna()
        if not container_vals.empty:
            return str(container_vals.iloc[0]).strip()

        # 3️⃣ Sinon "Unknown"
        print("⚠️ Aucun 'Document Number' ni 'ContainerNumber' trouvé, on utilise 'Unknown'")
        return "Unknown"



    def _generate_csv_filename(self, output_dir, exporter_ref, index):
        """
        Génère le nom du fichier CSV.
        """
        fournisseur = self.csv_settings.get("Fournisseur", "Générique")
        subfolder = os.path.join(output_dir, fournisseur)
        os.makedirs(subfolder, exist_ok=True)
        return os.path.join(subfolder, f"PL_{exporter_ref}_{index}.csv")

    def _write_to_csv(self, path, data):
        if not data:
            print("⚠️ Aucune donnée à écrire.")
            return
        clean = [{k.strip(): v for k, v in row.items()} for row in data]
        CSVManager.write_csv(path, clean)
        print(f"✅ CSV généré : {path}")