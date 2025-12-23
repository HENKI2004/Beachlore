from .Block_Interface import Block_Interface
from .Faults import FAULTS
from collections import defaultdict
from .Coverage_Block import Coverage_Block
from .Split_Block import Split_Block
from .Transformation_Block import Transformation_Block

class Sum_Block(Block_Interface):
    """
    Parallel block that aggregates FIT rates from multiple sub-blocks and manages path junctions.
    """
    def __init__(self, name: str, sub_blocks: list[Block_Interface]):
        """
        Initializes the sum block.

        @param name The descriptive name of the aggregation block.
        @param sub_blocks List of blocks whose results will be summed.
        """
        self.name = name
        self.sub_blocks = sub_blocks

    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        """
        Transforms the input fault rate dictionaries according to the block's specific logic.
        
        @param spfm_rates Dictionary containing current SPFM/residual fault rates.
        @param lfm_rates Dictionary containing current LFM/latent fault rates.
        @return A tuple of updated (spfm_rates, lfm_rates) dictionaries.
        """
        total_spfm = spfm_rates.copy()
        total_lfm = lfm_rates.copy()
        for block in self.sub_blocks:
            res_spfm, res_lfm = block.compute_fit(spfm_rates, lfm_rates)
            for fault in set(res_spfm.keys()) | set(spfm_rates.keys()):
                delta = res_spfm.get(fault, 0.0) - spfm_rates.get(fault, 0.0)
                if delta != 0: total_spfm[fault] = total_spfm.get(fault, 0.0) + delta
            for fault in set(res_lfm.keys()) | set(lfm_rates.keys()):
                delta = res_lfm.get(fault, 0.0) - lfm_rates.get(fault, 0.0)
                if delta != 0: total_lfm[fault] = total_lfm.get(fault, 0.0) + delta
        return total_spfm, total_lfm

    def to_dot(self, dot, input_ports: dict) -> dict:
        """
        Generates Graphviz visualization ports for the aggregation block.

        @param dot The Graphviz Digraph object to draw on.
        @param input_ports Mapping of fault types to their incoming node IDs.
        @return An updated dictionary with the output ports of this block.
        """
        rf_collect = defaultdict(list)
        lat_collect = defaultdict(list)
        
        consumed_rf = set()
        consumed_lat = set()
        
        for b in self.sub_blocks:
            if isinstance(b, (Coverage_Block, Split_Block)):
                fault = getattr(b, 'target_fault', None) or getattr(b, 'fault_to_split', None)
                if b.is_spfm: consumed_rf.add(fault)
                else: consumed_lat.add(fault)
            elif isinstance(b, Transformation_Block):
                consumed_rf.add(b.source)

        with dot.subgraph(name=f"cluster_sum_{id(self)}") as c:
            c.attr(label=self.name, style="dotted", color="gray80", fontcolor="gray50")
            
            for block in self.blocks if hasattr(self, 'blocks') else self.sub_blocks:
                res_ports = block.to_dot(c, input_ports)
                for fault, ports in res_ports.items():
                    in_p = input_ports.get(fault, {})
                    if ports.get('rf') and ports['rf'] != in_p.get('rf'):
                        rf_collect[fault].append(ports['rf'])
                    if ports.get('latent') and ports['latent'] != in_p.get('latent'):
                        lat_collect[fault].append(ports['latent'])
            
            final_ports = {}
            all_faults = set(input_ports.keys()) | set(rf_collect.keys()) | set(lat_collect.keys())
            
            for fault in all_faults:
                in_p = input_ports.get(fault, {'rf': None, 'latent': None})
                
                srcs_rf = list(set(rf_collect[fault]))
                if in_p['rf'] and fault not in consumed_rf:
                    srcs_rf.append(in_p['rf'])
                
                res_rf = None
                if len(srcs_rf) > 1:
                    j_id = f"sum_{fault.name}_rf_{id(self)}"
                    c.node(j_id, label="+", shape="circle", width="0.3", fixedsize="true", color="red", fontcolor="red", fontsize="10")
                    for s in srcs_rf: c.edge(s, j_id, color="red")
                    res_rf = j_id
                elif len(srcs_rf) == 1:
                    res_rf = srcs_rf[0]

                srcs_lat = list(set(lat_collect[fault]))
                if in_p['latent'] and fault not in consumed_lat:
                    srcs_lat.append(in_p['latent'])
                
                res_lat = None
                if len(srcs_lat) > 1:
                    j_id = f"sum_{fault.name}_lat_{id(self)}"
                    c.node(j_id, label="+", shape="circle", width="0.3", fixedsize="true", color="blue", fontcolor="blue", fontsize="10")
                    for s in srcs_lat: c.edge(s, j_id, color="blue", style="dashed")
                    res_lat = j_id
                elif len(srcs_lat) == 1:
                    res_lat = srcs_lat[0]
                
                final_ports[fault] = {'rf': res_rf, 'latent': res_lat}
                    
        return final_ports