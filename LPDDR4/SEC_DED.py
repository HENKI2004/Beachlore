from Modules.Base import Base,FAULTS

class SEC_DED(Base):
    """
    Stellt den SEC-DED-Block aus Abbildung 3 dar.
    Wendet Coverage auf SBE, DBE, TBE und MBE an.
    Fügt eine latente Fehlerquelle für den Ausfall des SEC-DED-Blocks hinzu.
    """
    def __init__(self, name: str, spfm_input: dict, lfm_input):
        
        # --- SPFM-Parameter ---
        self.SBE_DC = 1.0         # 100% Coverage für SBE
        self.DBE_DC = 1.0         # 100% Coverage für DBE
        self.MBE_DC = 0.5         # 50% Coverage für MBE
        self.TBE_DC = 1.0         # 100% Coverage für den TBE-Anteil
        
        # TBE-Split: 44% werden von TBE-Coverage (100%) abgedeckt, 56% werden zu MBE
        self.TBE_SPLIT_TO_MBE = 0.56

        # --- LFM-Parameter ---
        self.LFM_SBE_DC = 1.0     # 100% Coverage für latente SBE
        self.LFM_DBE_DC = 1.0     # 100% Coverage für latente DBE
        
        # --- Quellen-Parameter ---
        self.SDB_SOURCE = 0.1     # "SEC-DED Broken" latente Fehlerquelle

        super().__init__(name, spfm_input, lfm_input)

    def configure_blocks(self):
        """
        Instanziiert die Blöcke für SEC-DED.
        """
        
        # --- SPFM Blöcke ---
        self.spfm_coverage_blocks[FAULTS.SBE] = self.CoverageBlock(FAULTS.SBE, self.SBE_DC)
        self.spfm_coverage_blocks[FAULTS.DBE] = self.CoverageBlock(FAULTS.DBE, self.DBE_DC)
        self.spfm_coverage_blocks[FAULTS.TBE] = self.CoverageBlock(FAULTS.TBE, self.TBE_DC)
        self.spfm_coverage_blocks[FAULTS.MBE] = self.CoverageBlock(FAULTS.MBE, self.MBE_DC)
        
        
        self.spfm_split_blocks[FAULTS.TBE] = self.SplitBlock(
            FAULTS.TBE, 
            {FAULTS.MBE: self.TBE_SPLIT_TO_MBE}
        )
        
        # --- LFM Blöcke ---
        self.lfm_coverage_blocks[FAULTS.SBE] = self.CoverageBlock(FAULTS.SBE, self.LFM_SBE_DC)
        self.lfm_coverage_blocks[FAULTS.DBE] = self.CoverageBlock(FAULTS.DBE, self.LFM_DBE_DC)
        
        # --- LFM Quellen ---
        self.lfm_source_blocks[FAULTS.SDB] = self.BasicEvent(FAULTS.SDB, self.SDB_SOURCE)