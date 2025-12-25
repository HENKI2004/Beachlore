# 
#  @file Pipeline_Block.py
#  @author Linus Held 
#  @brief Executes a sequence of logic blocks for FIT rate transformations.
#  @version 2.0
#  @date 2025-12-25
# 
#  @copyright Copyright (c) 2025 Linus Held. All rights reserved.
# 

from ..Interfaces.Block_Interface import Block_Interface

class Pipeline_Block(Block_Interface):
    """
    Executes a sequence of blocks where the output of one block becomes the input of the next.
    """

    def __init__(self, name: str, blocks: list[Block_Interface]):
        """
        Initializes the Pipeline_Block with a sequence of sub-blocks.

        @param name The descriptive name of the pipeline.
        @param blocks A list of blocks implementing Block_Interface to be executed in order.
        """
        self.name = name
        self.blocks = blocks

    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        """
        Sequentially processes all blocks in the pipeline, passing the output rates of one block to the next.

        @param spfm_rates Dictionary containing current SPFM/residual fault rates.
        @param lfm_rates Dictionary containing current LFM/latent fault rates.
        @return A tuple of updated (spfm_rates, lfm_rates) dictionaries after all steps.
        """
        current_spfm = spfm_rates.copy()
        current_lfm = lfm_rates.copy()

        for block in self.blocks:
            current_spfm, current_lfm = block.compute_fit(current_spfm, current_lfm)

        return current_spfm, current_lfm