import pandas as pd

class IngophaseLoader:
    @staticmethod
    def load_excel_file(file_path):
        """
        Charge la première feuille du fichier Excel.
        """
        try:
            xls = pd.ExcelFile(file_path)
            print(f"📄 Feuilles Excel détectées : {xls.sheet_names}")
            if len(xls.sheet_names) == 0:
                raise ValueError("Aucune feuille détectée dans le fichier.")
            
            # Toujours charger la première feuille
            df = pd.read_excel(xls, sheet_name=0, dtype=str)
            print(f"📥 [IngophaseLoader] Chargement réussi : {len(df)} lignes")
            return df
        except Exception as e:
            print(f"❌ Erreur lors du chargement Excel : {e}")
            raise