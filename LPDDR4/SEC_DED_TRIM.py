# 
#  @file SEC_DED_TRIM.py
#  @author Linus Held 
#  @brief Component for trimming and distributing residual and latent fault rates after SEC-DED processing.
#  @version 2.0
#  @date 2025-12-25
# 
#  @copyright Copyright (c) 2025 Linus Held. All rights reserved.
# 

from Modules.Core import Base, Sum_Block, Split_Block
from Modules.Interfaces import FAULTS

class SEC_DED_TRIM(Base):
    """
    Component for trimming and distributing residual and latent fault rates after SEC-DED processing.
    This module chains sequential split operations for SBE, DBE, and TBE fault types.
    Uses a Pipeline_Block to ensure correct sequential processing and clear visual layout.
    """

    def __init__(self, name: str):
        """
        Initializes the SEC_DED_TRIM component with predefined split parameters for SPFM and LFM.

        @param name The descriptive name of the component.
        """
        self.spfm_SBE_split = {FAULTS.SBE: 0.89}
        self.spfm_DBE_split = {FAULTS.SBE: 0.20, FAULTS.DBE: 0.79}
        self.spfm_TBE_split = {FAULTS.SBE: 0.03, FAULTS.DBE: 0.27, FAULTS.TBE: 0.70}
        

        self.lfm_SBE_split = {FAULTS.SBE: 0.89}
        self.lfm_DBE_split = {FAULTS.SBE: 0.20, FAULTS.DBE: 0.79}
        self.lfm_TBE_split = {FAULTS.SBE: 0.03, FAULTS.DBE: 0.27, FAULTS.TBE: 0.70}
        
        super().__init__(name)

    def configure_blocks(self):
        """
        Configures the root block as a pipeline of sequential split operations for both SPFM and LFM paths.
        The Pipeline_Block ensures that transformations are applied step-by-step.
        """
        self.root_block = Sum_Block(self.name, [
            Split_Block("SPFM_SBE_Split", FAULTS.SBE, self.spfm_SBE_split, is_spfm=True),
            Split_Block("SPFM_DBE_Split", FAULTS.DBE, self.spfm_DBE_split, is_spfm=True),
            Split_Block("SPFM_TBE_Split", FAULTS.TBE, self.spfm_TBE_split, is_spfm=True),
            
            Split_Block("LFM_SBE_Split", FAULTS.SBE, self.lfm_SBE_split, is_spfm=False),
            Split_Block("LFM_DBE_Split", FAULTS.DBE, self.lfm_DBE_split, is_spfm=False),
            Split_Block("LFM_TBE_Split", FAULTS.TBE, self.lfm_TBE_split, is_spfm=False)
        ])