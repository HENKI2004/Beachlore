from Modules.Base import Base,FAULTS

class SEC_DED_TRIM(Base):
    """
    Stellt den SEC-DED-TRIM-Block aus Abbildung 3 dar.
    Modelliert die Redundanzentfernung und die damit verbundene Neuverteilung 
    von Fehlern (Split-Operationen).
    """
    def __init__(self, name: str, spfm_input: dict, lfm_input):
        
        # --- SPFM Split-Parameter ---
        self.spfm_SBE_split = {FAULTS.SBE: 0.89}
        self.spfm_DBE_split = {FAULTS.SBE: 0.20, FAULTS.DBE: 0.79}
        self.spfm_TBE_split = {FAULTS.SBE: 0.03, FAULTS.DBE: 0.27, FAULTS.TBE: 0.70}
        
        # --- LFM Split-Parameter (identisch zur SPFM-Logik) ---
        
        super().__init__(name, spfm_input, lfm_input)

    def configure_blocks(self):
        """
        Instanziiert die Split-Blöcke für SEC-DED-TRIM.
        """
        
        # --- SPFM Split Blöcke ---
        self.spfm_split_blocks[FAULTS.SBE] = self.SplitBlock(FAULTS.SBE, self.spfm_SBE_split)
        self.spfm_split_blocks[FAULTS.DBE] = self.SplitBlock(FAULTS.DBE, self.spfm_DBE_split)
        self.spfm_split_blocks[FAULTS.TBE] = self.SplitBlock(FAULTS.TBE, self.spfm_TBE_split)
        
        # --- LFM Split Blöcke ---
