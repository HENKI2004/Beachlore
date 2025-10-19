from Modules import Basic_Event,Asil_Block,Coverage_Block,Split_Block,Sum_Block
from collections import defaultdict

class SEC:
    
    def __init__(self, name: str, spfm_input: dict,lfm_input,CoverageBlock, SplitBlock,SumBlock,BasicEvent):
            
        self.name = name
            
        self.spfm_input = spfm_input
        self.lfm_input = lfm_input
            
        self.SEC_ECC_DC = 1.0           # 100% Diagnostic Coverage for SBEs
        self.DBE_TO_DBE_P = 0.83        # 83% of DBEs remain DBEs
        self.DBE_TO_TBE_P = 0.17        # 17% of DBEs become Triple-Bit Errors (TBEs)
        self.SB_SCOURCE = 0.1
        
        self.spfm_output = defaultdict(float) # Rates contributing to Lambda_Dangerous (RF)
        self.lfm_output = defaultdict(float)  # Rates contributing to Lambda_MPF_L (Latent)
        
        self.spfm_split_blocks = {}
        self.spfm_coverage_blocks = {}
        self.spfm_source_blocks = {}
        
        self.lfm_split_blocks = {}
        self.lfm_coverage_blocks = {}
        self.lfm_source_blocks = {}
            
        self.CoverageBlock = CoverageBlock
        self.SplitBlock = SplitBlock
        self.BasicEvent = BasicEvent
        self.SumBlock = SumBlock
            
        self.lfm_source_blocks['SB'] = self.BasicEvent("SB",self.SB_SCOURCE)                                            
        self.spfm_coverage_blocks['SBE'] = self.CoverageBlock("SBE", self.SEC_ECC_DC)
        self.spfm_split_blocks['DBE'] = self.SplitBlock("DBE", {'DBE': self.DBE_TO_DBE_P, 'TBE': self.DBE_TO_TBE_P})
            
        self.lfm_output['DBE'] += 172.0
            
    def computefit(self) -> dict: 
        for name, rate in self.spfm_input.items():
            
            was_processed = False 
            
            if name in self.spfm_coverage_blocks:
                coverage_results = self.spfm_coverage_blocks[name].compute_fit(rate)
                lambda_RF = coverage_results['RF']
                lambda_MPFL = coverage_results['MPF_L']
                
                self.spfm_output[name] += lambda_RF      
                self.lfm_output[name] += lambda_MPFL 
                
                was_processed = True
                
            if name in self.spfm_split_blocks:

                split_results:dict = self.spfm_split_blocks[name].compute_fit(rate)
                
                for split_name, split_rate in split_results.items():
                    self.spfm_output[split_name] += split_rate 
                
                was_processed = True
            
            if not was_processed:

                self.spfm_output[name] += rate
        
        for name, rate in self.lfm_input.items():
            was_processed = False
            
            if name in self.lfm_split_blocks:
                split_results:dict = self.lfm_split_blocks[name].compute_fit(rate)
                for split_name, split_rate in split_results.items():
                    self.lfm_output[split_name] += split_rate
                
                was_processed = True
                
            if not was_processed:
                self.lfm_output[name] += rate
        

        for name, block in self.spfm_source_blocks.items():
            self.spfm_output[name] += block.get_output_rate()
            
        for name, block in self.lfm_source_blocks.items():
            self.lfm_output[name] += block.get_output_rate()
        
        return {
            'SPFM': self.spfm_output,
            'LFM': self.lfm_output
        }
    
    