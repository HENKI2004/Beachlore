# Modules/Base.py
from abc import ABC, abstractmethod
from .Block_Interface import Block_Interface

class Base(Block_Interface, ABC):
    def __init__(self, name: str):
        self.name = name
        self.root_block: Block_Interface = None
        self.configure_blocks()

    @abstractmethod
    def configure_blocks(self):
        pass

    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        """Ermöglicht es, die Komponente in einer Pipeline zu nutzen."""
        if self.root_block is None:
            return spfm_rates.copy(), lfm_rates.copy()
        return self.root_block.compute_fit(spfm_rates, lfm_rates)
    
    # Modules/Base.py
    def to_dot(self, dot, input_ports: dict = None) -> dict:
        if input_ports is None: input_ports = {}
        
        with dot.subgraph(name=f"cluster_{self.name}") as c:
            c.attr(label=self.name, style="filled", color="gray95")
            
            # 1. EINGANGS-INTERFACE (Getrennte Boxen für RF und L)
            internal_in_ports = {}
            with c.subgraph() as s:
                s.attr(rank='source')
                for fault, ports in input_ports.items():
                    # Wir erstellen hier zwei Ankerpunkte, damit die Linien getrennt reinkommen
                    for path_type in ['rf', 'latent']:
                        if ports.get(path_type):
                            label = f"{fault.name}\n({'RF' if path_type=='rf' else 'L'})"
                            in_id = f"in_{self.name}_{fault.name}_{path_type}_{id(self)}"
                            color = "red" if path_type == 'rf' else "blue"
                            style = "solid" if path_type == 'rf' else "dashed"
                            
                            s.node(in_id, label=label, shape="box", style="filled", fillcolor="white")
                            dot.edge(ports[path_type], in_id, color=color, style=style)
                            
                            if fault not in internal_in_ports: internal_in_ports[fault] = {'rf': None, 'latent': None}
                            internal_in_ports[fault][path_type] = in_id

            # 2. INTERNE LOGIK
            res_ports = self.root_block.to_dot(c, internal_in_ports) if self.root_block else internal_in_ports

            # 3. AUSGANGS-INTERFACE (Getrennte Boxen für RF und L)
            final_out_ports = {}
            with c.subgraph() as s:
                s.attr(rank='sink')
                for fault, ports in res_ports.items():
                    final_out_ports[fault] = {'rf': None, 'latent': None}
                    for path_type in ['rf', 'latent']:
                        if ports.get(path_type):
                            label = f"{fault.name}\n({'RF' if path_type=='rf' else 'L'})"
                            out_id = f"out_{self.name}_{fault.name}_{path_type}_{id(self)}"
                            color = "red" if path_type == 'rf' else "blue"
                            style = "solid" if path_type == 'rf' else "dashed"
                            
                            s.node(out_id, label=label, shape="box", style="filled", fillcolor="white")
                            c.edge(ports[path_type], out_id, color=color, style=style)
                            final_out_ports[fault][path_type] = out_id
                    
        return final_out_ports