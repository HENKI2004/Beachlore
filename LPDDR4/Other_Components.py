from Modules import Base, FAULTS, Sum_Block, Basic_Event

class Other_Components(Base):
    """
    Component representing miscellaneous hardware parts that contribute a fixed FIT rate to the system.
    """

    def __init__(self, name: str):
        """
        Initializes the component and sets the constant source FIT rate.
        
        @param name The descriptive name of the component.
        """
        self.source_rate = 96.0 
        super().__init__(name)

    def configure_blocks(self):
        """
        Configures the root block to inject the FIT rate as a residual fault (SPFM).
        """
        self.root_block = Sum_Block(self.name, [
            Basic_Event(FAULTS.OTH, self.source_rate, is_spfm=True)
        ])