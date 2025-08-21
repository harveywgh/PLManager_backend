import pandas as pd

class SwellenCalculations:
    @staticmethod
    def nb_of_fruits_per_box(caliber, species=""):
        """
        ➕ Nombre de fruits par boîte.
        - Pour SC → correspondance directe par calibre.
        - Sinon → retourne simplement le calibre (en int).
        """
        try:
            caliber_str = str(caliber).strip().upper()
            species = species.strip().upper()

            if species in ["SC"]:
                mapping = {
                "1": 94,
                "1X": 75,
                "1XX": 68,
                "1XXX": 43,
                "2": 98,
                "3": "",  # Inconnu
                "4": "",  # Inconnu
                "5": "",  # Inconnu
            }
                if caliber_str in mapping and mapping[caliber_str] != "":
                    return mapping[caliber_str]
                else:
                    return caliber_str  # défaut : retourne le calibre tel quel
            else:
                return caliber_str  # pour les autres espèces, on retourne juste le calibre
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

            lignes = df[df["Pallet n°"] == pallet_num]

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
    def net_weight_per_pallet(cartons, weight_per_box):
        """
        Calcule le poids net total d'une palette :
        Net weight per pallet = Cartons per pallet × Net weight per box (kg)
        """
        try:
            cartons = float(str(cartons).replace(",", "."))
            weight = float(str(weight_per_box).replace(",", "."))
            return round(cartons * weight, 2)
        except Exception as e:
            print(f"⚠️ Erreur net_weight_per_pallet: {e}")
            return ""
        
    @staticmethod
    def net_weight_per_box(mass, cartons):
        """
        Calcule le poids net par boîte :
        Net weight per box = Net weight per pallet / Cartons per pallet
        """
        try:
            mass = float(str(mass).replace(",", "."))
            cartons = float(str(cartons).replace(",", "."))

            if cartons > 0:
                return round(mass / cartons, 2)
        except Exception as e:
            print(f"⚠️ Erreur net_weight_per_box: {e}")
        return ""


    @staticmethod
    def box_tare(cartons_per_pallet):
        """
        ➕ Calcule la tare de la boîte selon le nombre de cartons par palette :
        - Si 216 cartons → tare = 0.35
        - Sinon → tare = 0.7
        """
        try:
            cartons = int(float(str(cartons_per_pallet).replace(",", ".")))
            return 0.35 if cartons == 216 else 0.7
        except Exception as e:
            print(f"⚠️ Erreur box_tare: {e}")
            return 0.7

