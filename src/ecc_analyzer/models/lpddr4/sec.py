#
#  @file SEC.py
#  @author Linus Held
#  @brief Component for Single Error Correction (SEC) in LPDDR4 architectures.
#  @version 2.0
#  @date 2025-12-25
#
#  @copyright Copyright (c) 2025 Linus Held. All rights reserved.
#


from ...core import Base, BasicEvent, CoverageBlock, SplitBlock, SumBlock
from ...interfaces import FaultType


class Sec(Base):
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
        self.root_block = SumBlock(
            self.name,
            [
                BasicEvent(FaultType.SB, self.SB_SOURCE, is_spfm=False),
                BasicEvent(FaultType.DBE, self.DBE_SOURCE, is_spfm=False),
                CoverageBlock(FaultType.SBE, self.SEC_ECC_DC),
                SplitBlock(
                    "DBE_to_TBE_Split",
                    FaultType.DBE,
                    {FaultType.DBE: self.DBE_TO_DBE_P, FaultType.TBE: self.DBE_TO_TBE_P},
                    is_spfm=True,
                ),
            ],
        )
