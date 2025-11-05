class Basic_Event:

    def __init__(self, output: str, rate: float):
        self.output = output
        self.lambda_BE = rate  

    def compute_fit(self) -> float:
        return self.lambda_BE