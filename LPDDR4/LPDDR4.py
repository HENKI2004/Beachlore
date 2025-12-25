# 
#  @file LPDDR4.py
#  @author Linus Held 
#  @brief Top-level system model for the LPDDR4 hardware architecture.
#  @version 2.0
#  @date 2025-12-25
# 
#  @copyright Copyright (c) 2025 Linus Held. All rights reserved.
# 

import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from Modules import System_Base
from Modules.Core import Pipeline_Block, Sum_Block
from Modules.Interfaces import FAULTS

from .Events import Events
from .SEC import SEC
from .DRAM_TRIM import DRAM_TRIM
from .BUS_TRIM import BUS_TRIM
from .SEC_DED import SEC_DED
from .SEC_DED_TRIM import SEC_DED_TRIM
from .Other_Components import Other_Components

class LPDDR4_System(System_Base):
    """
    Coordinates the connection of all sub-components and defines the overall system layout.
    """

    def configure_system(self):
        """
        Defines the hierarchical structure of the LPDDR4 system.
        Constructs the main DRAM processing chain and merges it with other hardware components.
        """
        main_chain = Pipeline_Block("DRAM_Path", [
            Events("Source"),
            # SEC("SEC"),
            # DRAM_TRIM("TRIM"),
            # BUS_TRIM("BUS"),
            # SEC_DED("SEC-DED"),
            # SEC_DED_TRIM("SEC-DED-TRIM")
        ])

        self.system_layout = Sum_Block(self.name, [
            main_chain,
            Other_Components("Other_HW")
        ])
