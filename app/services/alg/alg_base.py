from ...utils.alg.alg_loader import AlgLoader
from ...utils.alg.alg_df_manager import AlgDataframeManager
from ...utils.alg.alg_container_manager import AlgContainerManager
from ...utils.csv_manager import CSVManager
import os

class BaseAlgService:
    def __init__(self, pl_column_mapping):
        self.pl_column_mapping = pl_column_mapping

    def process_file(self, file_path, output_dir):
        dataframe = self._prepare_dataframe(file_path)
        containers = self._group_containers(dataframe)
        generated_files = []

        for index, container in enumerate(containers, start=1):
            container_dataframe = self._filter_container(dataframe, container)
            output_csv_path = self._process_container(container_dataframe, output_dir, index, len(containers) == 1)
            if output_csv_path:
                generated_files.append(output_csv_path)

        print(f"✅ DEBUG: Fichiers générés = {generated_files}")
        return generated_files

    def _prepare_dataframe(self, file_path):
        dataframe = AlgLoader.load_excel_file(file_path, sheet_name="Sheet1")
        AlgDataframeManager.normalize_columns(dataframe)
        AlgDataframeManager.validate_columns(dataframe, self.pl_column_mapping)
        AlgDataframeManager.add_missing_columns(dataframe, self.pl_column_mapping)
        return dataframe

    def _group_containers(self, dataframe):
        return AlgContainerManager.group_by_container(dataframe)

    def _filter_container(self, dataframe, container):
        return AlgContainerManager.filter_by_container(dataframe, "Container No", container)

    def _process_container(self, container_dataframe, output_dir, index, single_container):
        extracted_data = self._extract_data(container_dataframe)
        exporter_ref = self._get_exporter_ref(container_dataframe)
        full_exporter_ref = exporter_ref if single_container else f"{exporter_ref}_{index}"

        for row in extracted_data:
            row["Exporter Ref"] = full_exporter_ref

        output_csv_path = self._generate_csv_filename(output_dir, exporter_ref, index)
        self._write_to_csv(output_csv_path, extracted_data)
        return output_csv_path

    def _extract_data(self, container_dataframe):
        raise NotImplementedError("La méthode _extract_data doit être implémentée dans une classe dérivée.")

    def _get_exporter_ref(self, container_dataframe):
        return container_dataframe["Invoice ID"].dropna().iloc[0] if "Invoice ID" in container_dataframe.columns else "Unknown"

    def _generate_csv_filename(self, output_dir, exporter_ref, index):
        fournisseur = self.csv_settings.get("Fournisseur", "Générique")  # par défaut
        subfolder = os.path.join(output_dir, fournisseur)
        os.makedirs(subfolder, exist_ok=True)
        return os.path.join(subfolder, f"PL_{exporter_ref}_{index}.csv")

    def _write_to_csv(self, output_csv_path, extracted_data):
        if not extracted_data:
            print("⚠️ Aucune donnée extraite ! Vérifie ton extraction.")
            return
        clean_data = []
        for row in extracted_data:
            clean_row = {key.strip(): value for key, value in row.items()}
            clean_data.append(clean_row)

        CSVManager.write_csv(output_csv_path, clean_data)
        print(f"✅ CSV généré : {output_csv_path}")
