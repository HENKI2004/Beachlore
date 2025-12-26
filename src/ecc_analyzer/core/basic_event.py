"""Represents a fault source (Basic Event) injecting FIT rates."""

# Copyright (c) 2025 Linus Held. All rights reserved.

from ..interfaces import BlockInterface, FaultType


class BasicEvent(BlockInterface):
    """Represents a source of a fault (Basic Event) that injects a specific FIT rate.

    This class handles the mathematical addition of failure rates to the fault dictionaries.
    """

    def __init__(self, fault_type: FaultType, rate: float, is_spfm: bool = True):
        """Initializes the BasicEvent fault source.

        Args:
            fault_type (FaultType): The type of fault (Enum) this event produces.
            rate (float): The FIT rate of this basic event.
            is_spfm (bool, optional): Whether this rate counts towards SPFM (True)
                or LFM (False). Defaults to True.
        """
        self.fault_type = fault_type
        self.lambda_BE = rate
        self.is_spfm = is_spfm

    def compute_fit(self, spfm_rates: dict[FaultType, float], lfm_rates: dict[FaultType, float]) -> tuple[dict[FaultType, float], dict[FaultType, float]]:
        """Transforms the input fault rate dictionaries by injecting the defined FIT rate.

        Args:
            spfm_rates (dict[FaultType, float]): Dictionary containing current SPFM/residual fault rates.
            lfm_rates (dict[FaultType, float]): Dictionary containing current LFM/latent fault rates.

        Returns:
            tuple[dict[FaultType, float], dict[FaultType, float]]: A tuple containing:
                - Updated SPFM rates dictionary.
                - Updated LFM rates dictionary.
        """
        new_spfm = spfm_rates.copy()
        new_lfm = lfm_rates.copy()

        target_dict = new_spfm if self.is_spfm else new_lfm
        target_dict[self.fault_type] = target_dict.get(self.fault_type, 0.0) + self.lambda_BE

        return new_spfm, new_lfm
