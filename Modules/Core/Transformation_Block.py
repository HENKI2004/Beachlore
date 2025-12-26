# 
#  @file Transformation_Block.py
#  @author Linus Held 
#  @brief Block logic for transferring FIT rates between fault types.
#  @version 2.0
#  @date 2025-12-25
# 
#  @copyright Copyright (c) 2025 Linus Held. All rights reserved.
# 

from ..Interfaces.Block_Interface import Block_Interface
from ..Interfaces.Faults import FAULTS

class Transformation_Block(Block_Interface):
    """
    Transfers a portion of one fault type's rate to another fault type without removing the original.
    """

    def __init__(self, source_fault: FAULTS, target_fault: FAULTS, factor: float):
        """
        Initializes the transformation block.

        @param source_fault The fault type from which the rate is taken.
        @param target_fault The fault type to which the rate is added.
        @param factor The multiplication factor applied to the source rate.
        """
        self.source = source_fault
        self.target = target_fault
        self.factor = factor

    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        """
        Transforms the input fault rate dictionaries by transferring a portion of the source rate.

        @param spfm_rates Dictionary containing current SPFM/residual fault rates.
        @param lfm_rates Dictionary containing current LFM/latent fault rates.
        @return A tuple of updated (spfm_rates, lfm_rates) dictionaries.
        """
        new_spfm = spfm_rates.copy()
        if self.source in new_spfm:
            transfer_rate = new_spfm[self.source] * self.factor
            new_spfm[self.target] = new_spfm.get(self.target, 0.0) + transfer_rate 

        return new_spfm, lfm_rates.copy()