# 
#  @file SEC.py
#  @author Linus Held 
#  @brief Component for Single Error Correction (SEC) in LPDDR4 architectures.
#  @version 2.0
#  @date 2025-12-25
# 
#  @copyright Copyright (c) 2025 Linus Held. All rights reserved.
# 

from Modules.Core import Base, Pipeline_Block, Sum_Block, Basic_Event, Coverage_Block, Split_Block
from Modules.Interfaces import FAULTS

class SEC(Base):
    """
    Component for Single Error Correction (SEC) in LPDDR4 architectures.
    This module handles SBE coverage and redistributes DBE failure rates.
    It uses a Pipeline_Block to ensure that local sources are added before 
    diagnostic coverage and split operations are applied.
    """

    def __init__(self, name: str):
        """
        Initializes the SEC component with specific diagnostic coverage and failure rates.

        @param name The descriptive name of the component.
        """
        self.SEC_ECC_DC = 1.0
        self.DBE_TO_DBE_P = 0.83
        self.DBE_TO_TBE_P = 0.17
        self.SB_SOURCE = 0.1
        self.DBE_SOURCE = 172
        super().__init__(name)

    def configure_blocks(self):
        """
        Configures the internal block structure as a sequential pipeline.
        This ensures fault sources are injected first, followed by coverage application 
        and final rate redistribution.
        """
        self.root_block = Sum_Block(self.name, [
            Basic_Event(FAULTS.SB, self.SB_SOURCE, is_spfm=False),
            Basic_Event(FAULTS.DBE, self.DBE_SOURCE, is_spfm=False),
            Coverage_Block(FAULTS.SBE, self.SEC_ECC_DC),
            Split_Block(
                "DBE_to_TBE_Split", 
                FAULTS.DBE, 
                {FAULTS.DBE: self.DBE_TO_DBE_P, FAULTS.TBE: self.DBE_TO_TBE_P}, 
                is_spfm=True
            )
        ])