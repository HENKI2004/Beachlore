from .Block_Interface import Block_Interface
from .Faults import FAULTS

class Transformation_Block(Block_Interface):
    """Überführt einen Anteil eines Fehlers in einen anderen, ohne das Original zu löschen."""
    def __init__(self, source_fault: FAULTS, target_fault: FAULTS, factor: float):
        self.source = source_fault
        self.target = target_fault
        self.factor = factor

    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        new_spfm = spfm_rates.copy()
        if self.source in new_spfm:
            transfer_rate = new_spfm[self.source] * self.factor
            new_spfm[self.target] = new_spfm.get(self.target, 0.0) + transfer_rate
        return new_spfm, lfm_rates.copy()