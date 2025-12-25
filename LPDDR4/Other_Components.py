# 
#  @file Other_Components.py
#  @author Linus Held 
#  @brief Component representing miscellaneous hardware parts with fixed FIT rates.
#  @version 2.0
#  @date 2025-12-25
# 
#  @copyright Copyright (c) 2025 Linus Held. All rights reserved.
# 

from Modules.Core import Base, Sum_Block, Basic_Event
from Modules.Interfaces import FAULTS

class Other_Components(Base):
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
        self.root_block = Sum_Block(self.name, [
            Basic_Event(FAULTS.OTH, self.source_rate, is_spfm=True)
        ])