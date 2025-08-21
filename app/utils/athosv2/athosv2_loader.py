import pandas as pd
import re 


class AthosV2Loader:
    @staticmethod
    def load_excel_file(file_path):
        """
        Charge uniquement le fichier Excel complet, sans l'analyser.
        """
        df = pd.read_excel(file_path, header=None, dtype=str)  # sans entête
        return df

    @staticmethod
    def extract_metadata(df):
        """
        Récupère les métadonnées dans des cellules spécifiques.
        """
        metadata = {
            "ETA": df.iloc[15, 3],  # D16 → ligne 15 (index), col 3 (D)
            "ETD": df.iloc[14, 3],  # D15
            "Container No": df.iloc[12, 3],  # D13
            "Exporter Name": df.iloc[6, 3],  # D7
            "Shipping Line": df.iloc[9, 3],  # D10
            "Exporter Ref": AthosV2Loader._extract_exporter_ref(df),
        }
        print("📌 Métadonnées extraites:", metadata)
        return metadata

    @staticmethod
    def extract_table(file_path):
        """
        Charge uniquement le tableau commençant à B19 (entêtes) / B20 (data).
        """
        df = pd.read_excel(file_path, header=18, dtype=str)  # header à la ligne 19 (index 18)
        print(f"📊 [AthosV2Loader] Tableau extrait : {len(df)} lignes")
        return df

    @staticmethod
    def _extract_exporter_ref(df):
        """
        Cherche un ou plusieurs numéros dans les cellules B2:P3 (lignes 1:3, colonnes 1:16).
        Retourne le premier numéro trouvé ou une concaténation.
        """
        try:
            zone = df.iloc[0:3, 1:16]  # lignes 0 à 2, colonnes B à P
            combined_text = " ".join(zone.astype(str).values.flatten())
            numbers = re.findall(r'\d+', combined_text)
            if numbers:
                ref = numbers[0]  # ou ' '.join(numbers) si tu veux tous les regrouper
                print(f"🔍 Exporter Ref détecté : {ref}")
                return ref
            else:
                print("⚠️ Aucun numéro détecté dans la zone Exporter Ref.")
                return ""
        except Exception as e:
            print(f"❌ Erreur extraction Exporter Ref : {e}")
            return ""

