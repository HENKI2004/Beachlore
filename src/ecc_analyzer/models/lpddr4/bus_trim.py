#
#  @file BUS_TRIM.py
#  @author Linus Held
#  @brief Component for trimming and distributing failure rates across the bus architecture.
#  @version 2.0
#  @date 2025-12-25
#
#  @copyright Copyright (c) 2025 Linus Held. All rights reserved.
#

from ...core import Base, BasicEvent, SplitBlock, SumBlock
from ...interfaces import FaultType


class BusTrim(Base):
    """
    Component for trimming and distributing failure rates across the bus architecture.
    This module injects specific bus-related fault sources (MBE, AZ) and redistributes
    SBE, DBE, and TBE faults for both SPFM and LFM paths.
    Uses a Pipeline to ensure that sources are injected before sequential split operations occur.
    """

    def __init__(self, name: str):
        """
        Initializes the BUS_TRIM component with bus-specific split distribution
        parameters and additional fault source rates.

        @param name The descriptive name of the component.
        """
        self.spfm_SBE_split = {FaultType.SBE: 0.438}
        self.spfm_DBE_split = {FaultType.SBE: 0.496, FaultType.DBE: 0.314}
        self.spfm_TBE_split = {FaultType.SBE: 0.325, FaultType.DBE: 0.419, FaultType.TBE: 0.175}

        self.lfm_SBE_split = {FaultType.SBE: 0.438}
        self.lfm_DBE_split = {FaultType.SBE: 0.496, FaultType.DBE: 0.314}

        self.spfm_MBE_Source = 2.3
        self.spfm_AZ_Source = 172

        super().__init__(name)

    def configure_blocks(self):
        """
        Configures the root block as a pipeline of fault injections and sequential
        split operations.
        """

        self.root_block = SumBlock(
            self.name,
            [
                BasicEvent(FaultType.MBE, self.spfm_MBE_Source, is_spfm=True),
                BasicEvent(FaultType.AZ, self.spfm_AZ_Source, is_spfm=True),
                SplitBlock("SPFM_SBE_Split", FaultType.SBE, self.spfm_SBE_split, is_spfm=True),
                SplitBlock("SPFM_DBE_Split", FaultType.DBE, self.spfm_DBE_split, is_spfm=True),
                SplitBlock("SPFM_TBE_Split", FaultType.TBE, self.spfm_TBE_split, is_spfm=True),
                SplitBlock("LFM_SBE_Split", FaultType.SBE, self.lfm_SBE_split, is_spfm=False),
                SplitBlock("LFM_DBE_Split", FaultType.DBE, self.lfm_DBE_split, is_spfm=False),
            ],
        )
