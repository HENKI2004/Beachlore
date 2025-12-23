from .Block_Interface import Block_Interface
from .Faults import FAULTS

class Coverage_Block(Block_Interface):
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
    
# Modules/Coverage_Block.py
    def to_dot(self, dot, input_ports: dict) -> dict:
        node_id = f"cov_{self.target_fault.name}_{id(self)}"
        rf_pc = (1.0 - self.c_R) * 100
        lat_pc = (1.0 - self.c_L) * 100
        
        label = f'<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD PORT="rf" BGCOLOR="white">{rf_pc:.1f}%</TD>' \
                f'<TD PORT="latent" BGCOLOR="white">{lat_pc:.1f}%</TD></TR>' \
                f'<TR><TD COLSPAN="2" BGCOLOR="gray90"><B>Coverage</B></TD></TR></TABLE>>'
        dot.node(node_id, label=label, shape="none")

        new_ports = input_ports.copy()
        prev = input_ports.get(self.target_fault, {'rf': None, 'latent': None})

        if self.is_spfm:
            # Eingang: Der rote Pfad (Residual) geht in den Block hinein
            if prev.get('rf'):
                dot.edge(prev['rf'], node_id, color="red")
            
            # AUSGANG: Der Block teilt den Fehler nun auf!
            # Ab hier kommen sowohl der rote als auch der blaue Pfad aus diesem Block.
            new_ports[self.target_fault] = {
                'rf': f"{node_id}:rf",       # Linkes Kästchen (Residual-Anteil)
                'latent': f"{node_id}:latent" # Rechtes Kästchen (Abgedeckter/Latenter-Anteil)
            }
        else:
            # Falls der Block auf einem latenten Pfad operiert (z.B. 2nd Order Coverage)
            if prev.get('latent'):
                dot.edge(prev['latent'], node_id, color="blue", style="dashed")
            
            new_ports[self.target_fault] = {
                'rf': prev['rf'], 
                'latent': f"{node_id}:latent"
            }
        
        return new_ports