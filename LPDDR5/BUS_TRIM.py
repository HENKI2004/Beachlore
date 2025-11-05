from Modules.Base import Base,FAULTS

class BUS_TRIM(Base):

    def __init__(self, name: str, spfm_input: dict, lfm_input):
        
        self.spfm_SBE_split = {FAULTS.SBE: 0.438 }  
        self.spfm_DBE_split = {FAULTS.SBE: 0.496 , FAULTS.DBE:0.314}
        self.spfm_TBE_split = {FAULTS.SBE:0.325,FAULTS.DBE:0.419,FAULTS.TBE:0.175}
        
        self.spfm_AZ_Source = 172
        
        super().__init__(name, spfm_input, lfm_input)

    def configure_blocks(self):
        
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
        
        # ---SOURCE Blocks ---
        
        self.spfm_source_blocks[FAULTS.AZ] = self.BasicEvent(FAULTS.AZ,self.spfm_AZ_Source)

        #---Sum Blocks---#
        