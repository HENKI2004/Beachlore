from Modules.Base import Base,FAULTS

class Other_Components(Base):
    """
    Stellt den "Other"-Block aus Abbildung 3 dar.
    Dies ist eine zusätzliche Fehlerquelle, die ebenfalls durch 
    eine Sicherheitsmaßnahme abgedeckt wird.
    """
    def __init__(self, name: str, spfm_input: dict, lfm_input):
        
        self.source_rate = 96 # Aus dram-metrics-example.cpp

        
        super().__init__(name, spfm_input, lfm_input)

    def configure_blocks(self):
        """
        Instanziiert die Blöcke für die "Other" Komponente.
        """
        
        # --- SPFM Blöcke ---
        # 1. Eine Quelle (BasicEvent)
        self.spfm_source_blocks[FAULTS.OTH] = self.BasicEvent(FAULTS.OTH, self.source_rate)
        
