from .Block_Interface import Block_Interface

class Sum_Block(Block_Interface):
    """
    Aggregates the results of multiple parallel blocks by summing their output FIT rates.
    This block is used for parallel fault paths or combining multiple sources.
    """

    def __init__(self, name: str, sub_blocks: list[Block_Interface]):
        """
        Initializes the Sum_Block with a list of parallel sub-blocks.

        @param name The name of the sum block.
        @param sub_blocks A list of blocks implementing Block_Interface to be executed in parallel.
        """
        self.name = name
        self.sub_blocks = sub_blocks

    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        """
        Processes all sub-blocks using the same input rates and sums their individual outputs.

        @param spfm_rates Dictionary containing current SPFM/residual fault rates.
        @param lfm_rates Dictionary containing current LFM/latent fault rates.
        @return A tuple containing the aggregated (spfm_rates, lfm_rates) dictionaries.
        """
        total_spfm = {}
        total_lfm = {}

        for block in self.sub_blocks:
            res_spfm, res_lfm = block.compute_fit(spfm_rates, lfm_rates)
            
            for fault, rate in res_spfm.items():
                total_spfm[fault] = total_spfm.get(fault, 0.0) + rate
            for fault, rate in res_lfm.items():
                total_lfm[fault] = total_lfm.get(fault, 0.0) + rate
                
        return total_spfm, total_lfm