from Modules.Base import Base,FAULTS

class Other_Components(Base):

    def __init__(self, name: str, spfm_input: dict, lfm_input):
        
        self.source_rate = 96 

        
        super().__init__(name, spfm_input, lfm_input)

    def configure_blocks(self):
        
        # --- SPFM Blöcke ---
        self.spfm_source_blocks[FAULTS.OTH] = self.BasicEvent(FAULTS.OTH, self.source_rate)
        
