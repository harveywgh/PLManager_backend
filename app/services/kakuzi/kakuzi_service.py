import os
import re
import pandas as pd
from .kakuzi_base import BaseKakuziService
from ...utils.kakuzi.kakuzi_calculations import KakuziCalculations


class KakuziService(BaseKakuziService):
    def __init__(self):
        pl_column_mapping = self._initialize_column_mapping()
        super().__init__(pl_column_mapping)
        self.csv_settings = {}
        
    def _extract_data_from_sheet(self, raw_df):
        calibres = []
        weights = []
        data_rows = []

        container_no = raw_df.iloc[7, 1]      # B8 (index 7,1)
        etd = raw_df.iloc[6, 3]               # D7 (index 6,3)
        eta = raw_df.iloc[9, 3]               # D10 (index 9,3)
        ggn = raw_df.iloc[10, 1]              # B11 (index 10,1)
        exporter_ref = raw_df.iloc[8, 1]      # B9 (index 8,1)
        vessel_raw = raw_df.iloc[9, 1]        # B10 = index (9,1)
        match = re.search(r"Vessel:\s*([^)]+)", str(vessel_raw))
        vessel_name = match.group(1).strip() if match else str(vessel_raw).strip()
        port_of_arrival = raw_df.iloc[3, 3]   # D4 (index 3,3)
        seal_no = ""
        try:
            seal_no = raw_df.iloc[42, 1]       # B43 (index 42,1)
        except IndexError:
            print("⚠️ Ligne 43 absente, 'Seal No' non trouvé.")

        # Calibres et net weights en lignes 16 et 17 (index 15 et 16)
        col = 2
        while True:
            value = raw_df.iloc[15, col]  # ligne 16 (index 15)
            if pd.isna(value):
                break
            
            # Extraction numérique du calibre avec regex
            match = re.match(r"(\d+)", str(value).strip())
            if not match:
                break  # Si pas de nombre au début, on stoppe la boucle
            calibre_num = int(match.group(1))
            
            calibres.append(calibre_num)
            
            net_weight = raw_df.iloc[16, col]  # ligne 17 (index 16)
            weights.append(float(str(net_weight).replace("Kgs", "").replace("[", "").replace("]", "").strip()))
            col += 1

        # Trouver dynamiquement la colonne "Crtn" avec "Type" en dessous
        brand_col_index = None
        for col in range(raw_df.shape[1]):
            header_1 = str(raw_df.iloc[15, col]).strip().lower()
            header_2 = str(raw_df.iloc[16, col]).strip().lower()
            if "crtn" in header_1 and "type" in header_2:
                brand_col_index = col
                break

        if brand_col_index is None:
            print("⚠️ Impossible de trouver la colonne des brands (Crtn Type)")

        # Palettes à partir de ligne 18 (index 17), colonne B (index 1)
        for i in range(17, raw_df.shape[0]):
            pallet_no = raw_df.iloc[i, 1]  # colonne B
            if pd.isna(pallet_no) or not str(pallet_no).strip().isdigit():
                break

            row = raw_df.iloc[i]

            # Récupération du brand dynamiquement, si la colonne existe
            brand = ""
            if brand_col_index is not None and raw_df.shape[1] > brand_col_index:
                brand = raw_df.iloc[i, brand_col_index]

            for j, (caliber, weight) in enumerate(zip(calibres, weights), start=2):
                nb_boxes = row[j]
                if pd.isna(nb_boxes) or not str(nb_boxes).strip().isdigit():
                    continue

                nb_boxes = int(nb_boxes)
                net_weight_per_box = weight
                net_weight_pallet = nb_boxes * weight
                nb_fruits = KakuziCalculations.nb_of_fruits_per_box(caliber, weight)

                data_rows.append({
                    "Pallet n°": pallet_no,
                    "Container n°": container_no,
                    "Exporter ref": exporter_ref,
                    "ETA": eta,
                    "ETD": etd,
                    "GGN\n(=GlobalGAP n°)": ggn,
                    "Seal No": seal_no,
                    "Vessel Name": vessel_name,
                    "Port of arrival": port_of_arrival,
                    "Exporter Name": "KAKUZI PLC",
                    "Size": str(caliber),
                    "Net weight per box (kg)": net_weight_per_box,
                    "Cartons per pallet": nb_boxes,
                    "Net weight per pallet (kg)": net_weight_pallet,
                    "Nb of fruits per box": nb_fruits,
                    "Variety": "HASS",
                    "Quantity per grower": nb_boxes,
                    "Brand": brand  # assigné dynamiquement
                })

        self.eta = eta
        self.etd = etd
        self.exporter_name = "KAKUZI PLC"  
        self.vessel_name = vessel_name
        self.seal_no = seal_no
        self.container_no = container_no
        self.port_of_arrival = port_of_arrival

        return pd.DataFrame(data_rows)




    def _initialize_column_mapping(self):
        return {
            "Pallet no": ["Pallet n°"],
            "Exporter Name": ["Exporter name"],
            "Shipping line": ["Shipping line"],
            "Vessel Name": ["Vessel name"],
            "Port of departure": ["Port of departure"],
            "Port of arrival": ["Port of arrival"],
            "Packing house departure date": ["Packing house departure (dd/mm/yyyy)"],
            "ETA": ["ETA (dd/mm/yyyy)"],
            "Exporter Ref": ["Exporter ref"],
            "Seal No": ["Cod. Tracabilidad"],
            "Container No": ["Container n°"],
            "Species": ["Product"],
            "Variety": ["Variety"],
            "Size_caliber_count": ["Size"],
            "Nb of fruits per box": ["Nb of fruits per box"],
            "Class": ["Cat"],
            "Brand": ["Brand"],
            "Country of origin": ["Country of origin"],
            "Packaging": ["Packaging"],
            "Packaging type": ["Packaging type"],
            "Box tare (kg)": ["Box tare (kg)"],
            "Net weight per box (kg)": ["Net weight per box (kg)"],
            "Net weight per pallet (kg)": ["Net weight per pallet (kg)"],
            "Cartons per pallet": ["Cartons per pallet"],
            "Nb of pallets": ["Nb of pallets"],
            "Lot no": ["Lot n°"],
            "Date of packaging": ["Packaging date (dd/mm/yyyy)"],
            "PACKING HOUSE/PRODUCER": ["Packing house / Producer"],
            "Producer": ["Producer name"],
            "ETD": ["ETD (dd/mm/yyyy)"],
            "Temperature recorder no": ["Temperature recorder n°"],
            "Date of harvesting": ["Harvest date \n (dd/mm/yyyy)"],
            "Plot": ["Field"],
            "Certifications": ["Certifications"],
            "GGN": ["GGN\n(=GlobalGAP n°)"],
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
            if csv_field == "Country of origin" and "Country of origin" in self.csv_settings:
                value = self.csv_settings["Country of origin"]
            elif csv_field == "Forwarder at destination" and "Forwarder at destination" in self.csv_settings:
                value = self.csv_settings["Forwarder at destination"]
            elif csv_field == "Species":
                value = "Avocat"
            elif csv_field == "Packaging type":
                weight = self._get_field_value(row, ["Net weight per box (kg)"])
                try:
                    weight_float = float(weight)
                except Exception:
                    weight_float = None

                value = f"COLIS {int(weight_float)}KG" if weight_float else "COLIS KG"
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
            elif csv_field == "Shipping line":
                value = "MAERSK"
            elif csv_field == "Class":
                value = 1
            elif csv_field == "Seal No":
                value = self.seal_no
            else:
                value = self._get_field_value(row, excel_columns)
                if csv_field in date_fields:
                    value = self._process_date_field(value)

            record[csv_field] = value if value not in [None, "Non spécifié"] else ""

        # Valeurs calculées spécifiques
        weight = self._get_field_value(row, ["Net weight per box (kg)"])
        try:
            weight_float = float(weight)
            box_tare = 0.31 if weight_float == 4 else 0.6
        except Exception:
            box_tare = 0.6
        record["Box tare (kg)"] = box_tare

        caliber = self._get_field_value(row, ["Size"])
        record["Nb of fruits per box"] = KakuziCalculations.nb_of_fruits_per_box(caliber, weight)
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


