from Modules.Core.Base import Base,FAULTS

class SEC(Base):

    def __init__(self, name: str, spfm_input: dict, lfm_input):
        
        self.SBE_DC_RESIDUAL = 1.0
        self.SBE_DC_LATENT = 0.0 
        
        self.DBE_TO_DBE_P = 0.83 
        self.DBE_TO_TBE_P = 0.17    
        self.SB_SCOURCE = 0.1
        
        super().__init__(name, spfm_input, lfm_input)

    def configure_blocks(self):

        # --- LFM Quellen ---
        self.lfm_source_blocks[FAULTS.SB] = self.BasicEvent(FAULTS.SB, self.SB_SCOURCE)
        
        # --- SPFM Coverage Blöcke ---
        self.spfm_coverage_blocks[FAULTS.SBE] = self.CoverageBlock(
            FAULTS.SBE, 
            self.SBE_DC_RESIDUAL, 
            self.SBE_DC_LATENT
        )
        
        # --- SPFM Split Blöcke ---
        self.spfm_split_blocks[FAULTS.DBE] = self.SplitBlock(
            FAULTS.DBE, 
            {FAULTS.DBE: self.DBE_TO_DBE_P, FAULTS.TBE: self.DBE_TO_TBE_P}
        )