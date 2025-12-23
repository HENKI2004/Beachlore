from Modules import Base, FAULTS, Sum_Block, Pipeline_Block, Basic_Event, Coverage_Block, Transformation_Block

class SEC_DED(Base):
    """
    Component for Single Error Correction and Double Error Detection (SEC-DED).
    This module manages diagnostic coverage for multiple fault types and handles transformations between failure modes.
    """

    def __init__(self, name: str):
        """
        Initializes the SEC-DED component with specific diagnostic coverage and source parameters.

        @param name The descriptive name of the component.
        """
        self.SBE_DC = 1.0         
        self.DBE_DC = 1.0         
        self.MBE_DC = 0.5         
        self.TBE_DC = 1.0         
        self.TBE_SPLIT_TO_MBE = 0.56
        self.LFM_SBE_DC = 1.0    
        self.LFM_DBE_DC = 1.0     
        self.SDB_SOURCE = 0.1     

        super().__init__(name)

    def configure_blocks(self):
        """
        Configures the internal block structure, ensuring the correct sequence of failure injections, transformations, and coverage applications.
        """
        self.root_block = Sum_Block(self.name, [
            Basic_Event(FAULTS.SDB, self.SDB_SOURCE, is_spfm=False),

            Coverage_Block(FAULTS.SBE, self.LFM_SBE_DC, is_spfm=False),
            Coverage_Block(FAULTS.DBE, self.LFM_DBE_DC, is_spfm=False),
            
            Pipeline_Block("Transformer", [
                Transformation_Block(FAULTS.TBE, FAULTS.MBE, self.TBE_SPLIT_TO_MBE)
            ]),
            
            Coverage_Block(FAULTS.SBE, self.SBE_DC),
            Coverage_Block(FAULTS.DBE, self.DBE_DC),
            Coverage_Block(FAULTS.TBE, self.TBE_DC),
            Coverage_Block(FAULTS.MBE, self.MBE_DC)
        ])