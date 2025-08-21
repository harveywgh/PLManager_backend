import pandas as pd

class CpfCalculations:
    @staticmethod
    def nb_of_pallets_by_palletnum(pallet_num, boxes, df, current_value=None):
        try:
            if current_value not in [None, "", "0", "0,00000"]:
                return current_value
            lignes = df[df["PALLET"] == pallet_num]
            if len(lignes) == 1:
                return "1,00000"
            total_boxes = lignes["CASES"].dropna().astype(float).sum()
            boxes = float(boxes)
            if total_boxes > 0:
                ratio = boxes / total_boxes
                return f"{ratio:.5f}".replace(".", ",")
        except Exception as e:
            print(f"⚠️ CPF pallets calc error: {e}")
        return ""
    
    @staticmethod
    def nb_of_fruits_per_box(caliber, net_weight_per_box):
        try:
            if not caliber or not net_weight_per_box:
                return ""

            caliber = float(str(caliber).strip().replace(",", "."))
            net = float(str(net_weight_per_box).strip().replace(",", "."))

            if abs(net - 4) < 0.01:
                return int(caliber)
            elif abs(net - 10) < 0.01:
                return int(round(caliber * 2.5))
        except Exception as e:
            print(f"⚠️ [CpfCalculations] Erreur calcul nb_of_fruits_per_box : {e}")
        return ""

    
    @staticmethod
    def box_tare(net_weight, cases, assumed_gross_per_box=10):
        try:
            net_weight = float(str(net_weight).replace(",", "."))
            cases = float(str(cases).replace(",", "."))
            if cases > 0:
                net_per_box = net_weight / cases
                tare = assumed_gross_per_box - net_per_box
                return round(tare, 2)
        except Exception as e:
            print(f"⚠️ Erreur box_tare: {e}")
        return ""
    
    @staticmethod
    def net_weight_per_pallet(net_weight_per_box, cartons_per_pallet):
        try:
            net_weight_per_box = float(str(net_weight_per_box).replace(",", "."))
            cartons_per_pallet = float(str(cartons_per_pallet).replace(",", "."))
            return round(net_weight_per_box * cartons_per_pallet, 2)
        except Exception as e:
            print(f"⚠️ Erreur net_weight_per_pallet: {e}")
            return ""


