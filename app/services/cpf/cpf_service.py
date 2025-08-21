import os
import pandas as pd
from .cpf_base import BaseCpfService
from ...utils.cpf.cpf_calculations import CpfCalculations

class CpfService(BaseCpfService):
    def __init__(self):
        pl_column_mapping = self._initialize_column_mapping()
        super().__init__(pl_column_mapping)
        self.csv_settings = {}

    def _initialize_column_mapping(self):
        return {
            "Pallet no": ["PALLET"],
            "Exporter Name": ["EXPORTER"],
            "Shipping line": ["SHIPPING LINE"],
            "Vessel Name": ["VESSEL"],
            "Port of departure": ["LOADING PORT"],
            "Port of arrival": ["PORT OF DISCHARGE"],
            "Packing house departure date": ["SHIPMENT DAY"],
            "ETA": ["ETA"],
            "Exporter Ref": ["INVOICE NUMBER"],
            "Seal No": ["TRACEABILITY"],
            "Container No": ["CONTAINER NUMBER"],
            "Species": ["PRODUCT"],
            "Variety": ["VARIETY"],
            "Size_caliber_count": ["SIZE"],
            "Nb of fruits per box": [],  # calculé
            "Class": [],
            "Brand": ["LABEL"],  # non dispo
            "Country of origin": [],  # via paramètre
            "Packaging": ["MATERIAL"],
            "Packaging type": ["MATERIAL"],
            "Box tare (kg)": [],  # à fixer si connu, sinon calcul manuel
            "Net weight per box (kg)": ["NET WEIGHT"],  # à fixer ou calculable
            "Net weight per pallet (kg)": [""],
            "Cartons per pallet": ["CASES"],
            "Nb of pallets": [],  # calculé
            "Lot no": ["TRACEABILITY"],
            "Date of packaging": ["DATE PACKING"],
            "PACKING HOUSE/PRODUCER": ["PACKING HOUSE NAME"],
            "Producer": ["GROWER NAME"],
            "ETD": ["SHIPMENT DAY"],
            "Temperature recorder no": [],  # non dispo
            "Date of harvesting": [],  # non dispo
            "Plot": ["GROWER CODE"],
            "Certifications": [],  # potentiellement GGN + FDA combinés
            "GGN": ["GGN NUMBER"],
            "COC": [],
            "Certified GG/COC": ["GGN VALIDITY"],
            "Forwarder at destination": [],  # via paramètre
        }

    def apply_csv_settings(self, settings):
        self.csv_settings = settings
        print("📌 Paramètres CSV CPF :", settings)

        self.csv_settings["Country of origin"] = settings.get("country_of_origin", "PE")
        self.csv_settings["Forwarder at destination"] = settings.get("forwarder", "")
        self.csv_settings["Importer"] = settings.get("importer", "")
        self.csv_settings["Archive"] = settings.get("archive", "")
        self.csv_settings["Fournisseur"] = settings.get("Fournisseur", "CPF")

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

            elif csv_field == "Class":
                record[csv_field] = 1
            elif csv_field == "Certifications":
                record[csv_field] = "GG/SMETA"

            elif csv_field == "Container No":
                value = self._get_field_value(row, excel_columns)
                if value:
                    value = str(value).replace("-", "").strip()
                record[csv_field] = value

            elif csv_field == "Packaging type":
                weight = self._get_field_value(row, ["Net weight per box (kg)"])
                try:
                    weight_float = float(weight)
                    if weight_float == 10:
                        value = f"Colis {int(weight_float)}KG Plastiques"
                    elif weight_float == 4:
                        value = f"Colis {int(weight_float)}KG"
                    else:
                        value = "Colis KG"
                except Exception:
                    value = "Colis KG"
                record[csv_field] = value

            else:
                value = self._get_field_value(row, excel_columns)
                if csv_field in date_fields:
                    value = self._process_date_field(value)
                record[csv_field] = value if value not in [None, "Non spécifié"] else ""

        net_per_box = self._get_field_value(row, ["NET WEIGHT"])
        try:
            weight_float = float(net_per_box)
            box_tare = 0.32 if weight_float == 4 else 0.31
        except Exception:
            box_tare = 0.6
        record["Box tare (kg)"] = box_tare

        # ✅ Nb de fruits par boîte
        caliber = self._get_field_value(row, ["SIZE"])
        record["Nb of fruits per box"] = CpfCalculations.nb_of_fruits_per_box(caliber, net_per_box)

        # ✅ Net weight per pallet
        cartons = self._get_field_value(row, ["CASES"])
        record["Net weight per pallet (kg)"] = CpfCalculations.net_weight_per_pallet(net_per_box, cartons)

        # ✅ Nb de palettes
        pallet = self._get_field_value(row, ["PALLET"])
        existing = self._get_field_value(row, ["Nb of pallets"])
        record["Nb of pallets"] = CpfCalculations.nb_of_pallets_by_palletnum(pallet, cartons, df, current_value=existing)

        return record




    def _get_field_value(self, row, excel_columns):
        for col in excel_columns:
            if col in row.index and pd.notna(row[col]):
                return row[col]
        return ""

    def _process_date_field(self, value):
        try:
            if pd.notnull(value) and value != "":
                return pd.to_datetime(value, dayfirst=True, errors='coerce').strftime("%d/%m/%Y")
        except Exception as e:
            print(f"⚠️ Erreur conversion date: {e}")
        return ""
