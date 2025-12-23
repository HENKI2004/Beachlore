from .Block_Interface import Block_Interface
from .Faults import FAULTS

class Transformation_Block(Block_Interface):
    """Überführt einen Anteil eines Fehlers in einen anderen, ohne das Original zu löschen."""
    def __init__(self, source_fault: FAULTS, target_fault: FAULTS, factor: float):
        self.source = source_fault
        self.target = target_fault
        self.factor = factor

    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        new_spfm = spfm_rates.copy()
        if self.source in new_spfm:
            transfer_rate = new_spfm[self.source] * self.factor
            new_spfm[self.target] = new_spfm.get(self.target, 0.0) + transfer_rate
        return new_spfm, lfm_rates.copy()
    
    def to_dot(self, dot, input_ports: dict) -> dict:
        """
        Erzeugt ein Rechteck mit dem Transfer-Faktor oben und 'Transformation' unten.
        Nutzt das Port-Dictionary für gezielte rote (SPFM) Pfeile.
        """
        node_id = f"trans_{self.source.name}_to_{self.target.name}_{id(self)}"
        percent = self.factor * 100
        
        # HTML-Tabelle mit Port "out" im Prozent-Kästchen oben
        label = f'''<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
  <TR>
    <TD PORT="out" BGCOLOR="white">{percent:.1f}%</TD>
  </TR>
  <TR>
    <TD BGCOLOR="gray90"><B>Transformation</B></TD>
  </TR>
</TABLE>>'''

        dot.node(node_id, label=label, shape="none")

        # Verbindung ziehen: Da deine Logik in compute_fit nur den SPFM-Pfad (Residual) 
        # transformiert, ziehen wir hier einen ROTEN Pfeil vom Quell-Fehler.
        if self.source in input_ports:
            source_node = input_ports[self.source]['rf']
            dot.edge(source_node, node_id, color="red", label="rf")

        # Rückgabewert: Wir aktualisieren das Port-Dictionary.
        # Der Residual-Pfad (rf) des Ziel-Fehlers kommt nun aus diesem Block.
        new_ports = input_ports.copy()
        
        # Wir erstellen/aktualisieren den Eintrag für den Target-Fault
        # Falls der Pfad latent weitergegeben wird, nehmen wir den alten Pfad der Quelle
        latent_source = input_ports.get(self.source, {}).get('latent', node_id)
        
        new_ports[self.target] = {
            'rf': f"{node_id}:out",
            'latent': latent_source
        }
        
        return new_ports