import pandas as pd

class JorieCalculations:
    @staticmethod
    def nb_of_fruits_per_box(caliber, weight):
        """
        Règle métier :
        - Si poids = 4 → nb fruits = caliber
        - Si poids = 10 → nb fruits = caliber * 2.5
        """
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
        Calcule le nombre de palettes si non défini :
        - Si une seule ligne → 1,00000
        - Sinon → ratio (boxes / total_boxes pour cette palette)
        - Si déjà défini (current_value), retourne sa valeur
        """
        try:
            if current_value not in [None, "", "0", "0,00000"]:
                return current_value

            if pd.isna(pallet_num) or pd.isna(boxes):
                return ""

            lignes = df[df["Pallet"] == pallet_num]

            if len(lignes) == 1:
                return "1,00000"

            total_boxes = lignes["Cartons per pallet"].dropna().astype(float).sum()
            boxes = float(boxes)

            if total_boxes > 0:
                ratio = boxes / total_boxes
                return f"{ratio:.5f}".replace(".", ",")
        except Exception as e:
            print(f"⚠️ Erreur nb_of_pallets_by_palletnum: {e}")
            
    @staticmethod
    def net_weight_per_box(mass, cartons):
        """
        Calcule le poids net par boîte à partir du poids total par palette (mass)
        et du nombre de cartons (cartons).
        """
        try:
            mass = float(str(mass).replace(",", "."))
            cartons = float(str(cartons).replace(",", "."))
            if cartons > 0:
                return round(mass / cartons, 2)
        except Exception as e:
            print(f"⚠️ Erreur net_weight_per_box: {e}")
        return ""
