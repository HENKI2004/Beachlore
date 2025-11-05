from abc import ABC, abstractmethod
from collections import defaultdict
from enum import Enum, auto

from .Basic_Event import Basic_Event
from .Coverage_Block import Coverage_Block
from .Split_Block import Split_Block
from .Sum_Block import Sum_Block
from .Asil_Block import ASIL_Block

class FAULTS(Enum):
    SBE = auto()
    DBE = auto()
    TBE = auto()
    MBE = auto()
    WD = auto()
    AZ = auto()
    SB = auto()
    SDB = auto() 
    OTH = auto() 
    SBE_IF = auto()

class Base(ABC):
    
    def __init__(self, name: str, spfm_input: dict, lfm_input : dict):

        self.name = name
        self.spfm_input = spfm_input.copy()
        self.lfm_input = lfm_input.copy()
        
        self.spfm_output = defaultdict(float) 
        self.lfm_output = defaultdict(float)  
        
        self.spfm_split_blocks = {}
        self.spfm_coverage_blocks = {}
        self.spfm_sum_blocks = {}
        self.spfm_source_blocks = {}
        
        self.lfm_split_blocks = {}
        self.lfm_coverage_blocks = {}
        self.lfm_source_blocks = {}
        
        self.BasicEvent = Basic_Event
        self.CoverageBlock = Coverage_Block
        self.SplitBlock = Split_Block
        self.SumBlock = Sum_Block

        
        self.configure_blocks()
    
    @abstractmethod
    def configure_blocks(self):
        pass
        
    def compute_fit(self) -> dict:
        
        # 3. ADD SOURCE BLOCK RATES
        for name, block in self.spfm_source_blocks.items():
            
            rate_to_add = block.compute_fit()
            current_rate = self.spfm_input.get(name, 0.0)
            self.spfm_input[name] = current_rate + rate_to_add
            
        for name, block in self.lfm_source_blocks.items():
            rate_to_add = block.compute_fit()
            current_rate = self.lfm_input.get(name, 0.0)
            self.lfm_input[name] = current_rate + rate_to_add
        
         
        # 1. PROCESS SPFM INPUTS
        for name, rate in self.spfm_input.items():
            was_processed = False 
            
            # Check for Coverage Block
            if name in self.spfm_coverage_blocks:
                coverage_results = self.spfm_coverage_blocks[name].compute_fit(rate)
                lambda_RF = coverage_results['RF']
                lambda_MPFL = coverage_results['MPF_L']
                
                self.spfm_output[name] += lambda_RF      
                self.lfm_output[name] += lambda_MPFL 
                
                was_processed = True
                
            # Check for Split Block
            if name in self.spfm_split_blocks:
                split_results:dict = self.spfm_split_blocks[name].compute_fit(rate)
                
                for split_name, split_rate in split_results.items():
                    if split_name != 'Safe':
                        self.spfm_output[split_name] += split_rate 
                
                was_processed = True
            
            if not was_processed:
                self.spfm_output[name] += rate
        
        # 2. PROCESS LFM INPUTS 
        for name, rate in self.lfm_input.items():
            was_processed = False
            
            # Check for LFM Coverage Block
            if name in self.lfm_coverage_blocks:
                coverage_results = self.lfm_coverage_blocks[name].compute_fit(rate)
                lambda_RF = coverage_results['RF'] 
                lambda_MPFL = coverage_results['MPF_L']
                self.lfm_output[name] += lambda_RF 
                
                was_processed = True

            # Check for LFM Split Block
            if name in self.lfm_split_blocks:
                split_results:dict = self.lfm_split_blocks[name].compute_fit(rate)
                for split_name, split_rate in split_results.items():
                    if split_name != 'Safe':
                        self.lfm_output[split_name] += split_rate
                
                was_processed = True
                
            if not was_processed:
                self.lfm_output[name] += rate
        
        
        # 4. RETURN FINAL RESULTS
        return {
            'SPFM': self.spfm_output,
            'LFM': self.lfm_output
        }