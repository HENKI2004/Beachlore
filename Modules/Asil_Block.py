# Modules/Asil_Block.py
from .Faults import FAULTS

class ASIL_Block:
    """
    Evaluates final system metrics and determines the achieved ASIL level according to ISO 26262 requirements.
    """

    ASIL_REQUIREMENTS = {
        "D": [0.99, 0.90, 10.0],  # SPFM > 99%, LFM > 90%, RF < 10 FIT
        "C": [0.97, 0.80, 100.0], # SPFM > 97%, LFM > 80%, RF < 100 FIT
        "B": [0.90, 0.60, 100.0], # SPFM > 90%, LFM > 60%, RF < 100 FIT
        "A": [0.00, 0.00, 1000.0] # Only residual FIT limit applies for ASIL A
    }

    def __init__(self, name: str):
        self.name = name

    def _determine_asil(self, spfm: float, lfm: float, lambda_rf_sum: float) -> str:
        # ... (Berechnungslogik bleibt identisch) ...
        for asil_level in ["D", "C", "B"]:
            req = self.ASIL_REQUIREMENTS[asil_level]
            spfm_min, lfm_min, rf_max = req
            if (spfm >= spfm_min and lfm >= lfm_min and lambda_rf_sum < rf_max):
                return f"ASIL {asil_level}"
        if lambda_rf_sum < self.ASIL_REQUIREMENTS["A"][2]:
            return "ASIL A"
        return "QM (Quality Management)"

    def compute_metrics(self, lambda_total: float, final_spfm_dict: dict, final_lfm_dict: dict) -> dict:
        # ... (Berechnungslogik bleibt identisch) ...
        lambda_dangerous_sum = sum(final_spfm_dict.values())
        lambda_latent_sum = sum(final_lfm_dict.values())
        lambda_rf_sum = lambda_dangerous_sum
        spfm = 0.0
        lfm = 0.0
        if lambda_total > 0:
            spfm = 1.0 - (lambda_dangerous_sum / lambda_total)
        lambda_safe_and_covered = lambda_total - lambda_dangerous_sum
        if lambda_safe_and_covered > 0:
            lfm = 1.0 - (lambda_latent_sum / lambda_safe_and_covered)
        achieved_asil = self._determine_asil(spfm, lfm, lambda_rf_sum)
        return {
            'SPFM': spfm,
            'LFM': lfm,
            'Lambda_RF_Sum': lambda_rf_sum,
            'ASIL_Achieved': achieved_asil
        }
    
    def to_dot(self, dot, input_ports: dict) -> dict:
        """
        Führt alle SPFM- und LFM-Pfade visuell in zentralen Plus-Knoten zusammen 
        und platziert die Berechnung ganz oben im Graphen.
        """
        node_id = f"asil_{id(self)}"
        
        # 1. Sammle alle RF- und Latent-Ausgangspunkte aller Fehlertypen
        all_rf_srcs = []
        all_lat_srcs = []
        for fault, ports in input_ports.items():
            if ports.get('rf'):
                all_rf_srcs.append(ports['rf'])
            if ports.get('latent'):
                all_lat_srcs.append(ports['latent'])

        # 2. Erzeuge die Visualisierung
        with dot.subgraph(name=f"cluster_final_eval_{id(self)}") as c:
            c.attr(label="Final ASIL Evaluation", style="dashed", color="gray80", fontcolor="gray50")
            
            # Zentrale Summationspunkte (+)
            rf_sum_id = f"final_sum_rf_{id(self)}"
            lat_sum_id = f"final_sum_lat_{id(self)}"
            
            # Wir definieren die Plus-Knoten (unten im BT-Fluss innerhalb der Evaluation)
            if all_rf_srcs:
                c.node(rf_sum_id, label="+", shape="circle", width="0.3", 
                       fixedsize="true", color="red", fontcolor="red", fontsize="10")
                for s in all_rf_srcs:
                    dot.edge(s, rf_sum_id, color="red")

            if all_lat_srcs:
                c.node(lat_sum_id, label="+", shape="circle", width="0.3", 
                       fixedsize="true", color="blue", fontcolor="blue", fontsize="10")
                for s in all_lat_srcs:
                    dot.edge(s, lat_sum_id, color="blue", style="dashed")

            # Der ASIL Block wird ganz oben platziert (rank='sink')
            # Das 'rank' Attribut zwingt den Block an den oberen Rand der Komponente
            with c.subgraph() as s:
                s.attr(rank='sink')
                s.node(node_id, label="Calculate ASIL Metrics", shape="rectangle", 
                       style="filled", fillcolor="white", penwidth="2")

            # Finale Pfeile von den Plus-Symbolen zum ASIL Block
            if all_rf_srcs:
                c.edge(rf_sum_id, node_id, color="red", penwidth="2")
            if all_lat_srcs:
                c.edge(lat_sum_id, node_id, color="blue", style="dashed", penwidth="2")
                
        return {}