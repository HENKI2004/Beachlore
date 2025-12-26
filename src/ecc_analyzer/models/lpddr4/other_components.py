#
#  @file Other_Components.py
#  @author Linus Held
#  @brief Component representing miscellaneous hardware parts with fixed FIT rates.
#  @version 2.0
#  @date 2025-12-25
#
#  @copyright Copyright (c) 2025 Linus Held. All rights reserved.
#

from ...core import Base, BasicEvent, SumBlock
from ...interfaces import FaultType


class OtherComponents(Base):
    """
    Component representing miscellaneous hardware parts that contribute a fixed FIT rate to the system.
    This module encapsulates all non-DRAM components into a single source injection.
    """

    def __init__(self, name: str):
        """
        Initializes the component and sets the constant source FIT rate.

        @param name The descriptive name of the component.
        """
        self.source_rate = 96.0
        super().__init__(name)

    def configure_blocks(self):
        """
        Configures the root block to inject the FIT rate as a residual fault (SPFM).
        Uses a Sum_Block as the base container for the fault source.
        """
        self.root_block = SumBlock(self.name, [BasicEvent(FaultType.OTH, self.source_rate, is_spfm=True)])
