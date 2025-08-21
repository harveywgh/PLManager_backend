import os
import pandas as pd
from .hnp_base import BaseHnpService
from ...utils.hnp.hnp_calculations import HnpCalculations


class HnpService(BaseHnpService):
    def __init__(self):
        pl_column_mapping = self._initialize_column_mapping()
        super().__init__(pl_column_mapping)
        self.csv_settings = {}

    def _initialize_column_mapping(self):
        return {
            "Pallet no": ["Pallet Ref. Nr."],
            "Exporter Name": ["Exporter Name"],
            "Shipping line": ["Shipping line"],
            "Vessel Name": ["Vessel"],
            "Port of departure": ["Port of departure"],
            "Port of arrival": ["Port of arrival"],
            "Packing house departure date": ["Packing house departure (dd/mm/yyyy)"],
            "ETA": ["ETA (dd/mm/yyyy)"],
            "Exporter Ref": ["ShipAdv"],
            "Seal No": ["Cod. Tracabilidad"],
            "Container No": ["Container"],
            "Species": ["Comm"],
            "Variety": ["Var"],
            "Size_caliber_count": ["Size"],
            "Nb of fruits per box": ["Size"],
            "Class": ["Grade"],
            "Brand": ["Mark"],
            "Country of origin": ["Country of origin"],
            "Packaging": ["Packaging"],
            "Packaging type": ["Pack Type"],
            "Box tare (kg)": ["Box tare (kg)"],
            "Net weight per box (kg)": ["Net weight per box (kg)"],
            "Net weight per pallet (kg)": ["Net weight per pallet (kg)"],
            "Cartons per pallet": ["Quantity"],
            "Nb of pallets": ["Pallet Size"],
            "Lot no": ["Lot n°"],
            "Date of packaging": ["Packaging date (dd/mm/yyyy)"],
            "PACKING HOUSE/PRODUCER": ["Farm"],
            "Producer": ["Producer name"],
            "ETD": ["ETD (dd/mm/yyyy)"],
            "Temperature recorder no": ["Temp recorder"],
            "Date of harvesting": ["Harvest date \n (dd/mm/yyyy)"],
            "Plot": ["Field"],
            "Certifications": ["Certifications"],
            "GGN": ["GGN"],
            "COC": ["COC n°"],
            "Certified GG/COC": ["Global G.A.P. certified"],
            "Forwarder at destination": ["Forwarder at destination"],
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
        extracted_data = []
        for _, row in container_df.iterrows():
            extracted_data.append(self._extract_row_data(row, container_df))  
        return extracted_data


    def _extract_row_data(self, row, df):
        record = {}
        date_fields = ["ETA", "ETD", "Packing house departure date", "Date of packaging", "Date of harvesting"]

        for csv_field, excel_columns in self.pl_column_mapping.items():
            if csv_field in self.csv_settings and self.csv_settings[csv_field] is not None:
                record[csv_field] = self.csv_settings[csv_field]
            elif csv_field == "Certifications":
                value = self._get_field_value(row, excel_columns)
                record[csv_field] = value if value not in [None, "", "Non spécifié"] else "GG/SMETA"
            elif csv_field == "Exporter Name":
                value = self._get_field_value(row, excel_columns)
                record[csv_field] = value if value not in [None, "", "Non spécifié"] else "HNP MARKETING"
            elif csv_field == "Port of departure":
                value = self._get_field_value(row, excel_columns)
                record[csv_field] = value if value not in [None, "", "Non spécifié"] else "DURBAN"
            elif csv_field == "Port of arrival":
                value = self._get_field_value(row, excel_columns)
                record[csv_field] = value if value not in [None, "", "Non spécifié"] else "ROTTERDAM"
            elif csv_field == "Net weight per box (kg)":
                value = self._get_field_value(row, excel_columns)
                record[csv_field] = value if value not in [None, "", "0.0"] else "0.0"
            else:
                value = self._get_field_value(row, excel_columns)
                if csv_field in date_fields:
                    value = self._process_date_field(value)
                record[csv_field] = value if value not in [None, "Non spécifié"] else ""
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
