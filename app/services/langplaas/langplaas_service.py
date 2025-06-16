from .langplaas_base import BaseLangplaasService
import pandas as pd

class LangplaasService(BaseLangplaasService):
    def __init__(self):
        pl_column_mapping = self._initialize_column_mapping()
        super().__init__(pl_column_mapping)
        self.csv_settings = {}

    def _initialize_column_mapping(self):
        return {
            "Pallet no": ["Pallet Number"],
            "Exporter Name": [""],
            "Shipping line": [""],
            "Vessel Name": ["Vessel"],
            "Port of departure": ["P.O.L"],
            "Port of arrival": ["P.O.D"],
            "Packing house departure date": [""],
            "ETA": ["ETA"],
            "Exporter Ref": ["Seal No."],
            "Seal No": ["Seal No."],
            "Container No": ["Container No."],
            "Species": ["Comm."],
            "Variety": ["Var."],
            "Size_caliber_count": ["Count"],
            "Nb of fruits per box": ["Packing"],
            "Class": ["Class"],
            "Brand": ["Mark"],
            "Country of origin": [""],
            "Packaging": ["Pack"],
            "Packaging type": ["Inventory"],
            "Box tare (kg)": ["Actual Gross Weight"],
            "Net weight per box (kg)": [""],
            "Net weight per pallet (kg)": ["Actual Nett Weight"],
            "Cartons per pallet": ["Ctns."],
            "Nb of pallets": ["Pallets"],
            "Lot no": [""],
            "Date of packaging": [""],
            "PACKING HOUSE/PRODUCER": [""],
            "Producer": ["PUC"],
            "ETD": ["ETD"],
            "Temperature recorder no": [""],
            "Date of harvesting": [""],
            "Plot": ["Orch."],
            "Certifications": [""],
            "GGN": ["GGN"],
            "COC": [""],
            "Certified GG/COC": [""],
            "Forwarder at destination": [""],
        }

    def apply_csv_settings(self, settings):
        self.csv_settings = settings
        self.csv_settings["Country of origin"] = self.csv_settings.pop("country_of_origin", "ZA")
        self.csv_settings["Forwarder at destination"] = self.csv_settings.pop("forwarder", "Non spécifié")
        self.csv_settings["Importer"] = self.csv_settings.pop("importer", "Non spécifié")
        self.csv_settings["Archive"] = self.csv_settings.pop("archive", "Non")

    def _extract_data(self, container_df):
        extracted_data = []
        for _, row in container_df.iterrows():
            extracted_data.append(self._extract_row_data(row))
        return extracted_data

    def _extract_row_data(self, row):
        record = {}
        date_fields = ["ETA", "ETD", "Packing house departure date", "Date of packaging", "Date of harvesting"]

        for csv_field, excel_columns in self.pl_column_mapping.items():
            if csv_field in self.csv_settings and self.csv_settings[csv_field] is not None:
                record[csv_field] = self.csv_settings[csv_field]
            else:
                if csv_field in date_fields:
                    record[csv_field] = self._process_date_field(row, excel_columns)
                else:
                    value = self._get_field_value(row, excel_columns)
                    record[csv_field] = value if value not in [None, "Non spécifié"] else ""
        #print(f"📦 Ligne extraite [{row.name}] : {record}")
        return record


    def _get_field_value(self, row, excel_columns):
        for col in excel_columns:
            if col in row.index and pd.notna(row[col]):
                return row[col]
            # ❌ DEBUG si aucune colonne trouvée
        print(f"⚠️ Colonne(s) non trouvée(s) : {excel_columns} dans ligne {row.name}")
        return ""

    def _process_date_field(self, row, excel_columns):
        """
        Traite les champs de type date et les formate en 'dd/mm/yyyy' (sans l'heure).
        """
        for excel_column in excel_columns:
            value = row.get(excel_column, "")

            try:
                if pd.notnull(value) and value != "":
                    date = pd.to_datetime(value, errors='coerce')
                    if not pd.isna(date):
                        return date.strftime("%d/%m/%Y")  # ⛔ PAS d'heure ici
            except Exception as e:
                print(f"⚠️ Erreur conversion date `{excel_column}`: {e}")

        return ""
