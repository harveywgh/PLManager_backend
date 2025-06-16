from .langplaas_parser import LangplaasParser
from ...utils.csv_manager import CSVManager
import os

class BaseLangplaasService:
    def __init__(self, pl_column_mapping):
        self.pl_column_mapping = pl_column_mapping

    def process_file(self, file_path, output_dir):
        dataframe = self._prepare_dataframe(file_path)
        containers = dataframe["Container No."].dropna().unique()

        generated_files = []
        for index, container in enumerate(containers, start=1):
            container_df = dataframe[dataframe["Container No."] == container]
            output_csv_path = self._process_container(container_df, output_dir, index, len(containers) == 1)
            if output_csv_path:
                generated_files.append(output_csv_path)

        print(f"✅ Fichiers générés : {generated_files}")
        return generated_files

    def _prepare_dataframe(self, file_path):
        return LangplaasParser.extract_dataframe(file_path)


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
        raise NotImplementedError("Doit être implémentée dans la classe enfant.")

    def _get_exporter_ref(self, container_dataframe):
        return container_dataframe["Seal No."].dropna().iloc[0] if "Seal No." in container_dataframe.columns else "Unknown"

    def _generate_csv_filename(self, output_dir, exporter_ref, index):
        fournisseur = self.csv_settings.get("Fournisseur", "Langplaas")
        subfolder = os.path.join(output_dir, fournisseur)
        os.makedirs(subfolder, exist_ok=True)
        return os.path.join(subfolder, f"PL_{exporter_ref}_{index}.csv")

    def _write_to_csv(self, output_csv_path, extracted_data):
        if not extracted_data:
            print("⚠️ Aucune donnée à écrire.")
            return
        clean_data = [{k.strip(): v for k, v in row.items()} for row in extracted_data]
        CSVManager.write_csv(output_csv_path, clean_data)
        print(f"✅ CSV généré : {output_csv_path}")
