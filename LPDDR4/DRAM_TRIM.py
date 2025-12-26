# 
#  @file DRAM_TRIM.py
#  @author Linus Held 
#  @brief Component for trimming and distributing failure rates for the DRAM hardware layer.
#  @version 2.0
#  @date 2025-12-25
# 
#  @copyright Copyright (c) 2025 Linus Held. All rights reserved.
# 

from Modules.Core import Base, Sum_Block, Split_Block
from Modules.Interfaces import FAULTS

class DRAM_TRIM(Base):
    """
    Handles the redistribution of SBE, DBE, and TBE faults for both residual and latent paths.
    This component uses a Pipeline to ensure sequential execution of split operations.
    """

    def __init__(self, name: str):
        """
        Initializes the DRAM_TRIM component with hardware-specific split distribution parameters.

        @param name The descriptive name of the component.
        """
        self.spfm_SBE_split = {FAULTS.SBE: 0.94}
        self.spfm_DBE_split = {FAULTS.SBE: 0.11, FAULTS.DBE: 0.89}
        self.spfm_TBE_split = {FAULTS.SBE: 0.009, FAULTS.DBE: 0.15, FAULTS.TBE: 0.83}
        
        self.lfm_SBE_split = {FAULTS.SBE: 0.94}
        self.lfm_DBE_split = {FAULTS.SBE: 0.11, FAULTS.DBE: 0.89}
        
        super().__init__(name)

    def configure_blocks(self):
        """
        Configures the root block as a pipeline of sequential split operations.
        Each split block redistributes the specified fault type according to the defined ratios.
        """
        self.root_block = Sum_Block(self.name, [
            Split_Block("SPFM_SBE_Split", FAULTS.SBE, self.spfm_SBE_split, is_spfm=True),
            Split_Block("SPFM_DBE_Split", FAULTS.DBE, self.spfm_DBE_split, is_spfm=True),
            Split_Block("SPFM_TBE_Split", FAULTS.TBE, self.spfm_TBE_split, is_spfm=True),

            Split_Block("LFM_SBE_Split", FAULTS.SBE, self.lfm_SBE_split, is_spfm=False),
            Split_Block("LFM_DBE_Split", FAULTS.DBE, self.lfm_DBE_split, is_spfm=False)
        ])