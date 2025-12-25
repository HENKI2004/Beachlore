# 
#  @file Coverage_Block.py
#  @author Linus Held 
#  @brief Applies diagnostic coverage (DC) to fault rates.
#  @version 2.0
#  @date 2025-12-25
# 
#  @copyright Copyright (c) 2025 Linus Held. All rights reserved.
# 

from ..Interfaces.Block_Interface import Block_Interface
from ..Interfaces.Faults import FAULTS

class Coverage_Block(Block_Interface):
    """
    Applies diagnostic coverage (DC) to a fault type, splitting FIT rates into residual and latent components.
    """

    def __init__(self, target_fault: FAULTS, dc_rate_c_or_cR: float, 
                 dc_rate_latent_cL: float = None, is_spfm: bool = True):
        """
        Initializes the Coverage_Block with specific diagnostic coverage parameters.

        @param target_fault The fault type (Enum) to which coverage is applied.
        @param dc_rate_c_or_cR The diagnostic coverage for residual faults (c or cR).
        @param dc_rate_latent_cL Optional specific coverage for latent faults (cL).
        @param is_spfm Indicates if this block processes the SPFM/residual path.
        """
        self.target_fault = target_fault
        self.is_spfm = is_spfm 
        is_lpddr5_mode = (dc_rate_latent_cL is not None)
        if is_lpddr5_mode:
            self.c_R = dc_rate_c_or_cR
            self.c_L = dc_rate_latent_cL
        else:
            self.c_R = dc_rate_c_or_cR
            self.c_L = 1.0 - dc_rate_c_or_cR

    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        """
        Transforms the input fault rate dictionaries by applying diagnostic coverage logic.
        
        @param spfm_rates Dictionary containing current SPFM/residual fault rates.
        @param lfm_rates Dictionary containing current LFM/latent fault rates.
        @return A tuple of updated (spfm_rates, lfm_rates) dictionaries.
        """
        new_spfm = spfm_rates.copy()
        new_lfm = lfm_rates.copy()
        
        if self.is_spfm:
            if self.target_fault in new_spfm:
                lambda_in = new_spfm.pop(self.target_fault)
                lambda_rf = lambda_in * (1.0 - self.c_R)
                if lambda_rf > 0:
                    new_spfm[self.target_fault] = new_spfm.get(self.target_fault, 0.0) + lambda_rf
                lambda_mpf_l = lambda_in * (1.0 - self.c_L)
                if lambda_mpf_l > 0:
                    new_lfm[self.target_fault] = new_lfm.get(self.target_fault, 0.0) + lambda_mpf_l
        else:
            if self.target_fault in new_lfm:
                lambda_in = new_lfm.pop(self.target_fault)
                lambda_rem = lambda_in * (1.0 - self.c_R)
                if lambda_rem > 0:
                    new_lfm[self.target_fault] = lambda_rem
        
        return new_spfm, new_lfm