"""Block logic for transferring FIT rates between fault types."""

# Copyright (c) 2025 Linus Held. All rights reserved.

from ..interfaces import BlockInterface, FaultType


class TransformationBlock(BlockInterface):
    """Transfers a portion of one fault type's rate to another fault type.

    This operation adds a calculated rate to the target fault type based on the
    source fault type, without removing the rate from the source (unlike SplitBlock).
    """

    def __init__(self, source_fault: FaultType, target_fault: FaultType, factor: float):
        """Initializes the transformation block.

        Args:
            source_fault (FaultType): The fault type from which the rate is calculated.
            target_fault (FaultType): The fault type to which the calculated rate is added.
            factor (float): The multiplication factor applied to the source rate.
        """
        self.source = source_fault
        self.target = target_fault
        self.factor = factor

    def compute_fit(self, spfm_rates: dict[FaultType, float], lfm_rates: dict[FaultType, float]) -> tuple[dict[FaultType, float], dict[FaultType, float]]:
        """Transforms the input fault rate dictionaries by transferring a portion of the source rate.

        Args:
            spfm_rates (dict[FaultType, float]): Current residual failure rates.
            lfm_rates (dict[FaultType, float]): Current latent failure rates.

        Returns:
            tuple[dict[FaultType, float], dict[FaultType, float]]: A tuple containing:
                - Updated SPFM rates (target fault increased).
                - Unchanged LFM rates.
        """
        new_spfm = spfm_rates.copy()
        if self.source in new_spfm:
            transfer_rate = new_spfm[self.source] * self.factor
            new_spfm[self.target] = new_spfm.get(self.target, 0.0) + transfer_rate

        return new_spfm, lfm_rates.copy()
