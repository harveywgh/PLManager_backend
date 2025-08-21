import pandas as pd

class AthosCalculations:
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

            lignes = df[df["Pallet n°"] == pallet_num]

            if len(lignes) == 1:
                return "1,00000"

            total_boxes = lignes["Quantity per grower"].dropna().astype(float).sum()
            boxes = float(boxes)

            if total_boxes > 0:
                ratio = boxes / total_boxes
                return f"{ratio:.5f}".replace(".", ",")
        except Exception as e:
            print(f"⚠️ Erreur nb_of_pallets_by_palletnum: {e}")
            
    @staticmethod
    def get_packaging_type(weight):
        """
        Déduit le type d’emballage à partir du poids net par boîte.
        - 4 kg → 'Colis 4kg'
        - 10 kg → 'Colis 10kg'
        - Autre → ''
        """
        try:
            weight = float(str(weight).replace(",", "."))
            if weight == 4:
                return "Colis 4kg"
            elif weight == 10:
                return "Colis 10kg"
        except Exception as e:
            print(f"⚠️ Erreur get_packaging_type: {e}")
        return ""

    @staticmethod
    def get_brand_from_class(cat_value, default_brand):
        """
        Si la catégorie est 'CAT 1.5', retourne 'ATHOS B', sinon retourne la brand d’origine.
        """
        try:
            if str(cat_value).strip().upper() == "CAT 1.5":
                return "ATHOS B"
        except Exception as e:
            print(f"⚠️ Erreur get_brand_from_class: {e}")
        return default_brand

    @staticmethod
    def clean_weight_value(value):
        """
        Nettoie le champ de poids pour ne garder que la valeur numérique.
        Par exemple : '4.0 KG' → 4.0
        """
        try:
            if isinstance(value, str):
                value = value.replace("KG", "").strip().replace(",", ".")
            return float(value)
        except Exception as e:
            print(f"⚠️ Erreur clean_weight_value: {e}")
            return ""

