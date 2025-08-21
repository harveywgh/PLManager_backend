import pandas as pd

class SafproCalculations:
    @staticmethod
    def nb_of_fruits_per_box(caliber, species="", net_weight_per_box=None):
        """
        ➕ Nombre de fruits par boîte.
        - Si species = SC et net_weight_per_box ∈ [9, 11] kg → mapping par calibre.
        - Sinon → retourne le calibre tel quel.
        """
        try:
            caliber_str = str(caliber).strip().upper()
            species = species.strip().upper()
            if species == "SC" and net_weight_per_box is not None:
                try:
                    net_weight = float(str(net_weight_per_box).replace(",", "."))
                    if 9.0 <= net_weight <= 11.0:
                        mapping = {
                            "1": 94,
                            "1X": 75,
                            "1XX": 68,
                            "1XXX": 43,
                            "2": 98,
                            "3": 105
                        }
                        if caliber_str in mapping:
                            return mapping[caliber_str]
                except ValueError:
                    pass  # On ignore si le poids est invalide

            # Par défaut, retourne le calibre tel quel
            return caliber_str

        except Exception as e:
            print(f"⚠️ Erreur nb_of_fruits_per_box: {e}")
            return ""



    @staticmethod
    def box_tare(cartons_per_pallet, species="", net_weight_per_box=None, original_value=None):
        """
        ➕ Calcule la tare uniquement si species = SC et poids net boîte ∈ [9, 11]
        Sinon, retourne la valeur d'origine (fichier Excel).
        """
        try:
            species = species.strip().upper()
            if species == "SC" and net_weight_per_box is not None:
                try:
                    net_weight = float(str(net_weight_per_box).replace(",", "."))
                    if 9.0 <= net_weight <= 11.0:
                        return 0.5
                except ValueError:
                    pass  
            return original_value 
        except Exception as e:
            print(f"⚠️ Erreur box_tare: {e}")
            return original_value

