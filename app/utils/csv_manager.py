import csv
import os

class CSVManager:
    @staticmethod
    def write_csv(file_path, data):
        """Écrit les données dans un fichier CSV."""
        if not data:
            raise ValueError("Les données sont vides.")

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, mode="w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys(), delimiter=";")
            writer.writeheader()
            writer.writerows(data)
