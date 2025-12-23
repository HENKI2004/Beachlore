from .Block_Interface import Block_Interface
from .Faults import FAULTS

class Sum_Block(Block_Interface):

    def __init__(self, name: str, sub_blocks: list[Block_Interface]):
        self.name = name
        self.sub_blocks = sub_blocks

    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        total_spfm = spfm_rates.copy()
        total_lfm = lfm_rates.copy()

        for block in self.sub_blocks:
            res_spfm, res_lfm = block.compute_fit(spfm_rates, lfm_rates)
            
            all_faults = set(res_spfm.keys()) | set(spfm_rates.keys())
            for fault in all_faults:
                new_rate = res_spfm.get(fault, 0.0)
                old_rate = spfm_rates.get(fault, 0.0)
                delta = new_rate - old_rate
                
                if delta != 0:
                    total_spfm[fault] = total_spfm.get(fault, 0.0) + delta

            all_lfm_faults = set(res_lfm.keys()) | set(lfm_rates.keys())
            for fault in all_lfm_faults:
                new_rate = res_lfm.get(fault, 0.0)
                old_rate = lfm_rates.get(fault, 0.0)
                delta = new_rate - old_rate
                
                if delta != 0:
                    total_lfm[fault] = total_lfm.get(fault, 0.0) + delta
                
        return total_spfm, total_lfm