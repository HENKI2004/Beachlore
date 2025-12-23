from abc import ABC, abstractmethod
from graphviz import Digraph
from .Pipeline_Block import Pipeline_Block
from .Sum_Block import Sum_Block
from .Asil_Block import ASIL_Block

class System_Base(ABC):
    def __init__(self, name: str, total_fit: float):
        self.name = name
        self.total_fit = total_fit
        self.system_layout = None  # Wird in configure_system definiert
        self.asil_block = ASIL_Block("Final_Evaluation")
        self.configure_system()

    @abstractmethod
    def configure_system(self):
        """Hier definieren Kinder-Klassen die Pipeline/Summen-Struktur."""
        pass

    def run_analysis(self):
        """Führt die mathematische FIT-Berechnung durch."""
        if not self.system_layout:
            raise ValueError("System layout is not configured.")
        
        # Start der Berechnung mit leeren Dictionaries
        final_spfm, final_lfm = self.system_layout.compute_fit({}, {})
        
        # Metriken berechnen
        return self.asil_block.compute_metrics(self.total_fit, final_spfm, final_lfm)

    def generate_pdf(self, filename: str = None):
        """Erzeugt die PDF-Visualisierung basierend auf deiner Test-Logik."""
        if filename is None:
            filename = f"output_{self.name}"
            
        dot = Digraph(comment=self.name)
        # Übernahme deiner bewährten Visualisierungs-Attribute
        dot.attr(rankdir='BT', splines='ortho', newrank='true', nodesep='0.6', ranksep='0.8')

        # Die gesamte Struktur in Dot umwandeln
        # Wir fügen den ASIL-Block visuell am Ende hinzu
        final_ports = self.system_layout.to_dot(dot, {})
        self.asil_block.to_dot(dot, final_ports)

        dot.render(filename, view=True, format='pdf')
        print(f"System-Visualisierung gespeichert als {filename}.pdf")