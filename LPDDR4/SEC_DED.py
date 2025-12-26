# 
#  @file SEC_DED.py
#  @author Linus Held 
#  @brief Component for Single Error Correction and Double Error Detection (SEC-DED).
#  @version 2.0
#  @date 2025-12-25
# 
#  @copyright Copyright (c) 2025 Linus Held. All rights reserved.
# 

from Modules.Core import Base, Pipeline_Block, Sum_Block, Basic_Event, Coverage_Block, Transformation_Block
from Modules.Interfaces import FAULTS

class SEC_DED(Base):
    """
    Component for Single Error Correction and Double Error Detection (SEC-DED).
    This module manages diagnostic coverage for multiple fault types and handles 
    transformations between failure modes.
    Uses a Pipeline_Block to enforce the sequence of injection, transformation, and coverage.
    """

    def __init__(self, name: str):
        """
        Initializes the SEC-DED component with specific diagnostic coverage and source parameters.

        @param name The descriptive name of the component.
        """
        self.SBE_DC = 1.0          
        self.DBE_DC = 1.0          
        self.MBE_DC = 0.5          
        self.TBE_DC = 1.0          
        
        self.TBE_SPLIT_TO_MBE = 0.56
        
        self.LFM_SBE_DC = 1.0     
        self.LFM_DBE_DC = 1.0      
        
        self.SDB_SOURCE = 0.1     

        super().__init__(name)

    def configure_blocks(self):
        """
        Configures the internal block structure as a sequential pipeline.
        This ensures that local sources are added before transformations occur, 
        and all rates are finally filtered by the coverage blocks.
        """
        self.root_block = Sum_Block(self.name, [
            Basic_Event(FAULTS.SDB, self.SDB_SOURCE, is_spfm=False),
            
            Coverage_Block(FAULTS.SBE, self.LFM_SBE_DC, is_spfm=False),
            Coverage_Block(FAULTS.DBE, self.LFM_DBE_DC, is_spfm=False),
            
            Transformation_Block(FAULTS.TBE, FAULTS.MBE, self.TBE_SPLIT_TO_MBE),
            
            Coverage_Block(FAULTS.SBE, self.SBE_DC),
            Coverage_Block(FAULTS.DBE, self.DBE_DC),
            Coverage_Block(FAULTS.TBE, self.TBE_DC),
            Coverage_Block(FAULTS.MBE, self.MBE_DC)
        ])