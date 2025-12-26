#
#  @file Basic_Event.py
#  @author Linus Held
#  @brief Represents a fault source (Basic Event) injecting FIT rates.
#  @version 2.0
#  @date 2025-12-25
#
#  @copyright Copyright (c) 2025 Linus Held. All rights reserved.
#

from ..interfaces import BlockInterface, FaultType


class BasicEvent(BlockInterface):
    """
    Represents a source of a fault (Basic Event) that injects a specific FIT rate into the system.
    This class handles the mathematical addition of failure rates to the fault dictionaries.
    """

    def __init__(self, fault_type: FaultType, rate: float, is_spfm: bool = True):
        """
        Initializes the Basic_Event fault source.

        @param fault_type The type of fault (Enum) this event produces.
        @param rate The FIT rate of this basic event.
        @param is_spfm Whether this rate counts towards SPFM (True) or LFM (False).
        """
        self.fault_type = fault_type
        self.lambda_BE = rate
        self.is_spfm = is_spfm

    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        """
        Transforms the input fault rate dictionaries by injecting the defined FIT rate.

        @param spfm_rates Dictionary containing current SPFM/residual fault rates.
        @param lfm_rates Dictionary containing current LFM/latent fault rates.
        @return A tuple of updated (spfm_rates, lfm_rates) dictionaries.
        """
        new_spfm = spfm_rates.copy()
        new_lfm = lfm_rates.copy()

        target_dict = new_spfm if self.is_spfm else new_lfm
        target_dict[self.fault_type] = target_dict.get(self.fault_type, 0.0) + self.lambda_BE

        return new_spfm, new_lfm
