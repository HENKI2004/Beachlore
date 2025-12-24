from .Block_Interface import Block_Interface
from .Faults import FAULTS

class Split_Block(Block_Interface):
    """
    Distributes the FIT rate of a specific fault type across multiple other fault types 
    based on a defined distribution. [cite: 1]
    """

    def __init__(self, name: str, fault_to_split: FAULTS, distribution_rates: dict, is_spfm: bool = True):
        sum_of_rates = sum(distribution_rates.values())
        if sum_of_rates > 1.0 + 1e-9: 
            raise ValueError(f"Sum of distribution rates ({sum_of_rates:.4f}) must not exceed 1.0.")
            
        self.name = name
        self.fault_to_split = fault_to_split
        self.distribution_rates = distribution_rates
        self.is_spfm = is_spfm

    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        new_spfm = spfm_rates.copy()
        new_lfm = lfm_rates.copy()
        target_dict = new_spfm if self.is_spfm else new_lfm
        
        if self.fault_to_split in target_dict:
            original_rate = target_dict.pop(self.fault_to_split)
            for target_fault, probability in self.distribution_rates.items():
                split_rate = original_rate * probability
                target_dict[target_fault] = target_dict.get(target_fault, 0.0) + split_rate
        
        return new_spfm, new_lfm
    
    def to_dot(self, dot, input_ports: dict, spfm_in: dict = None, lfm_in: dict = None) -> dict:
        """
        Generates a square split block (72pt x 72pt) with precise vertical alignment. 
        """
        node_id = f"split_{self.name}_{id(self)}"
        
        # Lane-ID für vertikale Ausrichtung bestimmen (lane_FAULTNAME_rf/latent)
        path_type = 'rf' if self.is_spfm else 'latent'
        group_id = f"lane_{self.fault_to_split.name}_{path_type}"
        
        # Dynamische Berechnung der Zellenbreite für das 72pt Grid
        num_cells = len(self.distribution_rates)
        cell_width = 72 // num_cells
        
        cells = [f'<TD PORT="p_{tf.name}" WIDTH="{cell_width}" HEIGHT="40" BGCOLOR="white">'
                 f'<FONT POINT-SIZE="8">{p*100:.1f}%</FONT></TD>' 
                 for tf, p in self.distribution_rates.items()]
        
        # HTML-Tabelle auf 72x72 Punkte fixiert 
        label = f'''<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" WIDTH="72" HEIGHT="72" FIXEDSIZE="TRUE">
  <TR>{"".join(cells)}</TR>
  <TR>
    <TD COLSPAN="{num_cells}" WIDTH="72" HEIGHT="32" BGCOLOR="gray90">
      <FONT POINT-SIZE="9"><B>Split: {self.fault_to_split.name}</B></FONT>
    </TD>
  </TR>
</TABLE>>'''

        dot.node(node_id, label=label, shape="none", group=group_id)

        new_ports = input_ports.copy()
        prev_source = input_ports.get(self.fault_to_split, {'rf': None, 'latent': None})
        
        # Eingangspfeil: Unten Mitte des gesamten Blocks (:s) 
        if self.fault_to_split in input_ports:
            color = "red" if self.is_spfm else "blue"
            p_key = 'rf' if self.is_spfm else 'latent'
            if prev_source.get(p_key): 
                dot.edge(f"{prev_source[p_key]}", f"{node_id}:s", color=color, minlen="2")

        # Ausgangsports: Oben Mitte der jeweiligen Prozent-Zelle (:n) 
        for target_fault, prob in self.distribution_rates.items():
            port_ref = f"{node_id}:p_{target_fault.name}:n"
            prev_target = input_ports.get(target_fault, {'rf': None, 'latent': None})
            
            if self.is_spfm:
                new_ports[target_fault] = {'rf': port_ref, 'latent': prev_target.get('latent')}
            else:
                new_ports[target_fault] = {'rf': prev_target.get('rf'), 'latent': port_ref}
                
        return new_ports