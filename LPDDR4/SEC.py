from Modules.Base import Base
from Modules.Faults import FAULTS
from Modules.Pipeline_Block import Pipeline_Block
from Modules.Basic_Event import Basic_Event
from Modules.Coverage_Block import Coverage_Block
from Modules.Split_Block import Split_Block

class SEC(Base):
    """
    Single Error Correction component for LPDDR4 using the new block architecture.
    """

    def __init__(self, name: str, spfm_input: dict, lfm_input: dict):
        """
        Initializes SEC parameters and calls the base constructor.
        """
        self.SEC_ECC_DC = 1.0
        self.DBE_TO_DBE_P = 0.83
        self.DBE_TO_TBE_P = 0.17
        self.SB_SOURCE = 0.1
        self.DBE_SOURCE = 172
        super().__init__(name, spfm_input, lfm_input)

    def configure_blocks(self):
        """
        Configures the root block as a pipeline of LFM sources, SPFM coverage, and splits.
        """
        self.root_block = Pipeline_Block(self.name, [
            Basic_Event(FAULTS.SB, self.SB_SOURCE, is_spfm=False),
            Basic_Event(FAULTS.DBE, self.DBE_SOURCE, is_spfm=False),
            Coverage_Block(FAULTS.SBE, self.SEC_ECC_DC),
            Split_Block("DBE_to_TBE_Split", FAULTS.DBE, 
                        {FAULTS.DBE: self.DBE_TO_DBE_P, FAULTS.TBE: self.DBE_TO_TBE_P}, 
                        is_spfm=True)
        ])