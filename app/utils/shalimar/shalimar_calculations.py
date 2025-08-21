# shalimar_calculations.py
import pandas as pd
import re

class ShalimarCalculations:
    @staticmethod
    def _extract_numeric(value):
        try:
            match = re.search(r"\d+(\.\d+)?", str(value).replace(",", "."))
            return float(match.group()) if match else None
        except Exception:
            return None

    @staticmethod
    def normalize_weight(value, return_format="2dec"):
        """
        Normalise un poids texte en supprimant les unités et décimales.
        Exemples:
          "4.3 KGS" -> "4.00" si return_format="2dec"
          "4,5 kg"  -> "4" si return_format="int"
          "  10kg " -> "10.00" si return_format="2dec"
        """
        num = ShalimarCalculations._extract_numeric(value)
        if num is None:
            return ""
        integer_part = int(num)
        if return_format == "int":
            return str(integer_part)
        return f"{integer_part:.2f}"

    @staticmethod
    def nb_of_fruits_per_box(caliber, weight):
        try:
            cal = ShalimarCalculations._extract_numeric(caliber)
            w = ShalimarCalculations._extract_numeric(weight)
            if cal is None or w is None:
                return ""
            if abs(w - 4) <= 0.6:
                w = 4.0
            elif abs(w - 10) <= 0.6:
                w = 10.0
            if w == 4.0:
                return int(round(cal))
            if w == 10.0:
                return int(round(cal * 2.5))
        except Exception as e:
            print(f"⚠️ Erreur nb_of_fruits_per_box: {e}")
        return ""

    @staticmethod
    def nb_of_pallets_by_palletnum(pallet_num, boxes, df, current_value=None):
        try:
            if current_value not in [None, "", "0", "0,00000"]:
                return current_value
            if pd.isna(pallet_num) or pd.isna(boxes):
                return ""
            lignes = df[df["Pallet Number"] == pallet_num]
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
    def compute_box_tare(df):
        def get_tare(value):
            weight_val = ShalimarCalculations._extract_numeric(value)
            if weight_val is None:
                return 0.60
            if abs(weight_val - 4) <= 0.6:
                return 0.32
            elif abs(weight_val - 10) <= 0.6:
                return 0.40
            else:
                return 0.60

        if "Weight per box" not in df.columns:
            print("⚠️ Colonne 'Weight per box' absente pour calculer 'Box tare (kg)'")
            df["Box tare (kg)"] = 0.60
        else:
            df["Box tare (kg)"] = df["Weight per box"].apply(get_tare)

    @staticmethod
    def compute_packaging_type(df):
        def build_packaging(value):
            weight_val = ShalimarCalculations._extract_numeric(value)
            return f"COLIS {int(weight_val)}KG" if weight_val is not None else "COLIS KG"

        if "Weight per box" not in df.columns:
            print("⚠️ Colonne 'Weight per box' absente pour créer 'Packaging type'")
            df["Packaging type"] = "COLIS KG"
        else:
            df["Packaging type"] = df["Weight per box"].apply(build_packaging)
