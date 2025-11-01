# Beachlore/Modules/Coverage_Block.py (Kombinierte Version)

class Coverage_Block:
    """
    Stellt den Coverage-Block in einer kombinierten Version dar,
    die sowohl für das LPDDR4- als auch für das LPDDR5-Paper funktioniert.

    Die Logik basiert auf den LPDDR5-Formeln (Steiner et al.):
    lambda_RF = lambda_in * (1 - c_R)
    lambda_MPF_L = lambda_in * (1 - c_L)
    
    Der LPDDR4-Fall (Uecker & Jung) wird darauf abgebildet.
    """

    def __init__(self, input: str, dc_rate_c_or_cR: float, dc_rate_latent_cL: float = None):
        """
        Konstruktor für den kombinierten CoverageBlock.

        ---
        ANWENDUNG:
        
        1. [cite_start]LPDDR5-Modus (Steiner et al.) [cite: 285-286, 288-292]:
           ZWEI Argumente (c_R, c_L) übergeben.
           Beispiel: Coverage_Block("SBE_COV", 1.0, 1.0)
                     -> c_R=1.0, c_L=1.0

        2. [cite_start]LPDDR4-Modus (Uecker & Jung) [cite: 149-152]:
           EIN Argument (c) übergeben.
           Beispiel: Coverage_Block("SBE_COV", 1.0)
                     -> c_R=1.0 (als c interpretiert)
                     -> c_L wird intern auf (1.0 - c) gesetzt
        ---

        @param input: Der Name des Eingangs (z.B. FAULTS.SBE).
        @param dc_rate_c_or_cR: Entspricht 'c' (LPDDR4) oder 'c_R' (LPDDR5).
        @param dc_rate_latent_cL: Entspricht 'c_L' (LPDDR5). Wenn None, wird LPDDR4-Logik aktiviert.
        """
        
        self.name = input
        is_lpddr5_mode = (dc_rate_latent_cL is not None)

        if is_lpddr5_mode:
            # --- LPDDR5-Modus (Zwei Parameter übergeben) ---
            c_R = dc_rate_c_or_cR
            c_L = dc_rate_latent_cL
            
            if not (0.0 <= c_R <= 1.0):
                raise ValueError(f"LPDDR5-Modus: Residual DC rate (c_R) '{c_R}' muss zwischen 0.0 und 1.0 liegen.")
            if not (0.0 <= c_L <= 1.0):
                raise ValueError(f"LPDDR5-Modus: Latent DC rate (c_L) '{c_L}' muss zwischen 0.0 und 1.0 liegen.")
            
            self.c_R = c_R
            self.c_L = c_L

        else:
            # --- LPDDR4-Modus (Nur ein Parameter übergeben) ---
            c = dc_rate_c_or_cR # Erster Parameter wird als 'c' interpretiert
            
            if not (0.0 <= c <= 1.0):
                raise ValueError(f"LPDDR4-Modus: Diagnostic Coverage rate (c) '{c}' muss zwischen 0.0 und 1.0 liegen.")

            # Wir bilden die LPDDR4-Logik auf die LPDDR5-Formeln ab:
            # Formel (LPDDR4): lambda_RF = lambda_in * (1 - c)
            # Ziel-Formel:    lambda_RF = lambda_in * (1 - c_R)
            # ==> c_R = c
            self.c_R = c
            
            # Formel (LPDDR4): lambda_MPF_L = lambda_in * c
            # Ziel-Formel:    lambda_MPF_L = lambda_in * (1 - c_L)
            # ==> c = 1 - c_L  =>  c_L = 1 - c
            self.c_L = 1.0 - c

    def compute_fit(self, lambda_in: float) -> dict:
        """
        Berechnet die Ausgaberaten. Die Logik ist für beide Modi identisch,
        da die LPDDR4-Parameter im Konstruktor auf die LPDDR5-Logik 
        umgerechnet ("gemappt") wurden.
        
        Logik:
        lambda_RF = lambda_in * (1 - c_R)
        lambda_MPF_L = lambda_in * (1 - c_L)
        """
        
        lambda_rf = lambda_in * (1.0 - self.c_R)
        lambda_mpf_l = lambda_in * (1.0 - self.c_L)
        
        return {
            'RF': lambda_rf,
            'MPF_L': lambda_mpf_l
        }