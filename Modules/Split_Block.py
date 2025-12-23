from .Block_Interface import Block_Interface
from .Faults import FAULTS

class Split_Block(Block_Interface):
    """
    Distributes the FIT rate of a specific fault type across multiple other fault types 
    based on a defined distribution.
    """

    def __init__(self, name: str, fault_to_split: FAULTS, distribution_rates: dict, is_spfm: bool = True):
        """
        Initializes the Split_Block with distribution parameters.

        @param name The name of the split block.
        @param fault_to_split The source fault type (Enum) to be divided.
        @param distribution_rates A dictionary mapping target fault types to their distribution probability.
        @param is_spfm Whether to perform the split on the SPFM dictionary (True) or LFM dictionary (False).
        """
        sum_of_rates = sum(distribution_rates.values())
        if sum_of_rates > 1.0 + 1e-9: 
            raise ValueError(f"Sum of distribution rates ({sum_of_rates:.4f}) must not exceed 1.0.")
            
        self.name = name
        self.fault_to_split = fault_to_split
        self.distribution_rates = distribution_rates
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
        
        if self.fault_to_split in target_dict:
            original_rate = target_dict.pop(self.fault_to_split)
            
            for target_fault, probability in self.distribution_rates.items():
                split_rate = original_rate * probability
                target_dict[target_fault] = target_dict.get(target_fault, 0.0) + split_rate
        
        return new_spfm, new_lfm
    
    def to_dot(self, dot, input_ports: dict) -> dict:
        """
        Generates Graphviz visualization ports for the split block.

        @param dot The Graphviz Digraph object to draw on.
        @param input_ports Mapping of fault types to their incoming node IDs.
        @return An updated dictionary with the output ports of this block.
        """
        node_id = f"split_{self.name}_{id(self)}"
        
        cells = [f'<TD PORT="p_{tf.name}" BGCOLOR="white">{p*100:.1f}%</TD>' 
                for tf, p in self.distribution_rates.items()]
        label = f'<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR>{"".join(cells)}</TR>' \
                f'<TR><TD COLSPAN="{len(cells)}" BGCOLOR="gray90"><B>Split: {self.fault_to_split.name}</B></TD></TR></TABLE>>'
        dot.node(node_id, label=label, shape="none")

        new_ports = input_ports.copy()
        prev_source = input_ports.get(self.fault_to_split, {'rf': None, 'latent': None})
        
        if self.fault_to_split in input_ports:
            if self.is_spfm:
                if prev_source.get('rf'): dot.edge(prev_source['rf'], node_id, color="red")
            else:
                if prev_source.get('latent'): dot.edge(prev_source['latent'], node_id, color="blue", style="dashed")

        for target_fault, prob in self.distribution_rates.items():
            port_ref = f"{node_id}:p_{target_fault.name}"
            prev_target = input_ports.get(target_fault, {'rf': None, 'latent': None})
            
            if self.is_spfm:
                new_ports[target_fault] = {'rf': port_ref, 'latent': prev_target.get('latent')}
            else:
                new_ports[target_fault] = {'rf': prev_target.get('rf'), 'latent': port_ref}
                
        return new_ports