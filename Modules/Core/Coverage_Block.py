from ..Interfaces.Block_Interface import Block_Interface
from ..Interfaces.Faults import FAULTS

class Coverage_Block(Block_Interface):
    """
    Applies diagnostic coverage (DC) to a fault type, splitting FIT rates into residual and latent components.
    """

    def __init__(self, target_fault: FAULTS, dc_rate_c_or_cR: float, 
                 dc_rate_latent_cL: float = None, is_spfm: bool = True):
        self.target_fault = target_fault
        self.is_spfm = is_spfm 
        
        is_lpddr5_mode = (dc_rate_latent_cL is not None)
        if is_lpddr5_mode:
            self.c_R = dc_rate_c_or_cR
            self.c_L = dc_rate_latent_cL
        else:
            self.c_R = dc_rate_c_or_cR
            self.c_L = 1.0 - dc_rate_c_or_cR

    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        new_spfm = spfm_rates.copy()
        new_lfm = lfm_rates.copy()
        
        if self.is_spfm:
            if self.target_fault in new_spfm:
                lambda_in = new_spfm.pop(self.target_fault)
                lambda_rf = lambda_in * (1.0 - self.c_R)
                if lambda_rf > 0:
                    new_spfm[self.target_fault] = new_spfm.get(self.target_fault, 0.0) + lambda_rf
                lambda_mpf_l = lambda_in * (1.0 - self.c_L)
                if lambda_mpf_l > 0:
                    new_lfm[self.target_fault] = new_lfm.get(self.target_fault, 0.0) + lambda_mpf_l
        else:
            if self.target_fault in new_lfm:
                lambda_in = new_lfm.pop(self.target_fault)
                lambda_rem = lambda_in * (1.0 - self.c_R)
                if lambda_rem > 0:
                    new_lfm[self.target_fault] = lambda_rem
        
        return new_spfm, new_lfm
    
    def to_dot(self, dot, input_ports: dict, spfm_in: dict = None, lfm_in: dict = None) -> dict:
        """
        Generiert eine quadratische Coverage-Box (72pt x 72pt) mit präzisen Port-Ankern. 
        """
        node_id = f"cov_{self.target_fault.name}_{id(self)}"
        rf_pc = (1.0 - self.c_R) * 100
        lat_pc = (1.0 - self.c_L) * 100
        
        # Gesamthöhe = 40 (Oben) + 32 (Unten) = 72 Punkte (1.0 Zoll) 
        # Gesamtbreite = 72 Punkte (1.0 Zoll) 
        label = f'''<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" WIDTH="72" HEIGHT="72" FIXEDSIZE="TRUE">
  <TR>
    <TD PORT="rf" WIDTH="36" HEIGHT="40" BGCOLOR="white"><FONT POINT-SIZE="9">{rf_pc:.1f}%</FONT></TD>
    <TD PORT="latent" WIDTH="36" HEIGHT="40" BGCOLOR="white"><FONT POINT-SIZE="9">{lat_pc:.1f}%</FONT></TD>
  </TR>
  <TR>
    <TD COLSPAN="2" WIDTH="72" HEIGHT="32" BGCOLOR="gray90"><B>Coverage</B></TD>
  </TR>
</TABLE>>'''

        # Lane-Gruppe für die vertikale Flucht (SBE, DBE, etc.) 
        path_type = 'rf' if self.is_spfm else 'latent'
        group_id = f"lane_{self.target_fault.name}_{path_type}"

        dot.node(node_id, label=label, shape="none", group=group_id)

        new_ports = input_ports.copy()
        prev = input_ports.get(self.target_fault, {'rf': None, 'latent': None})

        if self.is_spfm:
            if prev.get('rf'):
                # Eingang: Unten Mitte der gesamten Tabelle (:s) 
                dot.edge(f"{prev['rf']}", f"{node_id}:s", color="red", minlen="2")
            
            # Ausgänge: Oben Mitte der jeweiligen Prozent-Zelle (:n) 
            new_ports[self.target_fault] = {
                'rf': f"{node_id}:rf:n",
                'latent': f"{node_id}:latent:n"
            }
        else:
            if prev.get('latent'):
                dot.edge(f"{prev['latent']}", f"{node_id}:s", color="blue", minlen="2")
            
            new_ports[self.target_fault] = {
                'rf': prev['rf'], 
                'latent': f"{node_id}:latent:n"
            }
        
        return new_ports