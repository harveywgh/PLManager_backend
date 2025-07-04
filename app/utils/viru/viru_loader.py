import pandas as pd

class ViruLoader:
    @staticmethod
    def load_excel_file(file_path):
        """
        Charge uniquement la première feuille du fichier Excel.
        """
        df = pd.read_excel(file_path, sheet_name=0, dtype=str)  # sheet_name=0 => première feuille
        print("📥 [ViruLoader] 1 seule feuille chargée")
        return {"Feuille1": df}  # On retourne un dict pour rester compatible avec BaseViruService
