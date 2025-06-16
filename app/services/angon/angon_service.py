
import os
import pandas as pd
from .angon_base import BaseAngonService
from ...utils.angon.angon_calculations import AngonCalculations


class AngonService(BaseAngonService):
    def __init__(self):
        pl_column_mapping = self._initialize_column_mapping()
        super().__init__(pl_column_mapping)
        self.csv_settings = {}

    def _initialize_column_mapping(self):
        return {
            "Pallet no": ["Pallet"],  
            "Exporter Name": ["sender_ref"],
            "Shipping line": ["Shipping Line"],
            "Vessel Name": ["Vessel"],
            "Port of departure": ["POL"],
            "Port of arrival": ["POD"],
            "Packing house departure date": ["Packing date"],
            "ETA": ["ETA"],
            "Exporter Ref": ["sender_ref"],
            "Seal No": ["Seal"],
            "Container No": ["Container"],
            "Species": ["Commodity"],
            "Variety": ["Variety"],
            "Size_caliber_count": ["Count"],
            "Nb of fruits per box": ["Nb of fruits per box"],  # À calculer
            "Class": ["Grade"],
            "Brand": ["Mark"],
            "Country of origin": ["Country"],
            "Packaging": ["Carton"],
            "Packaging type": ["Pack"],
            "Box tare (kg)": ["Box tare (kg)"],  # À vérifier si dispo ou fixe
            "Net weight per box (kg)": ["Net weight per box (kg)"],  # à ajouter si dispo
            "Net weight per pallet (kg)": ["Net weight per pallet (kg)"],  # à ajouter si dispo
            "Cartons per pallet": ["Carton"],
            "Nb of pallets": ["Nb of pallets"],
            "Lot no": ["Consignment No"],
            "Date of packaging": ["Packing date"],
            "PACKING HOUSE/PRODUCER": ["Farm"],
            "Producer": ["Inventory"],
            "ETD": ["ETD"],
            "Temperature recorder no": ["Recorder"],
            "Date of harvesting": ["Harvest date (dd/mm/yyyy)"],  # Peut être vide
            "Plot": ["Orchard"],
            "Certifications": ["Certifications"],  # Peut être vide
            "GGN": ["GGN (=GlobalGAP n°)"],        # Peut être vide
            "COC": ["COC n°"],                      # Peut être vide
            "Certified GG/COC": ["Certified GG/COC"],
            "Forwarder at destination": ["Forwarder at destination"],
        }

    def apply_csv_settings(self, settings):
        self.csv_settings = settings
        print("📌 Paramètres CSV reçus APRES TRANSMISSION:", settings)

        # Obligatoires
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

                # ➕ Gestion Box tare (kg)
                if csv_field == "Box tare (kg)":
                    if value in [None, "", "Non spécifié"]:
                        value = AngonCalculations.box_tare(value)
                record[csv_field] = value if value not in [None, "Non spécifié"] else ""

        # ➕ Calcul Nb of fruits per box (si vide ou non numérique)
        caliber = self._get_field_value(row, ["Count"])
        weight = self._get_field_value(row, ["Net weight per box (kg)"])
        existing = record.get("Nb of fruits per box", "")
        if not str(existing).isdigit():
            record["Nb of fruits per box"] = AngonCalculations.nb_of_fruits_per_box(caliber, weight)

        # ➕ Calcul Nb of pallets (si vide)
        pallet = self._get_field_value(row, ["Pallet"])
        boxes = self._get_field_value(row, ["Carton"])
        current_nb = self._get_field_value(row, ["Nb of pallets"])
        record["Nb of pallets"] = AngonCalculations.nb_of_pallets_by_palletnum(pallet, boxes, df, current_value=current_nb)

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
