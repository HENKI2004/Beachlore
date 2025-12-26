"""Top-level system model for the LPDDR5 hardware architecture."""

# Copyright (c) 2025 Linus Held. All rights reserved.

from ...core import PipelineBlock, SumBlock
from ...system_base import SystemBase
from .bus_trim import BusTrim
from .dram_trim import DramTrim
from .events import Events
from .link_ecc import LinkEcc
from .other_components import OtherComponents
from .sec import Sec
from .sec_ded import SecDed
from .sec_ded_trim import SecDedTrim


class Lpddr5System(SystemBase):
    """Coordinates the connection of all sub-components and defines the overall system layout for LPDDR5."""

    def configure_system(self):
        """Defines the hierarchical structure of the LPDDR5 system.

        Constructs the main DRAM processing chain (Sources -> SEC -> TRIM -> BUS -> LINK -> SEC-DED -> TRIM)
        and merges it with other hardware components.
        """
        main_chain = PipelineBlock(
            "DRAM_Path",
            [
                Events("DRAM_Sources"),
                Sec("SEC"),
                DramTrim("TRIM"),
                BusTrim("BUS"),
                LinkEcc("LINK-ECC"),
                SecDed("SEC-DED"),
                SecDedTrim("SEC-DED-TRIM"),
            ],
        )

        self.system_layout = SumBlock(self.name, [main_chain, OtherComponents("Other_HW")])
