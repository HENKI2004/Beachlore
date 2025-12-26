"""Exposes the LPDDR5 specific hardware components and system model."""

# Copyright (c) 2025 Linus Held. All rights reserved.

from .bus_trim import BusTrim
from .dram_trim import DramTrim
from .events import Events
from .link_ecc import LinkEcc
from .lpddr5_system import Lpddr5System
from .other_components import OtherComponents
from .sec import Sec
from .sec_ded import SecDed
from .sec_ded_trim import SecDedTrim

__all__ = [
    "BusTrim",
    "DramTrim",
    "Events",
    "Lpddr5System",
    "OtherComponents",
    "Sec",
    "SecDed",
    "SecDedTrim",
    "LinkEcc",
]
