from Modules.Base import Base, FAULTS
from Modules.Pipeline_Block import Pipeline_Block
from Modules.Split_Block import Split_Block

class DRAM_TRIM(Base):
    def __init__(self, name: str, spfm_input: dict, lfm_input: dict):
        self.spfm_SBE_split = {FAULTS.SBE: 0.94}
        self.spfm_DBE_split = {FAULTS.SBE: 0.11, FAULTS.DBE: 0.89}
        self.spfm_TBE_split = {FAULTS.SBE: 0.009, FAULTS.DBE: 0.15, FAULTS.TBE: 0.83}
        self.lfm_SBE_split = {FAULTS.SBE: 0.94}
        self.lfm_DBE_split = {FAULTS.SBE: 0.11, FAULTS.DBE: 0.89}
        
        super().__init__(name, spfm_input, lfm_input)

    def configure_blocks(self):
        """
        Configures the root block using a Pipeline of Split blocks.
        """
        self.root_block = Pipeline_Block(self.name, [
            Split_Block("SPFM_SBE_Split", FAULTS.SBE, self.spfm_SBE_split, is_spfm=True),
            Split_Block("SPFM_DBE_Split", FAULTS.DBE, self.spfm_DBE_split, is_spfm=True),
            Split_Block("SPFM_TBE_Split", FAULTS.TBE, self.spfm_TBE_split, is_spfm=True),
            Split_Block("LFM_SBE_Split", FAULTS.SBE, self.lfm_SBE_split, is_spfm=False),
            Split_Block("LFM_DBE_Split", FAULTS.DBE, self.lfm_DBE_split, is_spfm=False)
        ])