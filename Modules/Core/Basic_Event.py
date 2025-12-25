from ..Interfaces.Block_Interface import Block_Interface
from ..Interfaces.Faults import FAULTS

class Basic_Event(Block_Interface):
    """
    Represents a source of a fault (Basic Event) that injects a specific FIT rate into the system.
    """

    def __init__(self, fault_type: FAULTS, rate: float, is_spfm: bool = True):
        """
        Initializes the Basic_Event fault source.
        
        @param fault_type The type of fault (Enum) this event produces.
        @param rate The FIT rate of this basic event.
        @param is_spfm Whether this rate counts towards SPFM (True) or LFM (False).
        """
        self.fault_type = fault_type
        self.lambda_BE = rate
        self.is_spfm = is_spfm

    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        """
        Transforms the input fault rate dictionaries according to the block's specific logic.
        
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
        """
        Generates Graphviz visualization ports for the basic event.

        @param dot The Graphviz Digraph object to draw on.
        @param input_ports Mapping of fault types to their incoming node IDs.
        @return An updated dictionary containing the outgoing ports of this block.
        """
        node_id = f"be_{self.fault_type.name}_{id(self)}"
        val = self.lambda_BE[0] if isinstance(self.lambda_BE, tuple) else self.lambda_BE
        label = f"{self.fault_type.name}\n{val:.2f}"

        path_type = 'rf' if self.is_spfm else 'latent'
        #group_id = f"lane_{self.fault_type.name}_{path_type}"

        dot.node(node_id, label=label, shape="circle", 
                 width="1.0", height="1.0", fixedsize="true", 
                 #group=group_id
                 )
        
        new_ports = input_ports.copy()
        current_fault_ports = new_ports.get(self.fault_type, {'rf': None, 'latent': None}).copy()
        
        if self.is_spfm:
            current_fault_ports['rf'] = f"{node_id}:n"
        else:
            current_fault_ports['latent'] = f"{node_id}:n"
            
        new_ports[self.fault_type] = current_fault_ports
        return new_ports