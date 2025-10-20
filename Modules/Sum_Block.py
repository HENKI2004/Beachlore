class Sum_Block:
    """
    Represents the Sum block in the ISO 26262 hardware safety model.
    Corresponds to the 'Sum' block from the Split'n'Cover methodology.
    Its purpose is to compute the total failure rate from multiple incoming
    failure rates (lambdas).
    """
    
    def __init__(self, input: str, input_components: list):
        """
        Constructor for the SumBlock.

        Initializes the component with its name and references to all upstream
        components whose output rates must be summed.

        @param name: The identifier for this specific summation point.
        @param input_components: A list of objects that provide failure rates 
                                 via a get_output_rate() method.
        """
        self.name = input
        self.input_components = input_components

    def compute_fit(self) -> float:
        """
        Calculates the total failure rate (lambda_Sum) by summing the output
        rates of all connected upstream components.

        This simulates the SystemC 'compute_fit' method, which reads the input
        ports and writes the calculated sum to the output port.

        @return: The summed total failure rate (lambda_Sum) in FIT.
        """
        lambda_sum = 0.0
        
        for component in self.input_components:
            try:
                lambda_sum += component.get_output_rate()
            except AttributeError as e:
                print(f"Error in {self.name}: Input component is missing required method 'get_output_rate()'. Details: {e}")
                pass 
        return lambda_sum