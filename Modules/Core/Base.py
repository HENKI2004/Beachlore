#  @file Base.py
#  @author Linus Held 
#  @brief Abstract base class for hardware components acting as logic containers.
#  @version 2.0
#  @date 2025-12-25
# 
#  @copyright Copyright (c) 2025 Linus Held. All rights reserved.

from abc import ABC, abstractmethod
from ..Interfaces.Block_Interface import Block_Interface

class Base(Block_Interface, ABC):
    """
    Abstract base class for hardware components.
    Provides a structured way to define internal logic hierarchies.
    """

    def __init__(self, name: str):
        """
        Initializes the component and triggers the internal block configuration.

        @param name The descriptive name of the hardware component.
        """
        self.name = name
        self.root_block: Block_Interface = None
        self.configure_blocks()

    @abstractmethod
    def configure_blocks(self):
        """
        Abstract method to define the internal logic structure (root block) of the component.
        Must be implemented by subclasses to specify the internal tree of blocks.
        """
        pass

    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        """
        Delegates the FIT rate transformation to the internal root block.
        This allows the component to be treated as a single modular unit within the system.

        @param spfm_rates Dictionary containing current SPFM/residual fault rates.
        @param lfm_rates Dictionary containing current LFM/latent fault rates.
        @return A tuple of updated (spfm_rates, lfm_rates) dictionaries.
        """
        if self.root_block is None:
            return spfm_rates.copy(), lfm_rates.copy()
        
        return self.root_block.compute_fit(spfm_rates, lfm_rates)