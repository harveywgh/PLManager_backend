class Calculations:
    @staticmethod
    def sfa_net_weight_per_box(net_weight, cartons):
        try:
            net_weight = float(net_weight)
            cartons = float(cartons)
            if cartons > 0:
                return f"{net_weight / cartons:.5f}".replace(".", ",")
        except (ValueError, TypeError):
            pass
        return ""



    @staticmethod
    def sfa_box_tare(pallet_totals, barcode):
        try:
            if barcode in pallet_totals.index:
                row = pallet_totals.loc[barcode]

                if all(col in row for col in ["Gross Weight", "Nett Weight", "No Cartons"]):
                    gross_weight = row["Gross Weight"]
                    net_weight = row["Nett Weight"]
                    cartons = row["No Cartons"]

                    # Sécurisation : conversion en float
                    try:
                        cartons = float(cartons)
                        gross_weight = float(gross_weight)
                        net_weight = float(net_weight)
                    except (ValueError, TypeError):
                        print(f"⚠️ Données non numériques pour {barcode}, impossible de calculer Box Tare.")
                        return ""

                    if cartons > 0:
                        return f"{(gross_weight - 20 - net_weight) / cartons:.2f}".replace(".", ",")
                else:
                    print(f"⚠️ Impossible de calculer Box Tare : colonnes manquantes pour {barcode}")
        except Exception as e:
            print(f"❌ Erreur dans sfa_box_tare pour {barcode} : {e}")
        return ""



    @staticmethod
    def sfa_nb_of_pallets(cartons, total_cartons):
        try:
            cartons = float(cartons)
            total_cartons = float(total_cartons)
            if total_cartons > 0:
                return f"{cartons / total_cartons:.5f}".replace(".", ",")
        except (ValueError, TypeError):
            pass
        return ""

