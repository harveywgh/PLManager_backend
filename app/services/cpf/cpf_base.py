import os
import pandas as pd
from ...utils.cpf.cpf_container_manager import CpfContainerManager
from ...utils.cpf.cpf_df_manager import CpfDataframeManager
from ...utils.cpf.cpf_loader import CpfLoader
from ...utils.csv_manager import CSVManager

class BaseCpfService:
    def __init__(self, pl_column_mapping):
        self.pl_column_mapping = pl_column_mapping

    def process_file(self, file_path, output_dir):
        df = self._prepare_dataframe(file_path)
        containers = self._group_containers(df)

        generated_files = []
        for index, container in enumerate(containers, start=1):
            container_df = self._filter_container(df, container)
            output_csv = self._process_container(container_df, output_dir, index, len(containers) == 1)
            if output_csv:
                generated_files.append(output_csv)

        print(f"✅ Fichiers générés : {generated_files}")
        return generated_files

    def _prepare_dataframe(self, file_path):
        df = CpfLoader.load_excel_file(file_path)
        CpfDataframeManager.normalize_columns(df)
        CpfDataframeManager.validate_columns(df, self.pl_column_mapping)
        CpfDataframeManager.add_missing_columns(df, self.pl_column_mapping)
        df = CpfDataframeManager.regroup_by_pallet_and_caliber(df)
        return df


    def _group_containers(self, df):
        return CpfContainerManager.group_by_container(df)

    def _filter_container(self, df, container):
        return CpfContainerManager.filter_by_container(df, "CONTAINER NUMBER", container)

    def _process_container(self, df, output_dir, index, single_container):
        extracted_data = self._extract_data(df)
        ref = self._get_exporter_ref(df)
        ref_full = ref if single_container else f"{ref}_{index}"

        for row in extracted_data:
            row["Exporter Ref"] = ref_full

        path = self._generate_csv_filename(output_dir, ref, index)
        self._write_to_csv(path, extracted_data)
        return path

    def _extract_data(self, df):
        raise NotImplementedError()

    def _get_exporter_ref(self, df):
        ref = df.get("INVOICE NUMBER", pd.Series()).dropna()
        if not ref.empty:
            return ref.iloc[0]
        cont = df.get("CONTAINER NUMBER", pd.Series()).dropna()
        return cont.iloc[0] if not cont.empty else "Unknown"

    def _generate_csv_filename(self, output_dir, ref, index):
        fournisseur = getattr(self, "csv_settings", {}).get("Fournisseur", "CPF")
        folder = os.path.join(output_dir, fournisseur)
        os.makedirs(folder, exist_ok=True)
        return os.path.join(folder, f"PL_{ref}_{index}.csv")

    def _write_to_csv(self, path, data):
        if not data:
            print("⚠️ Aucune donnée à écrire.")
            return
        clean = [{k.strip(): v for k, v in row.items()} for row in data]
        CSVManager.write_csv(path, clean)
        print(f"✅ CSV CPF généré : {path}")
