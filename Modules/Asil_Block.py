class ASIL_Block:
    
    # --- ISO 26262 ASIL Requirements ---
   
    ASIL_REQUIREMENTS = {
        "D": [0.99, 0.90, 10.0],  # SPFM > 99%, LFM > 90%, RF < 10 FIT
        "C": [0.97, 0.80, 100.0], # SPFM > 97%, LFM > 80%, RF < 100 FIT
        "B": [0.90, 0.60, 100.0], # SPFM > 90%, LFM > 60%, RF < 100 FIT
        "A": [0.00, 0.00, 1000.0] # Only residual FIT limit applies for ASIL A
    }

    def __init__(self, name: str):

        self.name = name

    def _determine_asil(self, spfm: float, lfm: float, lambda_rf_sum: float) -> str:
        
        for asil_level in ["D", "C", "B"]:
            req = self.ASIL_REQUIREMENTS[asil_level]
            spfm_min, lfm_min, rf_max = req
            
            if (spfm >= spfm_min and
                lfm >= lfm_min and
                lambda_rf_sum < rf_max):
                return f"ASIL {asil_level}"

        if lambda_rf_sum < self.ASIL_REQUIREMENTS["A"][2]:
            return "ASIL A"

        return "QM (Quality Management)"


    def compute_metrics(self, lambda_total: float, lambda_dangerous_sum: float, 
                        lambda_latent_sum: float, lambda_rf_sum: float) -> dict:
        spfm = 0.0
        lfm = 0.0
        achieved_asil = "QM"
        
        if lambda_total > 0:
            spfm = 1.0 - (lambda_dangerous_sum / lambda_total)
            
        lambda_safe_and_covered = lambda_total - lambda_dangerous_sum
        
        if lambda_safe_and_covered > 0:
            lfm = 1.0 - (lambda_latent_sum / lambda_safe_and_covered)
        
        achieved_asil = self._determine_asil(spfm, lfm, lambda_rf_sum)

        return {
            'SPFM': spfm,
            'LFM': lfm,
            'Lambda_RF_Sum': lambda_rf_sum,
            'ASIL_Achieved': achieved_asil
        }