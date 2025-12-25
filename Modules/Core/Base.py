from abc import ABC, abstractmethod
from ..Interfaces.Block_Interface import Block_Interface

class Base(Block_Interface, ABC):
    """
    Abstract base class for hardware components, providing a structured way to define 
    internal logic clusters and standardized visualization interfaces.
    """

    def __init__(self, name: str):
        """
        Initializes the component and triggers the internal block configuration.

        @param name The descriptive name of the component.
        """
        self.name = name
        self.root_block: Block_Interface = None
        self.configure_blocks()

    @abstractmethod
    def configure_blocks(self):
        """
        Abstract method to define the internal logic structure (root block) of the component.
        Must be implemented by subclasses.
        """
        pass

    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        """
        Delegates the FIT rate transformation to the internal root block.
        Allows the component to be used as a modular unit within a processing pipeline.

        @param spfm_rates Dictionary containing current SPFM/residual fault rates.
        @param lfm_rates Dictionary containing current LFM/latent fault rates.
        @return A tuple of updated (spfm_rates, lfm_rates) dictionaries.
        """
        if self.root_block is None:
            return spfm_rates.copy(), lfm_rates.copy()
        return self.root_block.compute_fit(spfm_rates, lfm_rates)
    
    def to_dot(self, dot, input_ports: dict = None) -> dict:
        """
        Generates Graphviz visualization clusters, including input/output interface boxes 
        and the internal logic blocks.

        @param dot The Graphviz Digraph object to draw on.
        @param input_ports Mapping of fault types to their incoming node IDs.
        @return An updated dictionary containing the outgoing interface ports of this component.
        """
        if input_ports is None: 
            input_ports = {}
        
        with dot.subgraph(name=f"cluster_{self.name}") as c:
            c.attr(label=self.name, style="filled", color="gray95")
            
            internal_in_ports = {}
            with c.subgraph() as s:
                s.attr(rank='same')
                for fault, ports in input_ports.items():
                    for path_type in ['rf', 'latent']:
                        if ports.get(path_type):
                            label = f"{fault.name}"
                            in_id = f"in_{self.name}_{fault.name}_{path_type}_{id(self)}"
                            color = "red" if path_type == 'rf' else "blue"
                            style = "solid"
                            
                            s.node(in_id, 
                                label=label, 
                                shape="box", 
                                style="filled", 
                                fillcolor="white", 
                                width="1",      
                                height="1",   
                                fixedsize="true",
                                group=f"lane_{fault.name}_{path_type}")
                            
                            dot.edge(ports[path_type], f"{in_id}:s", color=color, style=style)
                            
                            if fault not in internal_in_ports: 
                                internal_in_ports[fault] = {'rf': None, 'latent': None}
                            internal_in_ports[fault][path_type] = f"{in_id}:n"

            res_ports = self.root_block.to_dot(c, internal_in_ports) if self.root_block else internal_in_ports

            final_out_ports = {}
            with c.subgraph() as s:
                s.attr(rank='sink')
                for fault, ports in res_ports.items():
                    final_out_ports[fault] = {'rf': None, 'latent': None}
                    for path_type in ['rf', 'latent']:
                        if ports.get(path_type):
                            label = f"{fault.name}"
                            out_id = f"out_{self.name}_{fault.name}_{path_type}_{id(self)}"
                            color = "red" if path_type == 'rf' else "blue"
                            style = "solid"
                            
                            s.node(out_id, 
                                label=label, 
                                shape="box", 
                                style="filled", 
                                fillcolor="white", 
                                width="1",      
                                height="1",   
                                fixedsize="true",
                                group=f"lane_{fault.name}_{path_type}")
                            c.edge(ports[path_type], f"{out_id}:s", color=color, style=style, minlen='2')
                            final_out_ports[fault][path_type] = f"{out_id}:n"
                    
        return final_out_ports