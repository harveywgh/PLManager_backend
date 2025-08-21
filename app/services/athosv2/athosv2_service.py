import os
import pandas as pd
from .athosv2_base import BaseAthosV2Service
from ...utils.athosv2.athosv2_calculations import AthosV2Calculations


class AthosV2Service(BaseAthosV2Service):
    def __init__(self):
        pl_column_mapping = self._initialize_column_mapping()
        super().__init__(pl_column_mapping)
        self.csv_settings = {}

    def _initialize_column_mapping(self):
        return {
            "Pallet no": ["Pallet Number"],
            "Exporter Name": ["Exporter Name"],
            "Shipping line": [""],
            "Vessel Name": ["Vessel name"],
            "Port of departure": ["Port of departure"],
            "Port of arrival": ["Port of arrival"],
            "Packing house departure date": ["Packing house departure (dd/mm/yyyy)"],
            "ETA": ["ETA"],
            "Exporter Ref": ["Exporter Ref"],
            "Seal No": ["Cod. Tracabilidad"],
            "Container No": ["Container No"],
            "Species": ["TYPE OF FRUIT"],
            "Variety": ["VARIETY"],
            "Size_caliber_count": ["Size/Caliber"],
            "Nb of fruits per box": ["Nb of fruits per box"],
            "Class": ["CATEGORY"],
            "Brand": ["BRAND"],
            "Country of origin": ["Country of origin"],
            "Packaging": ["Packaging"],
            "Packaging type": ["Packaging type"],
            "Box tare (kg)": ["Box tare (kg)"],
            "Net weight per box (kg)": ["WEIGHT (KG)"],
            "Net weight per pallet (kg)": ["NET WEIGHT (KG)"],
            "Cartons per pallet": ["BOXES"],
            "Nb of pallets": ["Nb of pallets"],
            "Lot no": ["LOT N°"],
            "Date of packaging": ["Packaging date (dd/mm/yyyy)"],
            "PACKING HOUSE/PRODUCER": ["PACKINGHOUSE CODE"],
            "Producer": ["Producer name"],
            "ETD": ["ETD"],
            "Temperature recorder no": ["Temperature recorder n°"],
            "Date of harvesting": ["Harvest date \n (dd/mm/yyyy)"],
            "Plot": ["COD. PLACE OF PRODUCTION"],
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

            elif csv_field == "Packaging type":
                weight = self._get_field_value(row, ["WEIGHT (KG)"])
                try:
                    weight_float = float(str(weight).replace(",", "."))
                    value = f"COLIS {int(weight_float)}KG"
                except Exception:
                    value = "COLIS KG"
                record[csv_field] = value
            elif csv_field == "Port of departure":
                record[csv_field] = "CALLAO"
            elif csv_field == "Certifications":
                record[csv_field] = "GG/GRASP"
            else:
                value = self._get_field_value(row, excel_columns)
                if csv_field in date_fields:
                    value = self._process_date_field(value)
                record[csv_field] = value if value not in [None, "Non spécifié"] else ""
                
        try:
            weight_float = float(weight)
            box_tare = 0.50 if weight_float == 4 else 0.40
        except Exception:
            box_tare = 0.6
        record["Box tare (kg)"] = box_tare

        # Calcul Nb of fruits per box
        caliber = self._get_field_value(row, ["Size/Caliber"])
        weight = self._get_field_value(row, ["WEIGHT (KG)"])
        record["Nb of fruits per box"] = AthosV2Calculations.nb_of_fruits_per_box(caliber, weight)

        # Nb of pallets (non recalculé après regroupement)
        record["Nb of pallets"] = self._get_field_value(row, ["Nb of pallets"])

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
