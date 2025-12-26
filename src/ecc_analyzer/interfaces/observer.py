"""Defines the abstract observer interface for safety analysis visualization."""

# Copyright (c) 2025 Linus Held. All rights reserved.

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .fault_type import FaultType

if TYPE_CHECKING:
    from .block_interface import BlockInterface


class SafetyObserver(ABC):
    """Abstract base class for all observers in the safety system.

    Allows the separation of calculation logic (Model) from visualization or
    reporting (View), implementing the Observer design pattern.
    """

    @abstractmethod
    def on_block_computed(
        self,
        block: "BlockInterface",
        input_ports: dict,
        spfm_in: dict[FaultType, float],
        lfm_in: dict[FaultType, float],
        spfm_out: dict[FaultType, float],
        lfm_out: dict[FaultType, float],
    ) -> dict:
        """Triggered after a hardware block completes its FIT rate transformation.

        The observer acts upon this event (e.g., drawing the block in a diagram)
        and returns the new visual connection points (ports).

        Args:
            block (BlockInterface): The instance of the logic block (defines shape and type).
            input_ports (dict): Mapping of fault types to incoming node IDs (defines edge origins).
            spfm_in (dict[FaultType, float]): Dictionary of incoming residual/SPFM FIT rates.
            lfm_in (dict[FaultType, float]): Dictionary of incoming latent/LFM FIT rates.
            spfm_out (dict[FaultType, float]): Updated dictionary of outgoing residual/SPFM FIT rates.
            lfm_out (dict[FaultType, float]): Updated dictionary of outgoing latent/LFM FIT rates.

        Returns:
            dict: A dictionary containing the newly created output ports (node IDs) to be
            used as inputs for the next block in the chain.
        """
        pass
