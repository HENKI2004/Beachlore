import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from Modules.Base import Base
from Modules.Faults import FAULTS
from Modules.Pipeline_Block import Pipeline_Block
from Modules.Sum_Block import Sum_Block
from Modules.Basic_Event import Basic_Event
from Modules.Coverage_Block import Coverage_Block
from Modules.Split_Block import Split_Block

class Events(Base):
    """
    Single Error Correction component for LPDDR4 using the new block architecture.
    """

    def __init__(self, name: str):
        DRAM_FIT = 2300.0

        self.FAULT_SBE = 0.7 * DRAM_FIT
        self.FAULT_DBE = 0.0748 * DRAM_FIT
        self.FAULT_MBE = 0.0748 * DRAM_FIT
        self.FAULT_WD = 0.0748 * DRAM_FIT
        
        super().__init__(name)

    def configure_blocks(self):
        """
        Configures the root block as a pipeline of LFM sources, SPFM coverage, and splits.
        """
        self.root_block = Sum_Block(self.name, [
            Basic_Event(FAULTS.SBE, self.FAULT_SBE, is_spfm=True),
            Basic_Event(FAULTS.DBE, self.FAULT_DBE, is_spfm=True),
            Basic_Event(FAULTS.MBE, self.FAULT_MBE, is_spfm=True),
            Basic_Event(FAULTS.WD, self.FAULT_WD, is_spfm=True),
        ])