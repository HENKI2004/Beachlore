from Modules import Base, FAULTS, Sum_Block, Basic_Event

class Events(Base):
    """
    Primary failure rate source component for LPDDR4 DRAM.
    This module initializes the baseline failure rates for SBE, DBE, MBE, and WD.
    """

    def __init__(self, name: str):
        """
        Initializes the fault rates based on a baseline DRAM FIT value.

        @param name The descriptive name of the component.
        """
        dram_fit = 2300.0

        self.fault_sbe = 0.7 * dram_fit
        self.fault_dbe = 0.0748 * dram_fit
        self.fault_mbe = 0.0748 * dram_fit
        self.fault_wd = 0.0748 * dram_fit
        
        super().__init__(name)

    def configure_blocks(self):
        """
        Configures the internal block structure by injecting failure rates as basic events.
        """
        self.root_block = Sum_Block(self.name, [
            Basic_Event(FAULTS.SBE, self.fault_sbe, is_spfm=True),
            Basic_Event(FAULTS.DBE, self.fault_dbe, is_spfm=True),
            Basic_Event(FAULTS.MBE, self.fault_mbe, is_spfm=True),
            Basic_Event(FAULTS.WD, self.fault_wd, is_spfm=True),
        ])