import os
import pandas as pd
from ...utils.viru.viru_loader import ViruLoader
from ...utils.viru.viru_container_manager import ViruContainerManager
from ...utils.csv_manager import CSVManager


class BaseViruService:
    def __init__(self, pl_column_mapping):
        self.pl_column_mapping = pl_column_mapping

    def process_file(self, file_path, output_dir):
        df_raw = ViruLoader.load_excel_file(file_path)
        metadata = ViruLoader.extract_metadata(df_raw)
        table_df = ViruLoader.extract_table(file_path)

        self._inject_metadata(table_df, metadata)

        containers = self._group_containers(table_df)

        generated_files = []
        for index, container in enumerate(containers, start=1):
            container_df = self._filter_container(table_df, container)
            output_csv = self._process_container(container_df, output_dir, index, len(containers) == 1)
            if output_csv:
                generated_files.append(output_csv)

        print(f"✅ Fichiers générés = {generated_files}")
        return generated_files

    def _inject_metadata(self, dataframe, metadata):
        """
        Injecte les métadonnées dans toutes les lignes du dataframe.
        """
        dataframe["Exporter Name"] = metadata.get("Exporter Name", "")
        dataframe["Exporter Ref"] = metadata.get("Exporter Ref", "")
        dataframe["Container No"] = metadata.get("Container No", "")
        dataframe["Seal No"] = metadata.get("Seal No", "")
        dataframe["Shipping line"] = metadata.get("Shipping line", "")
        dataframe["Vessel Name"] = metadata.get("Vessel Name", "")
        dataframe["ETD"] = metadata.get("ETD", "")  
        dataframe["ETA"] = metadata.get("ETA", "")  
        dataframe["Port of departure"] = metadata.get("Port of departure", "")
        dataframe["Port of arrival"] = metadata.get("Port of arrival", "")

        # Stockage dans l'instance
        self.exporter_name = metadata.get("Exporter Name", "")
        self.exporter_ref = metadata.get("Exporter Ref", "")
        self.container_no = metadata.get("Container No", "")
        self.vessel_name = metadata.get("Vessel Name", "")
        self.seal_no = metadata.get("Seal No", "")
        self.etd = metadata.get("ETD", "")
        self.eta = metadata.get("ETA", "")



    def _group_containers(self, dataframe):
        return ViruContainerManager.group_by_container(dataframe)

    def _filter_container(self, dataframe, container):
        return ViruContainerManager.filter_by_container(dataframe, "Container No", container)

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
        exporter_refs = container_df.get("Exporter Ref", pd.Series()).dropna()
        if not exporter_refs.empty:
            return exporter_refs.iloc[0]

        container_nos = container_df.get("Container No", pd.Series()).dropna()
        if not container_nos.empty:
            print("⚠️ Aucun 'Exporter Ref' trouvé, on utilise le 'Container No'")
            return container_nos.iloc[0]

        print("⚠️ Aucun 'Exporter Ref' ni 'Container No' trouvé, on utilise 'Unknown'")
        return "Unknown"

    def _generate_csv_filename(self, output_dir, exporter_ref, index):
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
