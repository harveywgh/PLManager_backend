import pandas as pd

class MavunoLoader:
    @staticmethod
    def load_excel_file(file_path):
        """
        Charge le tableau principal à partir de la ligne 10 (ligne 10 = index 9).
        """
        df = pd.read_excel(file_path, dtype=str, skiprows=9)
        print(f"📥 [MavunoLoader] Chargement principal : {len(df)} lignes")
        return df

    @staticmethod
    def extract_metadata(file_path):
        """
        Extrait les métadonnées des lignes 1 à 10 du fichier Excel.
        """
        raw = pd.read_excel(file_path, header=None, nrows=10)

        def extract_from_range(row_idx, col_range):
            for col in col_range:
                value = raw.iloc[row_idx, col]
                if pd.notna(value):
                    return str(value).strip()
            return ""

        metadata = {
            "Exporter Name": extract_from_range(0, range(1, 6)),  # Ligne 1, colonnes B-F
            "Exporter Ref": extract_from_range(2, range(1, 6)),   # Ligne 3
            "Seal No": extract_from_range(4, range(1, 6)),        # Ligne 5
            "GGN": extract_from_range(5, range(1, 6)),            # Ligne 6
            "COC": extract_from_range(6, range(1, 6)),            # Ligne 7
            "Port of departure": extract_from_range(4, range(10, 13)),  # Ligne 5, colonnes K-M
            "Port of arrival": extract_from_range(5, range(10, 13)),    # Ligne 6
        }

        # Traitement ETA/ETD
        etd_raw = extract_from_range(4, range(13, 17))
        eta_raw = extract_from_range(5, range(13, 17))
        if "ETD" in etd_raw:
            metadata["ETD"] = etd_raw.split(":")[-1].strip()
        if "ETA" in eta_raw:
            metadata["ETA"] = eta_raw.split(":")[-1].strip()

        print(f"📌 [MavunoLoader] Métadonnées extraites : {metadata}")
        return metadata
