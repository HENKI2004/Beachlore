from .Block_Interface import Block_Interface
from .Faults import FAULTS

class Coverage_Block(Block_Interface):
    def __init__(self, target_fault: FAULTS, dc_rate_c_or_cR: float, 
                 dc_rate_latent_cL: float = None, is_spfm: bool = True):
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