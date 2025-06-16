from .southern_fruit_alliance_base import BaseSFAService
from ...utils.southern_fruit_alliance.southern_fruit_alliance_calculation import Calculations
import pandas as pd

class SFAService(BaseSFAService):
    def __init__(self):
        self.csv_settings = {}
        super().__init__(pl_column_mapping=self._initialize_column_mapping())

    def _initialize_column_mapping(self):
        return {
            "Pallet no": ["PALLET NO"],
            "Exporter Name": ["EXPORTER NAME"],
            "Shipping line": ["Shipping line"],
            "Vessel Name": ["Vessel name"],
            "Port of departure": ["Port of departure"],
            "Port of arrival": ["Port of arrival"],
            "Packing house departure date": ["Packing house departure date"],
            "ETA": ["ETA"],
            "Exporter Ref": ["Exporter ref"],
            "Seal No": ["Seal No"],
            "Container No": ["Container No"],
            "Species": ["Species"],
            "Variety": ["Variety"],
            "Size_caliber_count": ["Count"],
            "Nb of fruits per box": ["Nb of fruits per box"],
            "Class": ["Class"],
            "Brand": ["Brand"],
            "Country of origin": ["Country of origin"],
            "Packaging": ["Packaging"],
            "Packaging type": ["Packaging Type"],
            "Box tare (kg)": ["Box tare (kg)"],
            "Net weight per box (kg)": ["Net weight per box (kg)"],
            "Net weight per pallet (kg)": ["Nett weight per pallet (kg)"],
            "Cartons per pallet": ["Cartons per pallet"],
            "Nb of pallets": ["Nb of pallets"],
            "Lot no": ["Lot no"],
            "Date of packaging": ["Date of packaging"],
            "PACKING HOUSE/PRODUCER": ["PACKING HOUSE/PRODUCER"],
            "Producer": ["Producer ID"],
            "ETD": ["ETD"],
            "Temperature recorder no": ["Temp Tail"],
            "Date of harvesting": ["Date of harvesting"],
            "Plot": ["Plot"],
            "Certifications": ["Certification"],
            "GGN": ["GGN"],
            "COC": ["COC"],
            "Certified GG/COC": ["Certified GG/COC"],
            "Forwarder at destination": ["Forwarder at destination"],
        }
        
    def apply_csv_settings(self, settings):
        self.csv_settings = settings
        print("📌 Paramètres CSV SFA :", settings)

        # Champs obligatoires
        required = ["country_of_origin", "forwarder"]
        for f in required:
            if not settings.get(f):
                raise ValueError(f"⚠️ Champ obligatoire manquant : {f}")

        # Mappage des clés standardisées
        self.csv_settings["Country of origin"] = settings.pop("country_of_origin")
        self.csv_settings["Forwarder at destination"] = settings.pop("forwarder")
        self.csv_settings["Importer"] = settings.get("importer", "")
        self.csv_settings["Archive"] = settings.get("archive", "")
        self.csv_settings["Fournisseur"] = settings.get("Fournisseur", "").strip().lower()

    def _extract_data(self, container_dataframe):
        """
        Méthode spécialisée pour extraire les données d'une PL SFA.
        """
        extracted_data = []
        pallet_totals = self._calculate_pallet_totals(container_dataframe)

        for _, row in container_dataframe.iterrows():
            record = self._extract_row_data(row, pallet_totals)
            extracted_data.append(record)

        if not extracted_data:
            print("⚠️ Aucune donnée extraite ! Vérifie ton extraction.")
            return []

        return extracted_data

    def _calculate_pallet_totals(self, container_dataframe):
        """
        Calcule les totaux pour les palettes (cartons, poids brut, poids net), seulement si les colonnes existent.
        """
        if "PALLET NO" not in container_dataframe.columns:
            print("⚠️ ERREUR: La colonne 'PALLET NO' est absente du fichier ! Vérifie ton mapping.")
            return pd.DataFrame()

        agg_dict = {}
        for col in ["No Cartons", "Gross Weight", "Nett Weight"]:
            if col in container_dataframe.columns:
                agg_dict[col] = "sum"
            else:
                print(f"⚠️ Colonne absente : {col} — elle ne sera pas incluse dans le calcul.")

        if not agg_dict:
            print("⚠️ Aucune colonne pertinente pour le calcul des totaux de palettes.")
            return pd.DataFrame()

        return container_dataframe.groupby("PALLET NO").agg(agg_dict)


    def _extract_row_data(self, row, pallet_totals):
        """
        Extrait les données d'une ligne spécifique en appliquant les paramètres CSV.
        """
        record = {}
        date_fields = ["ETA", "ETD", "Packing house departure date", "Date of packaging", "Date of harvesting"]

        for csv_field, excel_columns in self.pl_column_mapping.items():
            if csv_field in self.csv_settings and self.csv_settings[csv_field] is not None:
                record[csv_field] = self.csv_settings[csv_field]
            else:
                record[csv_field] = self._process_field(csv_field, excel_columns, row, pallet_totals)

                if csv_field in date_fields:
                    record[csv_field] = self._process_date_field(row, excel_columns)

            if record[csv_field] in [None, "", "Non spécifié"]:
                record[csv_field] = ""

        return record


    def _process_field(self, csv_field, excel_columns, row, pallet_totals):
        """
        Traite un champ spécifique en fonction de sa logique.
        """
        if csv_field == "Country of origin":
            return self.csv_settings.get("Country of origin", "ZA")

        if csv_field == "Exporter name":
            supplier_code_map = {
                "zestfruit": "Z6",
                "komati": "KV",
                "mahela": "9J",
                "grosa": "7V"
            }
            fournisseur = str(self.csv_settings.get("Fournisseur", "")).strip().lower()
            prefix = supplier_code_map.get(fournisseur, "")
            if not prefix:
                print(f"⚠️ Fournisseur inconnu ou non mappé : '{fournisseur}'")
            return f"{prefix}-{row.get('Producer ID', '').strip()}" if prefix else row.get("Producer ID", "").strip()

        return self._get_field_value(row, excel_columns)

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

    def _get_field_value(self, row, excel_columns):
        """
        Récupère la valeur brute d'une colonne Excel correspondant à un champ CSV.
        """
        for excel_column in excel_columns:
            if excel_column in row.index and pd.notna(row[excel_column]):
                return row[excel_column]
        return ""
