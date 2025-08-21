import os
import pandas as pd
from .ingophase_base import BaseIngophaseService
from ...utils.ingophase.ingophase_calculations import IngophaseCalculations
import datetime


class IngophaseService(BaseIngophaseService):
    def __init__(self):
        pl_column_mapping = self._initialize_column_mapping()
        super().__init__(pl_column_mapping)
        self.csv_settings = {}

    def _initialize_column_mapping(self):
        return {
            "Pallet no": ["Pallet_Id"],
            "Exporter Name": ["Cust_Name"],
            "Shipping line": [""], 
            "Vessel Name": ["Vessel_Name"],
            "Port of departure": [""],
            "Port of arrival": ["Port"],
            "Packing house departure date": [""],
            "ETA": [""],
            "Exporter Ref": ["Load_Ref"],
            "Seal No": [""],
            "Container No": [""],
            "Species": ["Comm"],
            "Variety": ["Variety"],
            "Size_caliber_count": ["Count"],
            "Nb of fruits per box": [],
            "Class": ["Grade"],
            "Brand": ["Mark"],
            "Country of origin": ["Country of origin"],
            "Packaging": [""],
            "Packaging type": ["Pack"],
            "Box tare (kg)": [""],
            "Net weight per box (kg)": ["Unit_Nett"],
            "Net weight per pallet (kg)": ["PO_NettM"],
            "Cartons per pallet": ["Cartons"],
            "Nb of pallets": ["Plts"],
            "Lot no": ["LotNumber"],
            "Date of packaging": [""],
            "PACKING HOUSE/PRODUCER": ["Orig_Depot"],
            "Producer": [""],
            "ETD": [""],
            "Temperature recorder no": [""],
            "Date of harvesting": [""],
            "Plot": [""],
            "Certifications": [""],
            "GGN": [""],
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
        self.csv_settings["Exporter Name"] = settings.get("exporter_name", "Ingophase FRUIT")

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
            elif csv_field == "Port of departure":
                record[csv_field] = "DURBAN"
            elif csv_field == "Certifications":
                record[csv_field] = "GG/SMETA"
            elif csv_field == "ETA":
                record[csv_field] = datetime.datetime.now().strftime("%d/%m/%Y")
            elif csv_field == "Brand":
                record[csv_field] = self.csv_settings.get("Fournisseur", "Générique")
            else:
                value = self._get_field_value(row, excel_columns)
                if csv_field in date_fields:
                    value = self._process_date_field(value)
                record[csv_field] = value if value not in [None, "Non spécifié"] else ""

        # ✅ Toujours recalculer Net weight per box (kg) depuis Mass et CtnQty
        mass = self._get_field_value(row, ["Net weight per pallet (kg)", "PO_NettM"])
        cartons = self._get_field_value(row, ["Cartons per pallet", "Cartons"])
        record["Net weight per box (kg)"] = IngophaseCalculations.net_weight_per_box(mass, cartons)

        # ✅ Tare recalculée selon le nombre de cartons
        cartons = self._get_field_value(row, self.pl_column_mapping.get("Cartons per pallet", []))
        record["Box tare (kg)"] = IngophaseCalculations.box_tare(cartons)

        # ✅ Nombre de fruits par boîte selon le poids (recalculé), le calibre et l'espèce
        caliber = self._get_field_value(row, self.pl_column_mapping.get("Size_caliber_count", []))
        species = self._get_field_value(row, self.pl_column_mapping.get("Species", []))
        record["Nb of fruits per box"] = IngophaseCalculations.nb_of_fruits_per_box(caliber, species)

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
