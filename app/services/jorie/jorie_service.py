import os
import pandas as pd
from .jorie_base import BaseJorieService
from ...utils.jorie.jorie_calculations import JorieCalculations


class JorieService(BaseJorieService):
    def __init__(self):
        pl_column_mapping = self._initialize_column_mapping()
        super().__init__(pl_column_mapping)
        self.csv_settings = {}

    def _initialize_column_mapping(self):
        return {
            "Pallet no": ["PalletId"],
            "Exporter Name": ["Orgzn"],
            "Shipping line": ["ShipLine"], #
            "Vessel Name": ["LoadName"],
            "Port of departure": ["LLocationCode"],
            "Port of arrival": ["DestinationLocation"],
            "Packing house departure date": ["LDepartureDate"],
            "ETA": ["DArrivalTime"],
            "Exporter Ref": ["Voyage"],
            "Seal No": ["CTSealNumber"],
            "Container No": ["Container n°"],
            "Species": ["Commodity"],
            "Variety": ["Variety"],
            "Size_caliber_count": ["SizeCount"],
            "Nb of fruits per box": ["SizeCount"],
            "Class": ["Grade"],
            "Brand": ["Mark"],
            "Country of origin": ["Country of origin"],
            "Packaging": [""],
            "Packaging type": ["Pack"],
            "Box tare (kg)": ["Box tare (kg)"],
            "Net weight per box (kg)": [""],
            "Net weight per pallet (kg)": ["Mass"],
            "Cartons per pallet": ["CtnQty"],
            "Nb of pallets": ["PltQty"],
            "Lot no": [""],
            "Date of packaging": [""],
            "PACKING HOUSE/PRODUCER": ["PackhouseCode"],
            "Producer": [""],
            "ETD": ["LDepartureTime"],
            "Temperature recorder no": ["Temp"],
            "Date of harvesting": [""],
            "Plot": [""],
            "Certifications": [""],
            "GGN": ["GlobalGapNumber"],
            "COC": [""],
            "Certified GG/COC": [""],
            "Forwarder at destination": [""],
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
            else:
                value = self._get_field_value(row, excel_columns)
                if csv_field in date_fields:
                    value = self._process_date_field(value)
                record[csv_field] = value if value not in [None, "Non spécifié"] else ""

        # ➕ Calcul Net weight per box si manquant
        if not record.get("Net weight per box (kg)"):
            mass = self._get_field_value(row, ["Net weight per pallet (kg)", "Mass"])
            cartons = self._get_field_value(row, ["Cartons per pallet", "CtnQty"])
            record["Net weight per box (kg)"] = JorieCalculations.net_weight_per_box(mass, cartons)

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
