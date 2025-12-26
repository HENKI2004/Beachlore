#
#  @file SEC_DED_TRIM.py
#  @author Linus Held
#  @brief Component for trimming and distributing residual and latent fault rates after SEC-DED processing.
#  @version 2.0
#  @date 2025-12-25
#
#  @copyright Copyright (c) 2025 Linus Held. All rights reserved.
#

from ...core import Base, SplitBlock, SumBlock
from ...interfaces import FaultType


class SecDedTrim(Base):
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
        self.spfm_SBE_split = {FaultType.SBE: 0.89}
        self.spfm_DBE_split = {FaultType.SBE: 0.20, FaultType.DBE: 0.79}
        self.spfm_TBE_split = {FaultType.SBE: 0.03, FaultType.DBE: 0.27, FaultType.TBE: 0.70}

        self.lfm_SBE_split = {FaultType.SBE: 0.89}
        self.lfm_DBE_split = {FaultType.SBE: 0.20, FaultType.DBE: 0.79}
        self.lfm_TBE_split = {FaultType.SBE: 0.03, FaultType.DBE: 0.27, FaultType.TBE: 0.70}

        super().__init__(name)

    def configure_blocks(self):
        """
        Configures the root block as a pipeline of sequential split operations for both SPFM and LFM paths.
        The Pipeline_Block ensures that transformations are applied step-by-step.
        """
        self.root_block = SumBlock(
            self.name,
            [
                SplitBlock("SPFM_SBE_Split", FaultType.SBE, self.spfm_SBE_split, is_spfm=True),
                SplitBlock("SPFM_DBE_Split", FaultType.DBE, self.spfm_DBE_split, is_spfm=True),
                SplitBlock("SPFM_TBE_Split", FaultType.TBE, self.spfm_TBE_split, is_spfm=True),
                SplitBlock("LFM_SBE_Split", FaultType.SBE, self.lfm_SBE_split, is_spfm=False),
                SplitBlock("LFM_DBE_Split", FaultType.DBE, self.lfm_DBE_split, is_spfm=False),
                SplitBlock("LFM_TBE_Split", FaultType.TBE, self.lfm_TBE_split, is_spfm=False),
            ],
        )
