from .Block_Interface import Block_Interface
from .Faults import FAULTS

class Basic_Event(Block_Interface):
    """
    Represents a source of a fault (Basic Event) that injects a specific FIT rate into the system.
    """

    def __init__(self, fault_type: FAULTS, rate: float, is_spfm: bool = True):
        """
        Initializes the Basic_Event.
        
        @param fault_type The type of fault (Enum) this event produces.
        @param rate The FIT rate of this basic event.
        @param is_spfm Whether this rate counts towards SPFM (True) or LFM (False).
        """
        self.fault_type = fault_type
        self.lambda_BE = rate
        self.is_spfm = is_spfm

    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        """
        Adds the FIT rate of this event to the provided rate dictionaries.
        
        @param spfm_rates Dictionary containing current SPFM/residual fault rates.
        @param lfm_rates Dictionary containing current LFM/latent fault rates.
        @return A tuple of updated (spfm_rates, lfm_rates) dictionaries.
        """
        new_spfm = spfm_rates.copy()
        new_lfm = lfm_rates.copy()
        
        target_dict = new_spfm if self.is_spfm else new_lfm
        target_dict[self.fault_type] = target_dict.get(self.fault_type, 0.0) + self.lambda_BE
        
        return new_spfm, new_lfm
    
    def to_dot(self, dot, input_ports: dict) -> dict:
        # Nutze .name für ein saubereres Label (z.B. "SBE" statt "FAULTS.SBE")
        node_id = f"be_{self.fault_type.name}_{id(self)}"
        val = self.lambda_BE[0] if isinstance(self.lambda_BE, tuple) else self.lambda_BE
        label = f"{self.fault_type.name}\n{val:.2f}"
        dot.node(node_id, label=label, shape="circle")
        
        new_ports = input_ports.copy()
        
        # Bestehende Ports für diesen Fehlertyp abrufen oder mit None initialisieren.
        # Das stellt sicher, dass Pfade nur dann existieren, wenn sie eine Quelle haben.
        current_fault_ports = new_ports.get(self.fault_type, {'rf': None, 'latent': None}).copy()
        
        if self.is_spfm:
            # Nur den Residual-Pfad (rf) auf diesen Knoten setzen
            current_fault_ports['rf'] = node_id
        else:
            # Nur den Latenten-Pfad (latent) auf diesen Knoten setzen
            current_fault_ports['latent'] = node_id
            
        new_ports[self.fault_type] = current_fault_ports
        return new_ports