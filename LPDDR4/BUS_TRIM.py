# 
#  @file BUS_TRIM.py
#  @author Linus Held 
#  @brief Component for trimming and distributing failure rates across the bus architecture.
#  @version 2.0
#  @date 2025-12-25
# 
#  @copyright Copyright (c) 2025 Linus Held. All rights reserved.
# 

from Modules.Core import Base, Pipeline_Block, Sum_Block, Split_Block, Basic_Event
from Modules.Interfaces import FAULTS

class BUS_TRIM(Base):
    """
    Component for trimming and distributing failure rates across the bus architecture.
    This module injects specific bus-related fault sources (MBE, AZ) and redistributes 
    SBE, DBE, and TBE faults for both SPFM and LFM paths.
    Uses a Pipeline to ensure that sources are injected before sequential split operations occur.
    """

    def __init__(self, name: str):
        """
        Initializes the BUS_TRIM component with bus-specific split distribution 
        parameters and additional fault source rates.

        @param name The descriptive name of the component.
        """
        self.spfm_SBE_split = {FAULTS.SBE: 0.438}
        self.spfm_DBE_split = {FAULTS.SBE: 0.496, FAULTS.DBE: 0.314}
        self.spfm_TBE_split = {FAULTS.SBE: 0.325, FAULTS.DBE: 0.419, FAULTS.TBE: 0.175}
        
        self.lfm_SBE_split = {FAULTS.SBE: 0.438}
        self.lfm_DBE_split = {FAULTS.SBE: 0.496, FAULTS.DBE: 0.314}
        
        self.spfm_MBE_Source = 2.3
        self.spfm_AZ_Source = 172
        
        super().__init__(name)

    def configure_blocks(self):
        """
        Configures the root block as a pipeline of fault injections and sequential 
        split operations.
        """
        sources = Sum_Block("Bus_Sources", [
            Basic_Event(FAULTS.MBE, self.spfm_MBE_Source, is_spfm=True),
            Basic_Event(FAULTS.AZ, self.spfm_AZ_Source, is_spfm=True)
        ])

        self.root_block = Pipeline_Block(self.name, [
            sources,
            Split_Block("SPFM_SBE_Split", FAULTS.SBE, self.spfm_SBE_split, is_spfm=True),
            Split_Block("SPFM_DBE_Split", FAULTS.DBE, self.spfm_DBE_split, is_spfm=True),
            Split_Block("SPFM_TBE_Split", FAULTS.TBE, self.spfm_TBE_split, is_spfm=True),
            
            Split_Block("LFM_SBE_Split", FAULTS.SBE, self.lfm_SBE_split, is_spfm=False),
            Split_Block("LFM_DBE_Split", FAULTS.DBE, self.lfm_DBE_split, is_spfm=False)
        ])