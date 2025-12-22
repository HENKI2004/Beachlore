from Modules.Base import Base, FAULTS
from Modules.Pipeline_Block import Pipeline_Block
from Modules.Basic_Event import Basic_Event
from Modules.Coverage_Block import Coverage_Block
from Modules.Split_Block import Split_Block

class SEC_DED(Base):
    """
    Component for Single Error Correction and Double Error Detection (SEC-DED).
    """

    def __init__(self, name: str, spfm_input: dict, lfm_input: dict):
        """
        Initializes the SEC_DED component by defining all parameters BEFORE calling the base constructor.
        """
        # --- SPFM Parameters ---
        self.SBE_DC = 1.0         
        self.DBE_DC = 1.0         
        self.MBE_DC = 0.5         
        self.TBE_DC = 1.0         
        
        # TBE-Split to MBE
        self.TBE_SPLIT_TO_MBE = 0.56

        # --- LFM Parameters ---
        self.LFM_SBE_DC = 1.0    
        self.LFM_DBE_DC = 1.0     
        
        # --- Source Parameters ---
        self.SDB_SOURCE = 0.1     

        super().__init__(name, spfm_input, lfm_input)

    def configure_blocks(self):
        """
        Configures the root block as a pipeline of sources, coverage, and splits.
        """
        self.root_block = Pipeline_Block(self.name, [
            Basic_Event(FAULTS.SDB, self.SDB_SOURCE, is_spfm=False),
            
            Coverage_Block(FAULTS.SBE, self.SBE_DC),
            Coverage_Block(FAULTS.DBE, self.DBE_DC),
            Coverage_Block(FAULTS.TBE, self.TBE_DC),
            Coverage_Block(FAULTS.MBE, self.MBE_DC),
            
            Coverage_Block(FAULTS.SBE, self.LFM_SBE_DC),
            Coverage_Block(FAULTS.DBE, self.LFM_DBE_DC),
            
            Split_Block("TBE_to_MBE_Split", FAULTS.TBE, 
                        {FAULTS.MBE: self.TBE_SPLIT_TO_MBE}, 
                        is_spfm=True)
        ])