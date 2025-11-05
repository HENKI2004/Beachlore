from Modules.Base import Base,FAULTS

class SEC(Base):
    
    def __init__(self, name: str, spfm_input: dict, lfm_input):
        
        self.SEC_ECC_DC = 1.0        # 100% Diagnostic Coverage for SBEs
        self.DBE_TO_DBE_P = 0.83     # 83% of DBEs remain DBEs
        self.DBE_TO_TBE_P = 0.17     # 17% of DBEs become Triple-Bit Errors (TBEs)
        self.SB_SCOURCE = 0.1
        self.DBE_SCOURCE = 172
        
        super().__init__(name, spfm_input, lfm_input)

    def configure_blocks(self):
        # --- LFM Source Blocks ---
        self.lfm_source_blocks[FAULTS.SB] = self.BasicEvent(FAULTS.SB, self.SB_SCOURCE)
        self.lfm_source_blocks[FAULTS.DBE] = self.BasicEvent(FAULTS.DBE, self.DBE_SCOURCE)
        
        # --- SPFM Coverage Blocks ---
        self.spfm_coverage_blocks[FAULTS.SBE] = self.CoverageBlock(FAULTS.SBE, self.SEC_ECC_DC)
        
        # --- SPFM Split Blocks ---
        self.spfm_split_blocks[FAULTS.DBE] = self.SplitBlock(
            FAULTS.DBE, 
            {FAULTS.DBE: self.DBE_TO_DBE_P, FAULTS.TBE: self.DBE_TO_TBE_P}
        )
        
        # ---Sum Blocks ---
    
    