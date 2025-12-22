from Modules.Base import Base
from Modules.Faults import FAULTS
from Modules.Pipeline_Block import Pipeline_Block
from Modules.Basic_Event import Basic_Event

class Other_Components(Base):
    """
    Component representing miscellaneous hardware parts that contribute a fixed FIT rate to the system.
    """

    def __init__(self, name: str, spfm_input: dict, lfm_input: dict):
        """
        Initializes the component and sets the constant source FIT rate.
        
        @param name The name of the component.
        @param spfm_input Initial dictionary of SPFM rates.
        @param lfm_input Initial dictionary of LFM rates.
        """
        self.source_rate = 96 
        super().__init__(name, spfm_input, lfm_input)

    def configure_blocks(self):
        """
        Configures the root block to inject the FIT rate as a residual fault (SPFM).
        """
        self.root_block = Pipeline_Block(self.name, [
            Basic_Event(FAULTS.OTH, self.source_rate, is_spfm=True)
        ])