import os
import re
import pandas as pd
from .viru_base import BaseViruService
from ...utils.viru.viru_calculations import ViruCalculations


class ViruService(BaseViruService):
    def __init__(self):
        pl_column_mapping = self._initialize_column_mapping()
        super().__init__(pl_column_mapping)
        self.csv_settings = {}
        
    def _extract_data_from_sheet(self, raw_df):
        # Extraction des infos fixes
        exporter_ref = raw_df.iloc[4, 1]          # B5 (index 4,1)
        shipping_line = raw_df.iloc[7, 1]         # B8 (index 7,1)
        port_of_departure = raw_df.iloc[9, 1]     # B10 (index 9,1)
        port_of_arrival = raw_df.iloc[10, 1]      # B11 (index 10,1)
        vessel_name = raw_df.iloc[8, 1]           # B9 (index 8,1)
        eta = raw_df.iloc[4, 4]                    # E5 (index 4,4)
        container_no = raw_df.iloc[5, 1]           # B6 (index 5,1)

        data_df = raw_df.iloc[16:].copy()  
        data_df.columns = raw_df.iloc[14]  
        data_rows = []

        for _, row in data_df.iterrows():
            if pd.isna(row["Supplier pallet number"]):
                continue

            pallet_no = row["Supplier pallet number"]
            product = row["Product"]
            variety = row["Variety"]
            local_grower = row["Local grower name"]
            size = row["Size"]
            net_weight_box = row["Net weight box(kg)"]
            cartons_per_pallet = row["Number of boxes"]
            packing_date = row["Packing date"]
            harvest_date = row["Harvest date"]
            ggn = row.get("GGN", "")

            # Calcul du nombre de fruits par box
            nb_fruits = ViruCalculations.nb_of_fruits_per_box(size, net_weight_box)

            data_rows.append({
                "Pallet n°": pallet_no,
                "Container n°": container_no,
                "Exporter ref": exporter_ref,
                "Shipping line": shipping_line,
                "Port of departure": port_of_departure,
                "Port of arrival": port_of_arrival,
                "Vessel Name": vessel_name,
                "ETA": eta,
                "Exporter Name": "Viru",
                "Size": size,
                "Net weight per box (kg)": net_weight_box,
                "Cartons per pallet": cartons_per_pallet,
                "Nb of fruits per box": nb_fruits,
                "Variety": variety,
                "Packing date": packing_date,
                "Harvest date": harvest_date,
                "GGN": ggn,
                "Quantity per grower": cartons_per_pallet,
            })

        self.eta = eta
        self.exporter_name = "Viru"
        self.vessel_name = vessel_name
        self.container_no = container_no
        self.port_of_arrival = port_of_arrival
        self.shipping_line = shipping_line
        self.port_of_departure = port_of_departure
        self.exporter_ref = exporter_ref

        return pd.DataFrame(data_rows)




    def _initialize_column_mapping(self):
        return {
            "Pallet no": ["Supplier pallet number"],
            "Exporter Name": [],
            "Shipping line": [],
            "Vessel Name": [],
            "Port of departure": [],
            "Port of arrival": [],
            "Packing house departure date": [],
            "ETA": [],
            "Exporter Ref": [],
            "Seal No": [],
            "Container No": [],
            "Species": ["Product"],
            "Variety": ["Variety"],
            "Size_caliber_count": ["Size"],
            "Nb of fruits per box": [],  # 
            "Class": ["Class"],
            "Brand": ["Brand name"],
            "Country of origin": [],
            "Packaging": ["Presentation"],
            "Packaging type": [],
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
        extracted_data = []
        for _, row in container_df.iterrows():
            extracted_data.append(self._extract_row_data(row, container_df))  
        return extracted_data


    def _extract_row_data(self, row, df):
        record = {}
        date_fields = ["ETA", "ETD", "Packing house departure date", "Date of packaging", "Date of harvesting"]

        for csv_field, excel_columns in self.pl_column_mapping.items():
            if csv_field == "Country of origin" and "Country of origin" in self.csv_settings:
                value = self.csv_settings["Country of origin"]
            elif csv_field == "Forwarder at destination" and "Forwarder at destination" in self.csv_settings:
                value = self.csv_settings["Forwarder at destination"]
            elif csv_field == "Species":
                value = "Avocat"  # valeur par défaut
            elif csv_field == "Packaging type":
                weight = self._get_field_value(row, ["Net weight per box (kg)"])
                try:
                    weight_float = float(weight)
                except Exception:
                    weight_float = None

                if weight_float == 10:
                    value = f"BOX {int(weight_float)}KG plastique"
                elif weight_float == 4:
                    value = f"BOX {int(weight_float)}KG"
                else:
                    # Par défaut, on affiche quand même le poids
                    if weight_float is not None:
                        value = f"BOX {int(weight_float)}KG"
                    else:
                        value = "BOX KG"
            elif csv_field == "ETA":
                value = self._process_date_field(self.eta)
            elif csv_field == "ETD":
                value = self._process_date_field(self.etd)
            elif csv_field == "Exporter Name":
                value = self.exporter_name
            elif csv_field == "Vessel Name":
                value = self.vessel_name
            elif csv_field == "Port of departure":
                value = "MOMBASA"
            elif csv_field == "Seal No":
                value = self.seal_no
            else:
                value = self._get_field_value(row, excel_columns)
                if csv_field in date_fields:
                    value = self._process_date_field(value)

            record[csv_field] = value if value not in [None, "Non spécifié"] else ""

        caliber = self._get_field_value(row, ["Size"])
        weight = self._get_field_value(row, ["Net weight per box (kg)"])
        record["Nb of fruits per box"] = ViruCalculations.nb_of_fruits_per_box(caliber, weight)
        record["Nb of pallets"] = 1

        return record





    def _get_field_value(self, row, excel_columns):
        for col in excel_columns:
            if col in row.index and pd.notna(row[col]):
                return row[col]
        return ""

    def _process_date_field(self, value):
        try:
            if pd.notnull(value) and value != "":
                parsed = pd.to_datetime(value, errors='coerce')
                if pd.notnull(parsed):
                    return parsed.strftime("%d/%m/%Y")
        except Exception as e:
            print(f"⚠️ Erreur conversion date: {e}")
        return ""


