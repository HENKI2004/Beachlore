class Coverage_Block:
    

    def __init__(self, input: str, dc_rate_c_or_cR: float, dc_rate_latent_cL: float = None):
        
        self.name = input
        is_lpddr5_mode = (dc_rate_latent_cL is not None)

        if is_lpddr5_mode:
            # --- LPDDR5-Modus  ---
            c_R = dc_rate_c_or_cR
            c_L = dc_rate_latent_cL
            
            if not (0.0 <= c_R <= 1.0):
                raise ValueError(f"LPDDR5-Modus: Residual DC rate (c_R) '{c_R}' muss zwischen 0.0 und 1.0 liegen.")
            if not (0.0 <= c_L <= 1.0):
                raise ValueError(f"LPDDR5-Modus: Latent DC rate (c_L) '{c_L}' muss zwischen 0.0 und 1.0 liegen.")
            
            self.c_R = c_R
            self.c_L = c_L

        else:
            # --- LPDDR4-Modus ---
            c = dc_rate_c_or_cR 
            
            if not (0.0 <= c <= 1.0):
                raise ValueError(f"LPDDR4-Modus: Diagnostic Coverage rate (c) '{c}' muss zwischen 0.0 und 1.0 liegen.")

            self.c_R = c
            
            self.c_L = 1.0 - c

    def compute_fit(self, lambda_in: float) -> dict:
        
        lambda_rf = lambda_in * (1.0 - self.c_R)
        lambda_mpf_l = lambda_in * (1.0 - self.c_L)
        
        return {
            'RF': lambda_rf,
            'MPF_L': lambda_mpf_l
        }