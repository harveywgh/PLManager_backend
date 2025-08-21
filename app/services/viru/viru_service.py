import os
import pandas as pd
import datetime
from .viru_base import BaseViruService
from ...utils.viru.viru_calculations import ViruCalculations
from ...utils.viru.viru_df_manager import ViruDataframeManager


class ViruService(BaseViruService):
    def __init__(self):
        pl_column_mapping = self._initialize_column_mapping()
        super().__init__(pl_column_mapping)
        self.csv_settings = {}

    def _initialize_column_mapping(self):
        return {
            "Pallet no": ["Supplier pallet number"],
            "Exporter Name": ["Exporter Name"],
            "Shipping line": ["Shipping line"],
            "Vessel Name": ["Vessel Name"],
            "Port of departure": ["Port of departure"],
            "Port of arrival": ["Port of arrival"],
            "Packing house departure date": [],
            "ETA": [],
            "Exporter Ref": [],
            "Seal No": [],
            "Container No": ["Container No"],
            "Species": ["Product"],
            "Variety": ["Variety"],
            "Size_caliber_count": ["Size"],
            "Nb of fruits per box": [],
            "Class": ["Class"],
            "Brand": ["Brand name"],
            "Country of origin": [],
            "Packaging": [""],
            "Packaging type": ["Presentation"],
            "Box tare (kg)": [],
            "Net weight per box (kg)": ["Net weight box(kg)"],
            "Net weight per pallet (kg)": [],
            "Cartons per pallet": ["Number of boxes"],
            "Nb of pallets": [],
            "Lot no": [],
            "Date of packaging": ["Packing date"],
            "PACKING HOUSE/PRODUCER": [],
            "Producer": [],
            "ETD": [],
            "Temperature recorder no": ["Temptale number"],
            "Date of harvesting": ["Harvest date"],
            "Plot": [],
            "Certifications": [],
            "GGN": ["GGN"],
            "COC": [],
            "Certified GG/COC": [],
            "Forwarder at destination": [],
        }

    def apply_csv_settings(self, settings):
        self.csv_settings = settings
        print("📌 Paramètres CSV reçus APRES TRANSMISSION:", settings)

        mandatory_fields = ["country_of_origin", "forwarder"]
        for field in mandatory_fields:
            if field not in settings or not settings[field]:
                raise ValueError(f"⚠️ Champ obligatoire manquant: {field}")

        self.csv_settings["Country of origin"] = settings.get("country_of_origin", "Non spécifié")
        self.csv_settings["Forwarder at destination"] = settings.get("forwarder", "Non spécifié")
        self.csv_settings["Importer"] = settings.get("importer", "Non spécifié")
        self.csv_settings["Archive"] = settings.get("archive", "Non")

    def _extract_data(self, container_df):
        # Étape 1 : regrouper les palettes mixtes par numéro + calibre
        grouped_df = ViruDataframeManager.regroup_by_pallet_and_caliber(container_df)

        # Étape 2 : extraire les données ligne par ligne
        extracted_data = []
        for _, row in grouped_df.iterrows():
            extracted_data.append(self._extract_row_data(row, grouped_df))
        return extracted_data


    def _extract_row_data(self, row, df):
        record = {}
        date_fields = ["ETA", "ETD", "Packing house departure date", "Date of packaging", "Date of harvesting"]

        for csv_field, excel_columns in self.pl_column_mapping.items():
            if csv_field in self.csv_settings and self.csv_settings[csv_field] is not None:
                value = self.csv_settings[csv_field]
            elif csv_field == "Certifications":
                value = "GG/SMETA"
            else:
                value = self._get_field_value(row, excel_columns)
                if csv_field == "ETA":
                    if value in ["", None]:
                        value = datetime.datetime.now().strftime("%d/%m/%Y")
                    else:
                        value = self._process_date_field(value)

                elif csv_field in date_fields:
                    value = self._process_date_field(value)

            record[csv_field] = value if value not in [None, "Non spécifié"] else ""

        # 🔹 Calculs complémentaires
        caliber = self._get_field_value(row, ["Size"])
        weight = self._get_field_value(row, ["Net weight box(kg)"])
        cartons = self._get_field_value(row, ["Number of boxes"])

        record["Nb of fruits per box"] = ViruCalculations.nb_of_fruits_per_box(caliber, weight)
        record["Nb of pallets"] = self._get_field_value(row, ["Nb of pallets"])
        record["Net weight per pallet (kg)"] = ViruCalculations.net_weight_per_pallet(cartons, weight)
        record["Box tare (kg)"] = ViruCalculations.box_tare(weight)

        return record


    def _get_field_value(self, row, excel_columns):
        for col in excel_columns:
            if col in row.index and pd.notna(row[col]):
                return row[col]
        return ""

    def _process_date_field(self, value):
        try:
            if pd.notnull(value) and value != "":
                return pd.to_datetime(value, errors='coerce').strftime("%d/%m/%Y")
        except Exception as e:
            print(f"⚠️ Erreur conversion date: {e}")
        return ""


