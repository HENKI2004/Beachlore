from Modules.Base import Base,FAULTS

class DRAM_TRIM(Base):
    """
    Specific Safety Element (SEC) for LPDDR4.
    Only defines the unique parameters and block connections.
    """
    def __init__(self, name: str, spfm_input: dict, lfm_input):
        
        self.spfm_SBE_split = {FAULTS.SBE:0.94 }  
        self.spfm_DBE_split = {FAULTS.SBE: 0.11 , FAULTS.DBE:0.89}
        self.spfm_TBE_split = {FAULTS.SBE:0.009,FAULTS.DBE:0.15,FAULTS.TBE:0.83}
        
        super().__init__(name, spfm_input, lfm_input)

    def configure_blocks(self):
        """
        Implements the abstract method to instantiate the blocks unique to SEC.
        """
        
        # --- SPFM Split Blocks ---
        self.spfm_split_blocks[FAULTS.SBE] = self.SplitBlock(
            FAULTS.SBE, 
            self.spfm_SBE_split
        )
        
        self.spfm_split_blocks[FAULTS.DBE] = self.SplitBlock(
            FAULTS.DBE, 
            self.spfm_DBE_split
        )
        
        self.spfm_split_blocks[FAULTS.TBE] = self.SplitBlock(
            FAULTS.TBE, 
            self.spfm_TBE_split
        )
        
        
        # --- LFM Split Blocks ---
        
        # ---Sum Blocks ---
        
    