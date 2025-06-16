from .sunny_base import BaseSunnyService
import pandas as pd
import os


class SunnyService(BaseSunnyService):
    def __init__(self):
        pl_column_mapping = self._initialize_column_mapping()
        super().__init__(pl_column_mapping)
        self.csv_settings = {}  # Stocke les paramètres CSV envoyés par le front
        
        # Debug pour voir si les colonnes existent bien dans le fichier Excel
        print("📌 Colonnes mappées pour SunnyService :", pl_column_mapping)

    def _initialize_column_mapping(self):
        """
        Initialise le mappage des colonnes entre le fichier Excel et le CSV.
        """
        return {
            "Pallet no": ["Pallet ID"],
            "Exporter Name": ["Exporter"],
            "Shipping line": ["Shipping Line"],
            "Vessel Name": ["Vessel"],
            "Port of departure": ["Departure Port"],
            "Port of arrival": ["Arrival Port"],
            "Packing house departure date": [""],
            "ETA": ["ETA"],
            "Exporter Ref": ["Ref nr"],
            "Seal No": ["Seal nr"],
            "Container No": ["Container"],
            "Species": ["Product"],
            "Variety": ["Variety"],
            "Size_caliber_count": ["Size"],
            "Nb of fruits per box": ["Peices"],
            "Class": ["Quality"],
            "Brand": ["Brand"],
            "Country of origin": ["Origin"],  
            "Packaging": ["Packing"],
            "Packaging type": ["Pack type"],
            "Box tare (kg)": ["Tare weight"],
            "Net weight per box (kg)": [""],
            "Net weight per pallet (kg)": ["Net pal weight"],
            "Cartons per pallet": ["Boxes"],
            "Nb of pallets": [],  
            "Lot no": [""],
            "Date of packaging": [""],
            "PACKING HOUSE/PRODUCER": ["Packhouse name"],
            "Producer": ["Grower"],
            "ETD": ["Date of Issue"],
            "Temperature recorder no": [""],
            "Date of harvesting": [""], #
            "Plot": ["Field"],
            "Certifications": [""],
            "GGN": ["GGN Exporter"],
            "COC": [""],
            "Certified GG/COC": ["GGN Supplier"],
            "Forwarder at destination": [""],
        }

    def apply_csv_settings(self, settings):
        """
        Applique les paramètres CSV envoyés par le front-end et valide les champs obligatoires.
        """
        self.csv_settings = settings
        print("📌 Paramètres CSV reçus APRES TRANSMISSION :", settings)

        mandatory_fields = ["country_of_origin", "forwarder"]
        for field in mandatory_fields:
            if field not in self.csv_settings or not self.csv_settings[field]:
                raise ValueError(f"⚠️ Le champ obligatoire '{field}' est manquant ou vide !")

        self.csv_settings["Country of origin"] = self.csv_settings.pop("country_of_origin", "Non spécifié")
        self.csv_settings["Forwarder at destination"] = self.csv_settings.pop("forwarder", "Non spécifié")
        self.csv_settings["Importer"] = self.csv_settings.pop("importer", "Non spécifié")
        self.csv_settings["Archive"] = self.csv_settings.pop("archive", "Non")

        # Gérer les champs facultatifs sans levée d'erreur
        optional_fields = ["packaging", "packaging_type", "custom1", "custom2"]
        for field in optional_fields:
            self.csv_settings[field] = self.csv_settings.get(field, None) 

    def _extract_data(self, container_df):
        """
        Extrait les données du DataFrame d'un conteneur.
        """
        if not isinstance(container_df, pd.DataFrame):
            print(f"❌ ERREUR: _extract_data() a reçu un type invalide : {type(container_df)}")
            return []

        extracted_data = []
        for _, row in container_df.iterrows():
            record = self._extract_row_data(row)
            extracted_data.append(record)

        if not extracted_data:
            print("⚠️ Aucune donnée extraite ! Vérifie ton extraction.")
            return []

        return extracted_data



    def _extract_row_data(self, row):
        """
        Extrait les données d'une ligne spécifique en appliquant les paramètres CSV.
        """
        if not isinstance(row, pd.Series):
            print(f"❌ ERREUR: _extract_row_data() a reçu un type invalide : {type(row)}")
            return {}

        record = {}
        date_fields = ["ETA", "ETD", "Packing house departure date", "Date of packaging", "Date of harvesting"]

        for csv_field, excel_columns in self.pl_column_mapping.items():
            if csv_field in self.csv_settings and self.csv_settings[csv_field] is not None:
                print(f"✅ Remplacement {csv_field} → {self.csv_settings[csv_field]}")
                record[csv_field] = self.csv_settings[csv_field]
            else:
                record[csv_field] = self._get_field_value(row, excel_columns)

                if csv_field in date_fields:
                    record[csv_field] = self._process_date_field(row, excel_columns)

            if record[csv_field] in [None, "", "Non spécifié"]:
                record[csv_field] = ""

        return record


    def _get_field_value(self, row, excel_columns):
        """
        Récupère la valeur brute d'une colonne Excel correspondant à un champ CSV.
        """
        for excel_column in excel_columns:
            if excel_column in row.index:
                value = row[excel_column]

                if pd.notna(value):
                    return value

        return ""


    def _process_date_field(self, row, excel_columns):
        """
        Traite les champs de type date et les formate en 'dd/mm/yyyy'.
        """
        for excel_column in excel_columns:
            if excel_column in row.index:
                value = row[excel_column]

                if isinstance(value, str):
                    value = value.strip()  # Nettoyer les espaces autour des valeurs

                try:
                    if pd.notnull(value) and value != "":
                        date_value = pd.to_datetime(value, errors='coerce')

                        if pd.isnull(date_value):
                            print(f"⚠️ Erreur conversion date `{excel_column}`: valeur incorrecte -> {value}")
                            return ""

                        return date_value.strftime("%d/%m/%Y")
                except Exception as e:
                    print(f"⚠️ Erreur conversion date `{excel_column}`: {e}")

        return ""

