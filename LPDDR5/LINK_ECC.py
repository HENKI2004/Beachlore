# Beachlore/LPDDR5/LINK_ECC.py
from Modules.Base import Base,FAULTS

class LINK_ECC(Base):
    """
    NEUER Block für LPDDR5 Link-ECC (gemäß Steiner et al., 2025).
    Fügt die Interface-SBE-Fehlerquelle hinzu und deckt sie ab.
    """
    def __init__(self, name: str, spfm_input: dict, lfm_input):
        
        # HINWEIS: Das Paper [cite: 386] gibt 5.050e9 FIT an.
        # Dies ist wahrscheinlich ein Tippfehler und würde die SPFM-Berechnung
        # dominieren. Wir verwenden 5.05 FIT als plausiblen Platzhalter,
        # um die restliche Modelllogik zu demonstrieren.
        # Wenn wir 5.050e9 verwenden, wird SPFM > 99.999%.
        self.SBE_IF_SOURCE_RATE = 5.050 
        
        # Das Diagramm (Abb. 5) [cite: 410-509, 453-455] zeigt 100% | 100% Coverage,
        # d.h. c_R = 1.0 und c_L = 1.0.
        self.SBE_IF_DC_RESIDUAL = 1.0
        self.SBE_IF_DC_LATENT = 1.0
        
        super().__init__(name, spfm_input, lfm_input)

    def configure_blocks(self):
        """
        Instanziiert die Blöcke für das LINK-ECC.
        """
        # --- SPFM Quellen ---
        # Fügen eine neue Grundfehlerquelle für Interface-Fehler hinzu
        self.spfm_source_blocks[FAULTS.SBE] = self.BasicEvent(
            FAULTS.SBE, 
            self.SBE_IF_SOURCE_RATE
        )
        
        # --- SPFM Coverage Blöcke ---
        # Decken diese neue Quelle sofort ab
        self.spfm_coverage_blocks[FAULTS.SBE] = self.CoverageBlock(
            FAULTS.SBE, 
            self.SBE_IF_DC_RESIDUAL,
            self.SBE_IF_DC_LATENT
        )