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
    
    # Modules/Transformation_Block.py
    def to_dot(self, dot, input_ports: dict) -> dict:
        node_id = f"trans_{self.source.name}_to_{self.target.name}_{id(self)}"
        # ... (Label Code bleibt gleich) ...
        
        if self.source in input_ports:
            source_rf = input_ports[self.source].get('rf')
            if source_rf: dot.edge(source_rf, node_id, color="red")

        new_ports = input_ports.copy()
        # Bestehende Pfade des Ziel-Fehlers abrufen
        prev_target = input_ports.get(self.target, {'rf': None, 'latent': None})
        
        new_ports[self.target] = {
            'rf': f"{node_id}:out",
            'latent': prev_target.get('latent') # Behalte den L-Pfad des Ziels bei!
        }
        return new_ports