import pandas as pd

class IngophaseCalculations:
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
                    return caliber_str  
            else:
                return caliber_str  
        except Exception as e:
            print(f"⚠️ Erreur nb_of_fruits_per_box: {e}")
            return ""
    
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
    def box_tare(cartons_per_pallet, net_weight=None, gross_weight=None):
        """
        ➕ Calcule la tare de la boîte selon le nombre de cartons par palette :
        - Si 216 cartons → tare = 0.35
        - Sinon → tare = 0.7
        """
        try:
            cartons = int(float(str(cartons_per_pallet).replace(",", ".")))

            # Si les poids sont fournis, on calcule dynamiquement la tare par boîte
            if net_weight is not None and gross_weight is not None:
                net = float(str(net_weight).replace(",", "."))
                gross = float(str(gross_weight).replace(",", "."))
                tare = (gross - net) / cartons
                return round(tare, 2)

            # Sinon, on applique la logique métier simple
            return 0.35 if cartons == 216 else 0.7

        except Exception as e:
            print(f"⚠️ Erreur box_tare: {e}")
            return 0.7

