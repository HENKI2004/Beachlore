class Split_Block:
    
    def __init__(self, input: str, distribution_rates: dict):
        
        sum_of_rates = sum(distribution_rates.values())
        
        if sum_of_rates > 1.0 + 1e-9: 
            raise ValueError(f"Sum of distribution rates ({sum_of_rates:.4f}) must not exceed 1.0.")
            
        self.name = input
        self.distribution_rates = distribution_rates  
        self.sum_of_rates = sum_of_rates

    def compute_fit(self, lambda_in: float) -> dict:
        
        results = {}
        
        for output_name, p_i in self.distribution_rates.items():
            lambda_i = lambda_in * p_i
            results[output_name] = lambda_i
        
        return results