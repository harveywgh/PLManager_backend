# shalimar_service.py
import os
import pandas as pd
from .shalimar_base import BaseShalimarService
from ...utils.shalimar.shalimar_calculations import ShalimarCalculations


class ShalimarService(BaseShalimarService):
    def __init__(self):
        pl_column_mapping = self._initialize_column_mapping()
        super().__init__(pl_column_mapping)
        self.csv_settings = {}

    def _initialize_column_mapping(self):
        return {
            "Pallet no": ["Pallet Number"],
            "Exporter Name": ["Exporter Name"],
            "Shipping line": [""],
            "Vessel Name": ["Vessel Name"],
            "Port of departure": ["Port of departure"],
            "Port of arrival": ["Port of arrival"],
            "Packing house departure date": ["Packing house departure (dd/mm/yyyy)"],
            "ETA": ["ETA"],
            "Exporter Ref": ["Exporter Ref"],
            "Seal No": ["Seal No"],
            "Container No": ["Container No"],
            "Species": ["Product"],
            "Variety": ["Variety"],
            "Size_caliber_count": ["Size/Caliber"],
            "Nb of fruits per box": ["Nb of fruits per box"],
            "Class": ["CATEGORY"],
            "Brand": ["Brand"],
            "Country of origin": ["Country of origin"],
            "Packaging": ["Packaging"],
            "Packaging type": ["Packaging type"],
            "Box tare (kg)": ["Box tare (kg)"],
            "Net weight per box (kg)": ["Weight per box"],
            "Net weight per pallet (kg)": ["Net weight"],
            "Cartons per pallet": ["Boxes per pallet"],
            "Nb of pallets": ["Nb of pallets"],
            "Lot no": ["LOT N°"],
            "Date of packaging": ["Packaging date (dd/mm/yyyy)"],
            "PACKING HOUSE/PRODUCER": ["Packinghouse code"],
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

            elif csv_field == "Certifications":
                record["Certifications"] = "GG/SMETA"

            elif csv_field == "Exporter Name":
                record["Exporter Name"] = "SHALIMAR"

            else:
                value = self._get_field_value(row, excel_columns)

                if csv_field in date_fields:
                    value = self._process_date_field(value)

                # Normalisation du poids unitaire pour l’ERP
                if csv_field == "Net weight per box (kg)":
                    # Choix du format: "2dec" retourne "4.00", "int" retourne "4"
                    value = ShalimarCalculations.normalize_weight(value, return_format="2dec")

                record[csv_field] = value if value not in [None, "Non spécifié"] else ""

        # Calcul automatique du nombre de fruits par carton avec le poids normalisé
        caliber = record.get("Size_caliber_count", "")
        weight_for_calc = record.get("Net weight per box (kg)", "")
        nb_fruits = ShalimarCalculations.nb_of_fruits_per_box(caliber, weight_for_calc)
        if nb_fruits != "":
            record["Nb of fruits per box"] = nb_fruits

        # Remplir automatiquement Packaging type si vide, basé sur le poids normalisé
        if not record.get("Packaging type"):
            w_num = ShalimarCalculations._extract_numeric(weight_for_calc)
            record["Packaging type"] = f"COLIS {int(w_num)}KG" if w_num is not None else "COLIS KG"

        return record

    def _get_field_value(self, row, excel_columns):
        for col in excel_columns:
            if col in row.index and pd.notna(row[col]) and str(row[col]).strip() != "":
                return row[col]
        if len(excel_columns) == 1:
            fallback_col = excel_columns[0]
            if fallback_col in row.index:
                return row[fallback_col]
        return ""

    def _process_date_field(self, value):
        try:
            if pd.notnull(value) and value != "":
                return pd.to_datetime(value, errors='coerce').strftime("%d/%m/%Y")
        except Exception as e:
            print(f"⚠️ Erreur conversion date: {e}")
        return ""
