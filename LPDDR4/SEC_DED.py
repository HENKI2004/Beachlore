import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from Modules.Base import Base
from Modules.Faults import FAULTS
from Modules.Sum_Block import Sum_Block
from Modules.Pipeline_Block import Pipeline_Block
from Modules.Basic_Event import Basic_Event
from Modules.Coverage_Block import Coverage_Block
from Modules.Transformation_Block import Transformation_Block 

class SEC_DED(Base):
    """
    Component for Single Error Correction and Double Error Detection (SEC-DED).
    """

    def __init__(self, name: str):
        # --- SPFM Parameters ---
        self.SBE_DC = 1.0         
        self.DBE_DC = 1.0         
        self.MBE_DC = 0.5         
        self.TBE_DC = 1.0         
        
        # TBE-Split to MBE
        self.TBE_SPLIT_TO_MBE = 0.56

        # --- LFM Parameters ---
        self.LFM_SBE_DC = 1.0    
        self.LFM_DBE_DC = 1.0     
        
        # --- Source Parameters ---
        self.SDB_SOURCE = 0.1     

        super().__init__(name)

    def configure_blocks(self):
        """
        Configures the root block as a pipeline. 
        Note: The order of Transformation and Coverage is crucial.
        """
        self.root_block = Sum_Block(self.name, [
            Basic_Event(FAULTS.SDB, self.SDB_SOURCE, is_spfm=False),

            Coverage_Block(FAULTS.SBE, self.LFM_SBE_DC, is_spfm=False),
            Coverage_Block(FAULTS.DBE, self.LFM_DBE_DC, is_spfm=False),
            
            Pipeline_Block("Transforme",[Transformation_Block(FAULTS.TBE, FAULTS.MBE, self.TBE_SPLIT_TO_MBE),]),
            
            Coverage_Block(FAULTS.SBE, self.SBE_DC),
            Coverage_Block(FAULTS.DBE, self.DBE_DC),
            Coverage_Block(FAULTS.TBE, self.TBE_DC),
            Coverage_Block(FAULTS.MBE, self.MBE_DC)
        ])
