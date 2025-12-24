from .Faults import FAULTS

class ASIL_Block:
    """
    Evaluates final system metrics and determines the achieved ASIL level according to ISO 26262 requirements.
    """

    ASIL_REQUIREMENTS = {
        "D": [0.99, 0.90, 10.0],
        "C": [0.97, 0.80, 100.0],
        "B": [0.90, 0.60, 100.0],
        "A": [0.00, 0.00, 1000.0]
    }

    def __init__(self, name: str):
        """
        Initializes the ASIL calculation block.

        @param name The descriptive name of the calculation block.
        """
        self.name = name

    def _determine_asil(self, spfm: float, lfm: float, lambda_rf_sum: float) -> str:
        """
        Determines the achieved ASIL level based on calculated metrics.

        @param spfm Single-Point Fault Metric value (0.0 to 1.0).
        @param lfm Latent Fault Metric value (0.0 to 1.0).
        @param lambda_rf_sum Total sum of residual FIT rates.
        @return A string representing the achieved ASIL level or QM.
        """
        for asil_level in ["D", "C", "B"]:
            req = self.ASIL_REQUIREMENTS[asil_level]
            spfm_min, lfm_min, rf_max = req
            if (spfm >= spfm_min and lfm >= lfm_min and lambda_rf_sum < rf_max):
                return f"ASIL {asil_level}"

        if lambda_rf_sum < self.ASIL_REQUIREMENTS["A"][2]:
            return "ASIL A"

        return "QM (Quality Management)"

    def compute_metrics(self, lambda_total: float, final_spfm_dict: dict, final_lfm_dict: dict) -> dict:
        """
        Calculates final ISO 26262 metrics using result dictionaries from the block chain.

        @param lambda_total The total FIT rate of the entire system.
        @param final_spfm_dict Dictionary containing final residual and dangerous FIT rates.
        @param final_lfm_dict Dictionary containing final latent FIT rates.
        @return A dictionary containing SPFM, LFM, Residual FIT sum, and the achieved ASIL level.
        """
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
        Aggregates all SPFM and LFM paths into central junction nodes and 
        places the calculation block at the top of the graph.

        @param dot The Graphviz Digraph object to draw on.
        @param input_ports Mapping of fault types to their incoming node IDs.
        @return An empty dictionary as this is the final block in the chain.
        """
        node_id = f"asil_{id(self)}"
        
        all_rf_srcs = []
        all_lat_srcs = []
        for fault, ports in input_ports.items():
            if ports.get('rf'):
                all_rf_srcs.append(ports['rf'])
            if ports.get('latent'):
                all_lat_srcs.append(ports['latent'])

        with dot.subgraph(name=f"cluster_final_eval_{id(self)}") as c:
            c.attr(label="Final ASIL Evaluation", style="dashed", color="gray80", fontcolor="gray50")
            
            rf_sum_id = f"final_sum_rf_{id(self)}"
            lat_sum_id = f"final_sum_lat_{id(self)}"
            
            if all_rf_srcs:
                c.node(rf_sum_id, label="+", shape="circle", width="0.3", 
                       fixedsize="true", color="red", fontcolor="red", fontsize="10")
                for s in all_rf_srcs:
                    dot.edge(s, rf_sum_id, color="red",minlen="2")

            if all_lat_srcs:
                c.node(lat_sum_id, label="+", shape="circle", width="0.3", 
                       fixedsize="true", color="blue", fontcolor="blue", fontsize="10")
                for s in all_lat_srcs:
                    dot.edge(s, lat_sum_id, color="blue", minlen="2")

            with c.subgraph() as s:
                s.attr(rank='sink')
                s.node(node_id, label="Calculate ASIL Metrics", shape="rectangle", 
                       style="filled", fillcolor="white", penwidth="2")

            if all_rf_srcs:
                c.edge(rf_sum_id, node_id, color="red", penwidth="2")
            if all_lat_srcs:
                c.edge(lat_sum_id, node_id, color="blue", penwidth="2")
                
        return {}