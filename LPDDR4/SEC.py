from Modules import Base, FAULTS, Sum_Block, Basic_Event, Coverage_Block, Split_Block

class SEC(Base):
    """
    Component for Single Error Correction (SEC) in LPDDR4 architectures.
    This module handles SBE coverage and redistributes DBE failure rates.
    """

    def __init__(self, name: str):
        """
        Initializes the SEC component with specific diagnostic coverage and failure rates.

        @param name The descriptive name of the component.
        """
        self.SEC_ECC_DC = 1.0
        self.DBE_TO_DBE_P = 0.83
        self.DBE_TO_TBE_P = 0.17
        self.SB_SOURCE = 0.1
        self.DBE_SOURCE = 172
        super().__init__(name)

    def configure_blocks(self):
        """
        Configures the internal block structure, combining fault sources, coverage, and splits.
        """
        self.root_block = Sum_Block(self.name, [
            Basic_Event(FAULTS.SB, self.SB_SOURCE, is_spfm=False),
            Basic_Event(FAULTS.DBE, self.DBE_SOURCE, is_spfm=False),
            Coverage_Block(FAULTS.SBE, self.SEC_ECC_DC),
            Split_Block(
                "DBE_to_TBE_Split", 
                FAULTS.DBE, 
                {FAULTS.DBE: self.DBE_TO_DBE_P, FAULTS.TBE: self.DBE_TO_TBE_P}, 
                is_spfm=True
            )
        ])