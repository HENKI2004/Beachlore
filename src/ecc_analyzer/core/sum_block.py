#
#  @file Sum_Block.py
#  @author Linus Held
#  @brief Parallel block that aggregates FIT rates from multiple sub-blocks.
#  @version 2.0
#  @date 2025-12-25
#
#  @copyright Copyright (c) 2025 Linus Held. All rights reserved.
#

from ..interfaces import BlockInterface


class SumBlock(BlockInterface):
    """
    Parallel block that aggregates FIT rates from multiple sub-blocks and manages path junctions.
    """

    def __init__(self, name: str, sub_blocks: list[BlockInterface]):
        """
        Initializes the sum block with a list of parallel sub-blocks.

        @param name The descriptive name of the aggregation block.
        @param sub_blocks List of blocks whose results will be summed.
        """
        self.name = name
        self.sub_blocks = sub_blocks

    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        """
        Aggregates the FIT rate transformations from all internal parallel blocks.
        Calculates the delta contribution of each block to the total system rates.

        @param spfm_rates Dictionary containing current SPFM/residual fault rates.
        @param lfm_rates Dictionary containing current LFM/latent fault rates.
        @return A tuple of updated (spfm_rates, lfm_rates) dictionaries.
        """
        total_spfm = spfm_rates.copy()
        total_lfm = lfm_rates.copy()
        for block in self.sub_blocks:
            res_spfm, res_lfm = block.compute_fit(spfm_rates, lfm_rates)
            for fault in set(res_spfm.keys()) | set(spfm_rates.keys()):
                delta = res_spfm.get(fault, 0.0) - spfm_rates.get(fault, 0.0)
                if delta != 0:
                    total_spfm[fault] = total_spfm.get(fault, 0.0) + delta
            for fault in set(res_lfm.keys()) | set(lfm_rates.keys()):
                delta = res_lfm.get(fault, 0.0) - lfm_rates.get(fault, 0.0)
                if delta != 0:
                    total_lfm[fault] = total_lfm.get(fault, 0.0) + delta
        return total_spfm, total_lfm
