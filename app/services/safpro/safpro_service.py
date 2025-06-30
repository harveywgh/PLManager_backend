from .safpro_base import BaseSafproService
import pandas as pd
import os

class SafproService(BaseSafproService):
    def __init__(self):
        pl_column_mapping = self._initialize_column_mapping()
        super().__init__(pl_column_mapping)
        self.csv_settings = {}
        self.special_commodity_codes = ["OR", "LE"]

    def _initialize_column_mapping(self):
        """
        Initialise le mappage des colonnes entre le fichier Excel et le CSV.
        """
        return {
            "Pallet no": ["Pallet n°"],  
            "Exporter Name": ["Exporter name"],
            "Shipping line": ["Shipping line"],
            "Vessel Name": ["Vessel Name"],
            "Port of departure": ["Port of departure"],
            "Port of arrival": ["Port of arrival"],
            "Packing house departure date": ["Packing house departure date"],
            "ETA": ["ETA"],
            "Exporter Ref": ["Exporter ref"],
            "Seal No": ["SEAL N°"],
            "Container No": ["Container n°"],
            "Species": ["Commodity"],
            "Variety": ["Variety"],
            "Size_caliber_count": ["Size/caliber/count"],
            "Nb of fruits per box": ["Nb of fruits per box"],
            "Class": ["Class"],
            "Brand": ["Brand"],
            "Country of origin": ["Country of origin"],
            "Packaging": ["Packaging"],
            "Packaging type": ["Packaging type"],
            "Box tare (kg)": ["Box tare (kg)"],
            "Net weight per box (kg)": ["Net weight per box (kg)"],
            "Net weight per pallet (kg)": ["Net weight per pallet (kg)"],
            "Cartons per pallet": ["Cartons"],
            "Nb of pallets": ["Nb of pallets"],  
            "Lot no": ["Lot n°"],
            "Date of packaging": ["Date of packaging"],
            "PACKING HOUSE/PRODUCER": ["Packhouse"],
            "Producer": ["Producer"],
            "ETD": ["ETD"],
            "Temperature recorder no": ["Temperature recorder n°"],
            "Date of harvesting": ["Date of harvesting"],
            "Plot": ["Plot"],
            "Certifications": ["Certifications"],
            "GGN": ["GGN"],
            "COC": ["COC n°"],
            "Certified GG/COC": ["Certified GG/COC"],
            "Forwarder at destination": ["Forwarder at destination"],
        }
    
    def apply_csv_settings(self, settings):
        """
        Applique les paramètres CSV envoyés par le front-end et valide les champs obligatoires.
        """
        self.csv_settings = settings
        print("📌 Paramètres CSV reçus APRES TRANSMISSION :", settings)  # ✅ Affichage complet des données
        
        # Vérifier si 'importer' est bien reçu
        if "importer" not in settings:
            print("❌ ERREUR : Le champ 'importer' est manquant dans les paramètres reçus !")
        else:
            print(f"✅ Importateur reçu : {settings['importer']}")

        # Champs obligatoires
        mandatory_fields = ["country_of_origin", "forwarder"]

        # Vérifier si tous les champs obligatoires sont bien remplis
        for field in mandatory_fields:
            if field not in self.csv_settings or not self.csv_settings[field]:
                raise ValueError(f"⚠️ Le champ obligatoire '{field}' est manquant ou vide !")

        # Adapter les clés envoyées par le front aux noms utilisés dans le mappage
        self.csv_settings["Country of origin"] = self.csv_settings.pop("country_of_origin", "Non spécifié")
        self.csv_settings["Forwarder at destination"] = self.csv_settings.pop("forwarder", "Non spécifié")
        self.csv_settings["Importer"] = self.csv_settings.pop("importer", "Non spécifié")
        self.csv_settings["Archive"] = self.csv_settings.pop("archive", "Non")

        # Gérer les champs facultatifs sans levée d'erreur
        optional_fields = ["packaging", "packaging_type", "custom1", "custom2"]
        for field in optional_fields:
            self.csv_settings[field] = self.csv_settings.get(field, None)  # Laisse None si non défini




    def _extract_data(self, container_df):
        """
        Méthode spécialisée pour extraire les données d'une PL SAFPRO.
        """
        extracted_data = []
        for _, row in container_df.iterrows():
            record = self._extract_row_data(row)
            extracted_data.append(record)
        return extracted_data


    def _extract_row_data(self, row):
        """
        Extrait les données d'une ligne spécifique en appliquant les paramètres CSV.
        """
        record = {}
        date_fields = ["ETA", "ETD", "Packing house departure date", "Date of packaging", "Date of harvesting"]  # ✅ Champs contenant des dates

        for csv_field, excel_columns in self.pl_column_mapping.items():
            if csv_field in self.csv_settings and self.csv_settings[csv_field] is not None:
                print(f"✅ Remplacement {csv_field} → {self.csv_settings[csv_field]}")
                record[csv_field] = self.csv_settings[csv_field]
            else:
                value = self._get_field_value(row, excel_columns)
                if csv_field == "Box tare (kg)":
                    # ✅ Toujours présent et on garde sa valeur brute
                    record[csv_field] = self._get_field_value(row, excel_columns)
                elif csv_field == "Nb of fruits per box":
                    commodity_code = self._get_field_value(row, ["Commodity"])
                    caliber = self._get_field_value(row, ["Size/caliber/count"])

                    if commodity_code in self.special_commodity_codes:
                        record[csv_field] = caliber  
                    else:
                        value = self._get_field_value(row, self.pl_column_mapping.get(csv_field, []))
                        if isinstance(value, (int, float)) or (isinstance(value, str) and value.replace('.', '', 1).isdigit()):
                            record[csv_field] = value
                        else:
                            print(f"⚠️ Valeur invalide ignorée pour '{csv_field}' : {value}")
                            record[csv_field] = ""
                elif csv_field in date_fields:
                    record[csv_field] = self._process_date_field(row, excel_columns)
                else:
                    record[csv_field] = value
            if record[csv_field] in [None, "", "Non spécifié"]:
                record[csv_field] = ""

        print("📌 Données extraites après correction :", record)
        return record


    def _get_field_value(self, row, excel_columns):
        """
        Récupère la valeur brute d'une colonne Excel correspondant à un champ CSV.
        """
        for excel_column in excel_columns:
            if excel_column in row.index and pd.notna(row[excel_column]):
                return row[excel_column]
        return ""

    def _process_date_field(self, row, excel_columns):
        """
        Traite les champs de type date et les formate en 'dd/mm/yyyy'.
        """
        for excel_column in excel_columns:
            value = row.get(excel_column, "")

            try:
                if pd.notnull(value) and value != "":
                    return pd.to_datetime(value, errors='coerce').strftime("%d/%m/%Y")
            except Exception as e:
                print(f"⚠️ Erreur conversion date `{excel_column}`: {e}")

        return ""


