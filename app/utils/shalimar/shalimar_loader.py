import pandas as pd
import re

class ShalimarLoader:

    @staticmethod
    def load_excel_file(file_path):
        return pd.read_excel(file_path, header=None, dtype=str)

    @staticmethod
    def extract_metadata(df):
        try:
            container_no = str(df.iloc[5, 2]).strip() if pd.notna(df.iloc[5, 2]) else ""
            seal_no = str(df.iloc[7, 2]).strip() if pd.notna(df.iloc[7, 2]) else ""

            # Exporter Ref (B/L NR:) en F6 → valeur en G6
            exporter_ref = ""
            print("🔍 Ligne 6 brute (index 5) :")
            print(df.iloc[5, 4:8])  # Affiche colonnes E (4), F (5), G (6), H (7)

            if "B/L" in str(df.iloc[5, 5]):
                exporter_ref = str(df.iloc[5, 6]).strip()

            metadata = {
                "Container No": container_no,
                "Exporter Ref": exporter_ref,
                "Vessel Name": str(df.iloc[3, 2]).strip() if pd.notna(df.iloc[3, 2]) else "",
                "ETD": str(df.iloc[3, 6]).strip() if pd.notna(df.iloc[3, 6]) else "",
                "ETA": str(df.iloc[3, 10]).strip() if pd.notna(df.iloc[3, 10]) else "",
                "Port of departure": str(df.iloc[4, 6]).strip() if pd.notna(df.iloc[4, 6]) else "",
                "Port of arrival": str(df.iloc[4, 10]).strip() if pd.notna(df.iloc[4, 10]) else "",
                "Seal No": seal_no,
            }

            print("📦 DEBUG metadata =", metadata)
            return metadata

        except Exception as e:
            print("❌ Erreur extraction metadata :", e)
            return {}





    def get_cell_value(sheet, cell_ref):
        for merged_range in sheet.merged_cells.ranges:
            if cell_ref in merged_range:
                return sheet[merged_range.bounds[0:2]].value  # top-left of merge
        return sheet[cell_ref].value



    @staticmethod
    def extract_table(file_path):
        """
        Charge le tableau des données (entêtes en ligne 16 / index 15), renomme les colonnes sans nom,
        et supprime les lignes de total ou vides à la fin.
        """
        try:
            # Lire à partir de la ligne 16 (index 15), colonnes B à M
            df = pd.read_excel(file_path, header=15, usecols="B:P", dtype=str)
            df.columns = [
                "Pallet Number",       # B
                "Product",             # C
                "Variety",             # D
                "",                    # E (vide)
                "Brand",               # F
                "Size/Caliber",      # G
                "Weight per box",        # H
                "Boxes per pallet",    # I
                "Net weight",          # J
                "Gross weight",        # K
                "Packing date",        # L
                "GGN",                 # M
                "GAP validity date",   # N
                "",                    # O (vide)
                "Track&Trace Code"     # P
            ]
            # Suppression des lignes de total et des vides (filtrer par numéro de palette)
            df = df[df["Pallet Number"].astype(str).str.isnumeric()]

            print(f"✅ [ShalimarLoader] {len(df)} lignes valides extraites depuis le tableau")
            return df

        except Exception as e:
            print(f"❌ Erreur d'extraction Shalimar : {e}")
            return pd.DataFrame()



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

