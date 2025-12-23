from .Block_Interface import Block_Interface
from .Faults import FAULTS

class Transformation_Block(Block_Interface):
    """
    Transfers a portion of one fault type's rate to another fault type without removing the original.
    """

    def __init__(self, source_fault: FAULTS, target_fault: FAULTS, factor: float):
        """
        Initializes the transformation block.

        @param source_fault The fault type from which the rate is taken.
        @param target_fault The fault type to which the rate is added.
        @param factor The multiplication factor applied to the source rate.
        """
        self.source = source_fault
        self.target = target_fault
        self.factor = factor

    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        """
        Transforms the input fault rate dictionaries according to the block's specific logic.

        @param spfm_rates Dictionary containing current SPFM/residual fault rates.
        @param lfm_rates Dictionary containing current LFM/latent fault rates.
        @return A tuple of updated (spfm_rates, lfm_rates) dictionaries.
        """
        new_spfm = spfm_rates.copy()
        if self.source in new_spfm:
            transfer_rate = new_spfm[self.source] * self.factor
            new_spfm[self.target] = new_spfm.get(self.target, 0.0) + transfer_rate
        return new_spfm, lfm_rates.copy()
    
    def to_dot(self, dot, input_ports: dict) -> dict:
        """
        Generates Graphviz visualization ports for the transformation block.

        @param dot The Graphviz Digraph object to draw on.
        @param input_ports Mapping of fault types to their incoming node IDs.
        @return An updated dictionary with the output ports of this block.
        """
        node_id = f"trans_{self.source.name}_to_{self.target.name}_{id(self)}"
        percent = self.factor * 100
        
        label = f'''<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
  <TR>
    <TD PORT="out" BGCOLOR="white">{percent:.1f}%</TD>
  </TR>
  <TR>
    <TD BGCOLOR="gray90"><B>Transformation</B></TD>
  </TR>
</TABLE>>'''

        dot.node(node_id, label=label, shape="none")

        if self.source in input_ports:
            source_rf = input_ports[self.source].get('rf')
            if source_rf:
                dot.edge(source_rf, node_id, color="red")

        new_ports = input_ports.copy()
        prev_target = input_ports.get(self.target, {'rf': None, 'latent': None})
        
        new_ports[self.target] = {
            'rf': f"{node_id}:out",
            'latent': prev_target.get('latent')
        }
        
        return new_ports