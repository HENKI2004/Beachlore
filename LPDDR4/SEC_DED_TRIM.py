from Modules.Base import Base
from Modules.Faults import FAULTS
from Modules.Pipeline_Block import Pipeline_Block
from Modules.Basic_Event import Basic_Event
from Modules.Coverage_Block import Coverage_Block
from Modules.Split_Block import Split_Block

class SEC_DED_TRIM(Base):

    def __init__(self, name: str, spfm_input: dict, lfm_input):
        
        # --- SPFM Split-Parameter ---
        self.spfm_SBE_split = {FAULTS.SBE: 0.89}
        self.spfm_DBE_split = {FAULTS.SBE: 0.20, FAULTS.DBE: 0.79}
        self.spfm_TBE_split = {FAULTS.SBE: 0.03, FAULTS.DBE: 0.27, FAULTS.TBE: 0.70}
        
        # --- LFM Split-Parameter ---
        self.lfm_SBE_split = {FAULTS.SBE: 0.89}
        self.lfm_DBE_split = {FAULTS.SBE: 0.20, FAULTS.DBE: 0.79}
        self.lfm_TBE_split = {FAULTS.SBE: 0.03, FAULTS.DBE: 0.27, FAULTS.TBE: 0.70}
        
        super().__init__(name, spfm_input, lfm_input)

    def configure_blocks(self):
        """
        Configures the root block as a pipeline of sequential split operations for both SPFM and LFM.
        """
        self.root_block = Pipeline_Block(self.name, [
            # SPFM Splits (Dangerous/Residual path)
            Split_Block("SPFM_SBE_Split", FAULTS.SBE, self.spfm_SBE_split, is_spfm=True),
            Split_Block("SPFM_DBE_Split", FAULTS.DBE, self.spfm_DBE_split, is_spfm=True),
            Split_Block("SPFM_TBE_Split", FAULTS.TBE, self.spfm_TBE_split, is_spfm=True),
            
            # LFM Splits (Latent path)
            Split_Block("LFM_SBE_Split", FAULTS.SBE, self.lfm_SBE_split, is_spfm=False),
            Split_Block("LFM_DBE_Split", FAULTS.DBE, self.lfm_DBE_split, is_spfm=False),
            Split_Block("LFM_TBE_Split", FAULTS.TBE, self.lfm_TBE_split, is_spfm=False)
        ])