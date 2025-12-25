# 
#  @file Split_Block.py
#  @author Linus Held 
#  @brief Distributes FIT rates of a specific fault type across multiple targets.
#  @version 2.0
#  @date 2025-12-25
# 
#  @copyright Copyright (c) 2025 Linus Held. All rights reserved.
# 

from ..Interfaces.Block_Interface import Block_Interface
from ..Interfaces.Faults import FAULTS

class Split_Block(Block_Interface):
    """
    Distributes the FIT rate of a specific fault type across multiple other fault types 
    based on a defined distribution.
    """

    def __init__(self, name: str, fault_to_split: FAULTS, distribution_rates: dict, is_spfm: bool = True):
        """
        Initializes the Split_Block with a distribution mapping.

        @param name The descriptive name of the split operation.
        @param fault_to_split The source fault type (Enum) to be distributed.
        @param distribution_rates Dictionary mapping target FAULTS to their probability (0.0 - 1.0).
        @param is_spfm Indicates if this split occurs on the SPFM/residual path.
        @throws ValueError If the sum of distribution rates exceeds 1.0.
        """
        sum_of_rates = sum(distribution_rates.values())
        if sum_of_rates > 1.0 + 1e-9: 
            raise ValueError(f"Sum of distribution rates ({sum_of_rates:.4f}) must not exceed 1.0.")
            
        self.name = name
        self.fault_to_split = fault_to_split
        self.distribution_rates = distribution_rates
        self.is_spfm = is_spfm

    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        """
        Transforms the input fault rate dictionaries by redistributing the source fault rate.
        
        @param spfm_rates Dictionary containing current SPFM/residual fault rates.
        @param lfm_rates Dictionary containing current LFM/latent fault rates.
        @return A tuple of updated (spfm_rates, lfm_rates) dictionaries.
        """
        new_spfm = spfm_rates.copy()
        new_lfm = lfm_rates.copy()
        target_dict = new_spfm if self.is_spfm else new_lfm
        
        if self.fault_to_split in target_dict:
            original_rate = target_dict.pop(self.fault_to_split)
            for target_fault, probability in self.distribution_rates.items():
                split_rate = original_rate * probability
                target_dict[target_fault] = target_dict.get(target_fault, 0.0) + split_rate
        
        return new_spfm, new_lfm