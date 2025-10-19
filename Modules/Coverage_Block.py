class Coverage_Block:
    """
    Represents the Coverage block in the ISO 26262 hardware safety model.
    Corresponds to the 'Coverage' block from the Split'n'Cover methodology.
    It models a safety mechanism, splitting an incoming failure rate (lambda_in)
    into a Residual Fault (lambda_RF) and a Latent Fault (lambda_MPF,L) based
    on the Diagnostic Coverage (DC) rate.
    """

    def __init__(self, name: str, dc_rate: float):
        """
        Constructor for the CoverageBlock.

        Initializes the component with its name and its Diagnostic Coverage (DC) rate.
        The DC rate should be a float between 0.0 (0%) and 1.0 (100%).

        @param name: The identifier for this specific safety mechanism/coverage point.
        @param dc_rate: The Diagnostic Coverage (DC) rate (c), where 0.0 <= c <= 1.0.
        @throws ValueError: If the dc_rate is outside the valid range [0.0, 1.0].
        """
        if not (0.0 <= dc_rate <= 1.0):
            raise ValueError("Diagnostic Coverage rate (dc_rate) must be between 0.0 and 1.0.")
            
        self.name = name
        self.dc_rate = dc_rate 

    def compute_fit(self, lambda_in: float) -> dict:
        """
        Calculates the two output failure rates based on the input rate and the DC.

        This simulates the SystemC 'compute_fit' method, which reads the input
        rate and calculates the two output rates (RF and MPF,L).

        @param lambda_in: The incoming failure rate to be covered (in FIT).
        @return: A dictionary containing the two output rates:
                 { 'RF': lambda_RF, 'MPF_L': lambda_MPF_L }
        """
        c = self.dc_rate
        
        lambda_rf = lambda_in * (1.0 - c)
        
        lambda_mpf_l = lambda_in * c
        
        return {
            'RF': lambda_rf,
            'MPF_L': lambda_mpf_l
        }
