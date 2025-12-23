import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from Modules.Base import Base
from Modules.Faults import FAULTS
from Modules.Sum_Block import Sum_Block
from Modules.Pipeline_Block import Pipeline_Block
from Modules.Split_Block import Split_Block

class DRAM_TRIM(Base):
    def __init__(self, name: str):
        self.spfm_SBE_split = {FAULTS.SBE: 0.94}
        self.spfm_DBE_split = {FAULTS.SBE: 0.11, FAULTS.DBE: 0.89}
        self.spfm_TBE_split = {FAULTS.SBE: 0.009, FAULTS.DBE: 0.15, FAULTS.TBE: 0.83}
        self.lfm_SBE_split = {FAULTS.SBE: 0.94}
        self.lfm_DBE_split = {FAULTS.SBE: 0.11, FAULTS.DBE: 0.89}
        
        super().__init__(name)

    def configure_blocks(self):
        """
        Configures the root block using a Pipeline of Split blocks.
        """
        self.root_block = Sum_Block(self.name, [
            Split_Block("SPFM_SBE_Split", FAULTS.SBE, self.spfm_SBE_split, is_spfm=True),
            Split_Block("SPFM_DBE_Split", FAULTS.DBE, self.spfm_DBE_split, is_spfm=True),
            Split_Block("SPFM_TBE_Split", FAULTS.TBE, self.spfm_TBE_split, is_spfm=True),
            Split_Block("LFM_SBE_Split", FAULTS.SBE, self.lfm_SBE_split, is_spfm=False),
            Split_Block("LFM_DBE_Split", FAULTS.DBE, self.lfm_DBE_split, is_spfm=False)
        ])