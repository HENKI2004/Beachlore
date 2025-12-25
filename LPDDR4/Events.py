# 
#  @file Events.py
#  @author Linus Held 
#  @brief Primary failure rate source component for LPDDR4 DRAM.
#  @version 2.0
#  @date 2025-12-25
# 
#  @copyright Copyright (c) 2025 Linus Held. All rights reserved.
# 

from Modules.Core import Base, Sum_Block, Basic_Event
from Modules.Interfaces import FAULTS

class Events(Base):
    """
    Initializes the baseline DRAM failure rates.
    This module acts as a primary source for SBE, DBE, MBE, and WD faults.
    As a pure source component, it uses a Sum_Block to inject all rates in parallel.
    """

    def __init__(self, name: str):
        """
        Initializes the fault rates based on a baseline DRAM FIT value.

        @param name The descriptive name of the component.
        """
        dram_fit = 2300.0

        self.fault_sbe = 0.7 * dram_fit
        self.fault_dbe = 0.0748 * dram_fit
        self.fault_mbe = 0.0748 * dram_fit
        self.fault_wd = 0.0748 * dram_fit
        
        super().__init__(name)

    def configure_blocks(self):
        """
        Configures the internal block structure by injecting failure rates as basic events.
        Uses a Sum_Block as these faults occur independently and in parallel on the hardware level.
        """
        self.root_block = Sum_Block(self.name, [
            Basic_Event(FAULTS.SBE, self.fault_sbe, is_spfm=True),
            Basic_Event(FAULTS.DBE, self.fault_dbe, is_spfm=True),
            Basic_Event(FAULTS.MBE, self.fault_mbe, is_spfm=True),
            Basic_Event(FAULTS.WD, self.fault_wd, is_spfm=True),
        ])