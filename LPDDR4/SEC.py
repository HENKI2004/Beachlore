from Modules.Base import Base

class SEC(Base):
    """
    Specific Safety Element (SEC) for LPDDR4.
    Only defines the unique parameters and block connections.
    """
    def __init__(self, name: str, spfm_input: dict, lfm_input):
        
        self.SEC_ECC_DC = 1.0        # 100% Diagnostic Coverage for SBEs
        self.DBE_TO_DBE_P = 0.83     # 83% of DBEs remain DBEs
        self.DBE_TO_TBE_P = 0.17     # 17% of DBEs become Triple-Bit Errors (TBEs)
        self.SB_SCOURCE = 0.1
        self.DBE_SCOURCE = 172
        
        super().__init__(name, spfm_input, lfm_input)

    def configure_blocks(self):
        """
        Implements the abstract method to instantiate the blocks unique to SEC.
        """
        # --- LFM Source Blocks ---
        self.lfm_source_blocks['SB'] = self.BasicEvent("SB", self.SB_SCOURCE)
        self.lfm_source_blocks['DBE'] = self.BasicEvent("DBE", self.DBE_SCOURCE)
        
        # --- SPFM Coverage Blocks ---
        self.spfm_coverage_blocks['SBE'] = self.CoverageBlock("SBE", self.SEC_ECC_DC)
        
        # --- SPFM Split Blocks ---
        self.spfm_split_blocks['DBE'] = self.SplitBlock(
            "DBE", 
            {'DBE': self.DBE_TO_DBE_P, 'TBE': self.DBE_TO_TBE_P}
        )
    
    