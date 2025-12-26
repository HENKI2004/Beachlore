from Modules.Core.Base import FAULTS, Base


class LINK_ECC(Base):
    def __init__(self, name: str, spfm_input: dict, lfm_input):
        self.SBE_IF_SOURCE_RATE = 5.050

        self.SBE_IF_DC_RESIDUAL = 1.0
        self.SBE_IF_DC_LATENT = 1.0

        super().__init__(name, spfm_input, lfm_input)

    def configure_blocks(self):
        # --- SPFM Quellen ---
        self.spfm_source_blocks[FAULTS.SBE] = self.BasicEvent(FAULTS.SBE, self.SBE_IF_SOURCE_RATE)

        # --- SPFM Coverage Blöcke ---
        self.spfm_coverage_blocks[FAULTS.SBE] = self.CoverageBlock(FAULTS.SBE, self.SBE_IF_DC_RESIDUAL, self.SBE_IF_DC_LATENT)
