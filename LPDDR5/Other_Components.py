# Beachlore/LPDDR5/Other_Components.py
from Modules.Base import Base,FAULTS

class Other_Components(Base):
    """
    Aktualisierter "Other"-Block (gemäß Steiner et al., 2025).
    Trägt eine pauschale RF-Rate von 9.5 FIT bei.
    """
    def __init__(self, name: str, spfm_input: dict, lfm_input):
        
        self.OTHER_RF_SOURCE = 9.5 # 
        
        super().__init__(name, spfm_input, lfm_input)

    def configure_blocks(self):
        """
        Instanziiert die Blöcke (nur eine RF-Quelle).
        """
        # Fügt 9.5 FIT direkt zum SPFM (Residual Fault) Output hinzu
        self.spfm_source_blocks[FAULTS.OTH] = self.BasicEvent(
            FAULTS.OTH, 
            self.OTHER_RF_SOURCE
        )