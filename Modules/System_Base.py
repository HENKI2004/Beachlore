from abc import ABC, abstractmethod
from graphviz import Digraph
from .Pipeline_Block import Pipeline_Block
from .Sum_Block import Sum_Block
from .Asil_Block import ASIL_Block

class System_Base(ABC):
    """
    Abstract base class for a safety system model, coordinating fault calculation and visualization.
    """

    def __init__(self, name: str, total_fit: float):
        """
        Initializes the system base.

        @param name The descriptive name of the system.
        @param total_fit The total FIT rate of the entire system.
        """
        self.name = name
        self.total_fit = total_fit
        self.system_layout = None 
        self.asil_block = ASIL_Block("Final_Evaluation")
        self.configure_system()

    @abstractmethod
    def configure_system(self):
        """
        Defines the internal structure (Pipeline or Sum blocks) of the system.
        Must be implemented by subclasses to specify how components are connected.
        """
        pass

    def run_analysis(self):
        """
        Performs the mathematical FIT calculation across the defined system layout.

        @return A dictionary containing calculated metrics (SPFM, LFM, ASIL level).
        """
        if not self.system_layout:
            raise ValueError("System layout is not configured.")
        
        final_spfm, final_lfm = self.system_layout.compute_fit({}, {})
        
        return self.asil_block.compute_metrics(self.total_fit, final_spfm, final_lfm)

    def generate_pdf(self, filename: str = None):
        """
        Generates a PDF visualization of the entire system architecture.

        @param filename Optional name for the output file. Defaults to "output_<name>".
        """
        if filename is None:
            filename = f"output_{self.name}"
            
        dot = Digraph(comment=self.name)
        dot.attr(rankdir='BT', splines='line', newrank='true', nodesep='1.0', ranksep='0.6')
        # line looks fine 
    

        dot.edge_attr.update(arrowhead='none')
        
        final_ports = self.system_layout.to_dot(dot, {})
        self.asil_block.to_dot(dot, final_ports)

        dot.render(filename, view=True, format='pdf')
        print(f"System visualization saved as {filename}.pdf")