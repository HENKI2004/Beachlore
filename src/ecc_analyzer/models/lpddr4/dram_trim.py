#
#  @file DRAM_TRIM.py
#  @author Linus Held
#  @brief Component for trimming and distributing failure rates for the DRAM hardware layer.
#  @version 2.0
#  @date 2025-12-25
#
#  @copyright Copyright (c) 2025 Linus Held. All rights reserved.
#

from ...core import Base, SplitBlock, SumBlock
from ...interfaces import FaultType


class DramTrim(Base):
    """
    Handles the redistribution of SBE, DBE, and TBE faults for both residual and latent paths.
    This component uses a Pipeline to ensure sequential execution of split operations.
    """

    def __init__(self, name: str):
        """
        Initializes the DRAM_TRIM component with hardware-specific split distribution parameters.

        @param name The descriptive name of the component.
        """
        self.spfm_SBE_split = {FaultType.SBE: 0.94}
        self.spfm_DBE_split = {FaultType.SBE: 0.11, FaultType.DBE: 0.89}
        self.spfm_TBE_split = {FaultType.SBE: 0.009, FaultType.DBE: 0.15, FaultType.TBE: 0.83}

        self.lfm_SBE_split = {FaultType.SBE: 0.94}
        self.lfm_DBE_split = {FaultType.SBE: 0.11, FaultType.DBE: 0.89}

        super().__init__(name)

    def configure_blocks(self):
        """
        Configures the root block as a pipeline of sequential split operations.
        Each split block redistributes the specified fault type according to the defined ratios.
        """
        self.root_block = SumBlock(
            self.name,
            [
                SplitBlock("SPFM_SBE_Split", FaultType.SBE, self.spfm_SBE_split, is_spfm=True),
                SplitBlock("SPFM_DBE_Split", FaultType.DBE, self.spfm_DBE_split, is_spfm=True),
                SplitBlock("SPFM_TBE_Split", FaultType.TBE, self.spfm_TBE_split, is_spfm=True),
                SplitBlock("LFM_SBE_Split", FaultType.SBE, self.lfm_SBE_split, is_spfm=False),
                SplitBlock("LFM_DBE_Split", FaultType.DBE, self.lfm_DBE_split, is_spfm=False),
            ],
        )
