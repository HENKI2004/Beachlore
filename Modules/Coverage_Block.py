from .Block_Interface import Block_Interface
from .Faults import FAULTS

class Coverage_Block(Block_Interface):
    """
    Applies diagnostic coverage to a specific fault type, splitting the rate into 
    residual (SPFM) and latent (LFM) components.
    """

    def __init__(self, target_fault: FAULTS, dc_rate_c_or_cR: float, dc_rate_latent_cL: float = None):
        """
        Initializes the Coverage_Block with diagnostic coverage parameters.

        @param target_fault The type of fault (Enum) this block processes.
        @param dc_rate_c_or_cR Residual diagnostic coverage or base coverage for LPDDR4.
        @param dc_rate_latent_cL Latent diagnostic coverage for LPDDR5 mode.
        """
        self.target_fault = target_fault
        is_lpddr5_mode = (dc_rate_latent_cL is not None)

        if is_lpddr5_mode:
            if not (0.0 <= dc_rate_c_or_cR <= 1.0) or not (0.0 <= dc_rate_latent_cL <= 1.0):
                raise ValueError("Diagnostic coverage rates must be between 0.0 and 1.0.")
            self.c_R = dc_rate_c_or_cR
            self.c_L = dc_rate_latent_cL
        else:
            if not (0.0 <= dc_rate_c_or_cR <= 1.0):
                raise ValueError("Diagnostic coverage rate must be between 0.0 and 1.0.")
            self.c_R = dc_rate_c_or_cR
            self.c_L = 1.0 - dc_rate_c_or_cR

    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        """
        Transforms the input rates by applying coverage to the target fault.

        @param spfm_rates Dictionary containing current SPFM/residual fault rates.
        @param lfm_rates Dictionary containing current LFM/latent fault rates.
        @return A tuple of updated (spfm_rates, lfm_rates) dictionaries.
        """
        new_spfm = spfm_rates.copy()
        new_lfm = lfm_rates.copy()
        
        if self.target_fault in new_spfm:
            lambda_in = new_spfm.pop(self.target_fault)
            
            lambda_rf = lambda_in * (1.0 - self.c_R)
            if lambda_rf > 0:
                new_spfm[self.target_fault] = new_spfm.get(self.target_fault, 0.0) + lambda_rf
            
            lambda_mpf_l = lambda_in * (1.0 - self.c_L)
            if lambda_mpf_l > 0:
                new_lfm[self.target_fault] = new_lfm.get(self.target_fault, 0.0) + lambda_mpf_l
        
        return new_spfm, new_lfm