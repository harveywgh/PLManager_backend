class AlgCalculations:
    @staticmethod
    def box_tare(gross_weight, net_weight, cartons):
        """
        Calcule la tare par boîte : (poids brut - poids net) / nb cartons
        Format : 2 décimales, séparateur français
        """
        if all(isinstance(x, (int, float)) for x in [gross_weight, net_weight, cartons]) and cartons > 0:
            tare = (gross_weight - net_weight) / cartons
            return f"{tare:.5f}".replace(".", ",")
        return ""

    @staticmethod
    def net_weight_per_box(net_weight, cartons):
        """
        Calcule le poids net par boîte : poids net / nb cartons
        Format : 2 décimales, séparateur français
        """
        if isinstance(net_weight, (int, float)) and isinstance(cartons, (int, float)) and cartons > 0:
            result = net_weight / cartons
            return f"{result:.5f}".replace(".", ",")
        return ""
    
    @staticmethod
    def nb_fruits_mandarines(caliber):
        if caliber is None:
            return ""

        try:
            # Conversion sûre + normalisation
            key = str(caliber).lower().strip()

            # Remove decimals if it's a whole number like "1.0"
            if key.endswith(".0"):
                key = key[:-2]

            mapping = {
                "1xxx": 54,
                "1xx": 60,
                "1x": 70,
                "1": 80,
                "2": 100,
                "3": 120,
                "4": 145,
                "5": 165
            }
            print(f"🧪 Caliber cleaned: {key} → {mapping.get(key, '2H')}")
            return mapping.get(key, "2H")  # fallback "2H" si pas trouvé
        except Exception as e:
            print(f"⚠️ erreur mapping caliber: {e}")
            return ""

