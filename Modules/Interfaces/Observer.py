#  @file Observer.py
#  @author Linus Held 
#  @brief Defines the abstract observer interface for safety analysis visualization.
#  @version 1.0
#  @date 2025-12-24
# 
#   @copyright Copyright (c) 2025 Linus Held. All rights reserved.

from abc import ABC, abstractmethod


class SafetyObserver(ABC):
    """
    Abstract base class for all observers in the safety system.
    Allows the separation of calculation logic from visualization or reporting.
    """

    @abstractmethod
    def on_block_computed(self, block, input_ports: dict, spfm_in: dict, lfm_in: dict, spfm_out: dict, lfm_out: dict):
        """
        Triggered after a hardware block completes its FIT rate transformation.

        @param block: The instance of the logic block (defines shape and type).
        @param input_ports: Mapping of fault types to incoming node IDs (defines edge origins).
        @param spfm_in: Dictionary of incoming residual/SPFM FIT rates (Red path logic).
        @param lfm_in: Dictionary of incoming latent/LFM FIT rates (Blue path logic).
        @param spfm_out: Updated dictionary of outgoing residual/SPFM FIT rates.
        @param lfm_out: Updated dictionary of outgoing latent/LFM FIT rates.
        """
        pass