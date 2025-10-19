class ASIL_Block:
    """
    Represents the ASIL block, the final component in the safety analysis.
    It calculates the ISO 26262 hardware metrics (SPFM, LFM) and determines 
    the final achievable ASIL level based on predefined target criteria.
    """

    # --- ISO 26262 ASIL Requirements (Used for metric checking) ---
    # Metrics are listed in the order: [SPFM_Min, LFM_Min, Residual_FIT_Max]
    ASIL_REQUIREMENTS = {
        "D": [0.99, 0.90, 10.0],  # SPFM > 99%, LFM > 90%, RF < 10 FIT
        "C": [0.97, 0.80, 100.0], # SPFM > 97%, LFM > 80%, RF < 100 FIT
        "B": [0.90, 0.60, 100.0], # SPFM > 90%, LFM > 60%, RF < 100 FIT
        "A": [0.00, 0.00, 1000.0] # Only residual FIT limit applies for ASIL A
    }

    def __init__(self, name: str):
        """
        Constructor for the ASILBlock.

        @param name: The identifier for the final system-level analysis point.
        """
        self.name = name

    def _determine_asil(self, spfm: float, lfm: float, lambda_rf_sum: float) -> str:
        """
        Helper method to determine the achieved ASIL level based on the metrics.
        Checks requirements from ASIL D down to ASIL A.

        @param spfm: The calculated Single-Point Fault Metric (0.0 to 1.0).
        @param lfm: The calculated Latent Fault Metric (0.0 to 1.0).
        @param lambda_rf_sum: The total Residual Fault rate (FIT).
        @return: The determined ASIL level (e.g., "ASIL D", "ASIL B", or "QM").
        """
        
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
        """
        Calculates the Single-Point Fault Metric (SPFM), Latent Fault Metric (LFM),
        and the final achievable ASIL level.

        @param lambda_total: The sum of all basic event failure rates (sum(lambda)).
        @param lambda_dangerous_sum: The sum of all Single-Point and Residual Faults 
                                     (sum(lambda_SPF + lambda_RF)).
        @param lambda_latent_sum: The sum of all Latent Multi-Point Faults 
                                  (sum(lambda_MPF_L)).
        @param lambda_rf_sum: The sum of ONLY Residual Faults (sum(lambda_RF)) 
                              for the absolute FIT requirement check.
        @return: A dictionary containing the calculated metrics and ASIL level.
        """
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