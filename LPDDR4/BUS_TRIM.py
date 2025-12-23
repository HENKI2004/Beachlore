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
from Modules.Basic_Event import Basic_Event

class BUS_TRIM(Base):
    
    def __init__(self, name: str):
        
        self.spfm_SBE_split = {FAULTS.SBE: 0.438 }  
        self.spfm_DBE_split = {FAULTS.SBE: 0.496 , FAULTS.DBE:0.314}
        self.spfm_TBE_split = {FAULTS.SBE:0.325,FAULTS.DBE:0.419,FAULTS.TBE:0.175}
        
        self.lfm_SBE_split = {FAULTS.SBE: 0.438}
        self.lfm_DBE_split = {FAULTS.SBE: 0.496, FAULTS.DBE:0.314}
        
        self.spfm_MBE_Source = 2.3
        self.spfm_AZ_Source = 172
        
        super().__init__(name)

    def configure_blocks(self):
        """
        Configures the root block as a pipeline of fault injections and splits.
        """
        self.root_block = Sum_Block(self.name, [
            # 1. Sources (Basic Events) should generally come first to inject rates
            Basic_Event(FAULTS.MBE, self.spfm_MBE_Source, is_spfm=True),
            Basic_Event(FAULTS.AZ, self.spfm_AZ_Source, is_spfm=True),

            # 2. SPFM Splits
            Split_Block("SPFM_SBE_Split", FAULTS.SBE, self.spfm_SBE_split, is_spfm=True),
            Split_Block("SPFM_DBE_Split", FAULTS.DBE, self.spfm_DBE_split, is_spfm=True),
            Split_Block("SPFM_TBE_Split", FAULTS.TBE, self.spfm_TBE_split, is_spfm=True),

            # 3. LFM Splits
            Split_Block("LFM_SBE_Split", FAULTS.SBE, self.lfm_SBE_split, is_spfm=False),
            Split_Block("LFM_DBE_Split", FAULTS.DBE, self.lfm_DBE_split, is_spfm=False)
        ])