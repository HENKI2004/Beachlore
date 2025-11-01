class Split_Block:
    """
    Represents the Split block in the ISO 26262 hardware safety model.
    Corresponds to the 'Split' block from the Split'n'Cover methodology.
    It distributes an incoming failure rate (lambda_in) into multiple 
    paths (outputs) based on predefined probability rates (p_i). The remaining 
    rate is categorized as Safe Faults (lambda_S).
    """
    
    def __init__(self, input: str, distribution_rates: dict):
        """
        Constructor for the SplitBlock.

        Initializes the component with its name and the specific distribution rates
        for each output path. The sum of all distribution rates must be <= 1.0.

        @param name: The identifier for this specific fault splitting point.
        @param distribution_rates: A dictionary where keys are output fault types 
                                   (e.g., 'DBE', 'TBE') and values are their 
                                   corresponding probability rates (p_i).
        @throws ValueError: If the sum of distribution_rates exceeds 1.0.
        """
        sum_of_rates = sum(distribution_rates.values())
        
        if sum_of_rates > 1.0 + 1e-9: 
            raise ValueError(f"Sum of distribution rates ({sum_of_rates:.4f}) must not exceed 1.0.")
            
        self.name = input
        self.distribution_rates = distribution_rates  
        self.sum_of_rates = sum_of_rates

    def compute_fit(self, lambda_in: float) -> dict:
        """
        Calculates the distributed failure rates for all output paths, plus the 
        Safe Fault rate.

        This simulates the SystemC 'compute_fit' method, calculating the output 
        rates based on the input rate and distribution ratios.

        @param lambda_in: The incoming failure rate to be split (in FIT).
        @return: A dictionary containing all distributed rates and the Safe Fault rate:
                 { 'Output_1': lambda_1, 'Output_2': lambda_2, ..., 'Safe': lambda_S }
        """
        results = {}
        
        for output_name, p_i in self.distribution_rates.items():
            lambda_i = lambda_in * p_i
            results[output_name] = lambda_i
        
        return results