from Modules.Core.Base import FAULTS, Base


class Other_Components(Base):
    def __init__(self, name: str, spfm_input: dict, lfm_input):
        self.OTHER_RF_SOURCE = 9.5  #

        super().__init__(name, spfm_input, lfm_input)

    def configure_blocks(self):
        self.spfm_source_blocks[FAULTS.OTH] = self.BasicEvent(FAULTS.OTH, self.OTHER_RF_SOURCE)
