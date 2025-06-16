from .alg_base import BaseAlgService
from ...utils.alg.alg_calculation import AlgCalculations
import pandas as pd

class AlgService(BaseAlgService):
    def __init__(self):
        pl_column_mapping = self._initialize_column_mapping()
        super().__init__(pl_column_mapping)
        self.csv_settings = {}

    def _initialize_column_mapping(self):
        return {
            "Pallet no": ["Barcode"],
            "Exporter Name": [""],
            "Shipping line": ["Shipping No"],
            "Vessel Name": ["Vessel Name"],
            "Port of departure": ["Port Of Loading"],
            "Port of arrival": ["Port of Discharge"],
            "Packing house departure date": ["Orig Inspection Date"],
            "ETA": ["ETA"],
            "Exporter Ref": ["Invoice ID"],
            "Seal No": ["Seal Number"],
            "Container No": ["Container No"],
            "Species": ["Commodity Code"],
            "Variety": ["Variety Code"],
            "Size_caliber_count": ["Count Code"],
            "Nb of fruits per box": [""],
            "Class": ["Grade Code"],
            "Brand": ["Mark Code"],
            "Country of origin": [""],
            "Packaging": [""],
            "Packaging type": ["Pack Code"],
            "Box tare (kg)": [""],
            "Net weight per box (kg)": [""],
            "Net weight per pallet (kg)": ["Nett Weight"],
            "Cartons per pallet": ["No Cartons"],
            "Nb of pallets": ["Pallet Size"],
            "Lot no": ["Consec No"],
            "Date of packaging": [""],
            "PACKING HOUSE/PRODUCER": ["PHC"],
            "Producer": ["Farm Number"],
            "ETD": ["ETD"],
            "Temperature recorder no": ["Temp Tail"],
            "Date of harvesting": [""],
            "Plot": ["Orchard"],
            "Certifications": ["Phyto Verification"],
            "GGN": ["Global Gap Number"],
            "COC": ["Inventory Code"],
            "Certified GG/COC": ["Global Gap Number"],
            "Forwarder at destination": [""],
        }

    def apply_csv_settings(self, settings):
        self.csv_settings = settings
        print("📌 Paramètres CSV reçus APRES TRANSMISSION :", settings)
        
        if "importer" not in settings:
            print("❌ ERREUR : Le champ 'importer' est manquant dans les paramètres reçus !")
        else:
            print(f"✅ Importateur reçu : {settings['importer']}")

        mandatory_fields = ["country_of_origin", "forwarder"]
        for field in mandatory_fields:
            if field not in self.csv_settings or not self.csv_settings[field]:
                raise ValueError(f"⚠️ Le champ obligatoire '{field}' est manquant ou vide !")

        self.csv_settings["Country of origin"] = self.csv_settings.pop("country_of_origin", "Non spécifié")
        self.csv_settings["Forwarder at destination"] = self.csv_settings.pop("forwarder", "Non spécifié")
        self.csv_settings["Importer"] = self.csv_settings.pop("importer", "Non spécifié")
        self.csv_settings["Archive"] = self.csv_settings.pop("archive", "Non")

        optional_fields = ["packaging", "packaging_type", "custom1", "custom2"]
        for field in optional_fields:
            self.csv_settings[field] = self.csv_settings.get(field, None)

    def _extract_data(self, container_df):
        extracted_data = []
        for _, row in container_df.iterrows():
            record = self._extract_row_data(row)
            extracted_data.append(record)
        return extracted_data

    def _extract_row_data(self, row):
        record = {}
        date_fields = ["ETA", "ETD", "Packing house departure date", "Date of packaging", "Date of harvesting"]

        for csv_field, excel_columns in self.pl_column_mapping.items():
            if csv_field in self.csv_settings and self.csv_settings[csv_field] is not None:
                print(f"✅ Remplacement {csv_field} → {self.csv_settings[csv_field]}")
                record[csv_field] = self.csv_settings[csv_field]
            else:
                if csv_field == "Exporter Name":
                    record[csv_field] = "ALG"

                elif csv_field == "Box tare (kg)":
                    record[csv_field] = AlgCalculations.box_tare(
                        row.get("Gross Weight", 0),
                        row.get("Nett Weight", 0),
                        row.get("No Cartons", 0)
                    )

                elif csv_field == "Net weight per box (kg)":
                    record[csv_field] = AlgCalculations.net_weight_per_box(
                        row.get("Nett Weight", 0),
                        row.get("No Cartons", 0)
                    )

                elif csv_field == "Nb of fruits per box":
                    species = row.get("Commodity Code", "").strip()
                    caliber = row.get("Count Code", "")
                    if species == "SC":
                        record[csv_field] = AlgCalculations.nb_fruits_mandarines(caliber)
                    else:
                        record[csv_field] = caliber

                elif csv_field in date_fields:
                    record[csv_field] = self._process_date_field(row, excel_columns)

                else:
                    record[csv_field] = self._get_field_value(row, excel_columns)

            # Normalisation vide
            if record[csv_field] in [None, "", "Non spécifié"]:
                record[csv_field] = ""

        print("📌 Données extraites après correction :", record)
        return record



    def _get_field_value(self, row, excel_columns):
        for excel_column in excel_columns:
            if excel_column in row.index and pd.notna(row[excel_column]):
                return row[excel_column]
        return ""

    def _process_date_field(self, row, excel_columns):
        for excel_column in excel_columns:
            value = row.get(excel_column, "")
            try:
                if pd.notnull(value) and value != "":
                    return pd.to_datetime(value, errors='coerce').strftime("%d/%m/%Y")
            except Exception as e:
                print(f"⚠️ Erreur conversion date `{excel_column}`: {e}")
        return ""
