import os
import pandas as pd
from ...utils.csv_manager import CSVManager
from ...utils.angon.angon_loader import AngonLoader
from ...utils.angon.angon_df_manager import AngonDataframeManager
from ...utils.angon.angon_container_manager import AngonContainerManager

class BaseAngonService:
    def __init__(self, pl_column_mapping):
        self.pl_column_mapping = pl_column_mapping

    def process_file(self, file_path, output_dir):
        df = self._prepare_dataframe(file_path)
        containers = self._group_containers(df)

        generated_files = []
        for index, container in enumerate(containers, start=1):
            container_df = self._filter_container(df, container)
            output_path = self._process_container(container_df, output_dir, index, len(containers) == 1)
            if output_path:
                generated_files.append(output_path)

        print(f"✅ Fichiers générés = {generated_files}")
        return generated_files

    def _prepare_dataframe(self, file_path):
        df = AngonLoader.load_excel_file(file_path)
        AngonDataframeManager.normalize_columns(df)
        AngonDataframeManager.validate_columns(df, self.pl_column_mapping)
        AngonDataframeManager.add_missing_columns(df, self.pl_column_mapping)
        return df

    def _group_containers(self, df):
        return AngonContainerManager.group_by_container(df)

    def _filter_container(self, df, container):
        return AngonContainerManager.filter_by_container(df, "Container", container)

    def _process_container(self, df, output_dir, index, single_container):
        extracted_data = self._extract_data(df)
        exporter_ref = self._get_exporter_ref(df)
        full_ref = exporter_ref if single_container else f"{exporter_ref}_{index}"

        for row in extracted_data:
            row["Exporter Ref"] = full_ref

        output_path = self._generate_csv_filename(output_dir, exporter_ref, index)
        self._write_to_csv(output_path, extracted_data)
        return output_path

    def _extract_data(self, df):
        raise NotImplementedError()

    def _get_exporter_ref(self, df):
        refs = df.get("sender_ref", pd.Series()).dropna()
        if refs.empty:
            print("⚠️ Aucun 'sender_ref' trouvé, on utilise 'Container'")
            return df.get("Container", pd.Series()).dropna().iloc[0] if "Container" in df.columns else "Unknown"
        return refs.iloc[0]

    def _generate_csv_filename(self, output_dir, exporter_ref, index):
        subfolder = os.path.join(output_dir, "Angon")
        os.makedirs(subfolder, exist_ok=True)
        return os.path.join(subfolder, f"PL_{exporter_ref}_{index}.csv")

    def _write_to_csv(self, path, data):
        if not data:
            print("⚠️ Aucune donnée à écrire.")
            return
        clean = [{k.strip(): v for k, v in row.items()} for row in data]
        CSVManager.write_csv(path, clean)
        print(f"✅ CSV généré : {path}")