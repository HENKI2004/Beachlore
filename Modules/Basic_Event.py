class Basic_Event:
    """
    Represents an internal fault source in the ISO 26262 hardware safety model.
    Corresponds to the 'Basic Event' block from the Split'n'Cover methodology.
    This module is initialized with a constant failure rate (lambda_BE) in FIT.
    """

    def __init__(self, name: str, rate: float):
        """
        Constructor for the BasicEvent block.

        Initializes the component with its name and its inherent failure rate.

        @param name: The identifier for this specific fault source.
        @param rate: The internal fault's failure rate (lambda_BE) in FIT.
        """
        self.name = name
        self.lambda_BE = rate  

    def get_output_rate(self) -> float:
        """
        Retrieves the failure rate of the Basic Event.

        This simulates the SystemC 'compute_fit' method, which writes the
        constant failure rate to the output port.

        @return: The Basic Event failure rate (lambda_BE) in FIT.
        """
        return self.lambda_BE