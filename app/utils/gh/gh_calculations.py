import pandas as pd

class GHCalculations:
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
            print(f"⚠️ Erreur GH nb_of_fruits_per_box: {e}")
        return ""
