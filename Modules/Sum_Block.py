class Sum_Block:
    
    def __init__(self, input: str, input_components: list):
       
        self.name = input
        self.input_components = input_components

    def compute_fit(self) -> float:
        
        lambda_sum = 0.0
        
        for component in self.input_components:
            try:
                lambda_sum += component.compute_fit()
            except AttributeError as e:
                print(f"Error in {self.name}: Input component is missing required method 'compute_fit()'. Details: {e}")
                pass 
        return lambda_sum