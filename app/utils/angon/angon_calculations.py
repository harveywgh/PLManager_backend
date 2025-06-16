import pandas as pd

class AngonCalculations:
    @staticmethod
    def nb_of_fruits_per_box(caliber, weight):
        try:
            caliber = float(str(caliber).replace(",", "."))
            weight = float(str(weight).replace(",", "."))

            if weight == 4:
                return int(caliber)
            elif weight == 10:
                return int(round(caliber * 2.5))
        except Exception as e:
            print(f"⚠️ Erreur nb_of_fruits_per_box: {e}")
        return ""

    @staticmethod
    def nb_of_pallets_by_palletnum(pallet_num, boxes, df, current_value=None):
        """
        Calcule le nombre de palettes basé sur la répartition des cartons si non fourni.
        """
        try:
            if current_value not in [None, "", "Non spécifié"]:
                return current_value

            if pd.isna(pallet_num) or pd.isna(boxes):
                return ""

            lignes = df[df["Pallet"] == pallet_num]
            if len(lignes) == 1:
                return "1,00000"

            total = lignes["Carton"].dropna().astype(float).sum()
            boxes = float(str(boxes).replace(",", "."))

            if total > 0:
                ratio = boxes / total
                return f"{ratio:.5f}".replace(".", ",")
        except Exception as e:
            print(f"⚠️ Erreur nb_of_pallets_by_palletnum: {e}")
        return ""

    @staticmethod
    def box_tare(value):
        try:
            if value in [None, "", "Non spécifié"]:
                return "0"
            return value
        except Exception as e:
            print(f"⚠️ Erreur box_tare: {e}")
        return "0"
