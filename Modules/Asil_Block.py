from .Base import FAULTS

class ASIL_Block:
    """
    Evaluates final system metrics and determines the achieved ASIL level according to ISO 26262 requirements.
    """

    ASIL_REQUIREMENTS = {
        "D": [0.99, 0.90, 10.0],  # SPFM > 99%, LFM > 90%, RF < 10 FIT
        "C": [0.97, 0.80, 100.0], # SPFM > 97%, LFM > 80%, RF < 100 FIT
        "B": [0.90, 0.60, 100.0], # SPFM > 90%, LFM > 60%, RF < 100 FIT
        "A": [0.00, 0.00, 1000.0] # Only residual FIT limit applies for ASIL A
    }

    def __init__(self, name: str):
        """
        Initializes the ASIL calculation block.

        @param name The descriptive name of the calculation block.
        """
        self.name = name

    def _determine_asil(self, spfm: float, lfm: float, lambda_rf_sum: float) -> str:
        """
        Determines the achieved ASIL level based on calculated metrics.

        @param spfm Single-Point Fault Metric value (0.0 to 1.0).
        @param lfm Latent Fault Metric value (0.0 to 1.0).
        @param lambda_rf_sum Total sum of residual FIT rates.
        @return A string representing the achieved ASIL level or QM.
        """
        for asil_level in ["D", "C", "B"]:
            req = self.ASIL_REQUIREMENTS[asil_level]
            spfm_min, lfm_min, rf_max = req
            
            if (spfm >= spfm_min and lfm >= lfm_min and lambda_rf_sum < rf_max):
                return f"ASIL {asil_level}"

        if lambda_rf_sum < self.ASIL_REQUIREMENTS["A"][2]:
            return "ASIL A"

        return "QM (Quality Management)"

    def compute_metrics(self, lambda_total: float, final_spfm_dict: dict, final_lfm_dict: dict) -> dict:
        """
        Calculates final ISO 26262 metrics using result dictionaries from the block chain.

        @param lambda_total The total FIT rate of the entire system.
        @param final_spfm_dict Dictionary containing final residual and dangerous FIT rates.
        @param final_lfm_dict Dictionary containing final latent FIT rates.
        @return A dictionary containing SPFM, LFM, Residual FIT sum, and the achieved ASIL level.
        """
        lambda_dangerous_sum = sum(final_spfm_dict.values())
        lambda_latent_sum = sum(final_lfm_dict.values())
        lambda_rf_sum = lambda_dangerous_sum
        
        spfm = 0.0
        lfm = 0.0
        
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