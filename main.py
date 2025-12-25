# 
#  @file main.py
#  @author Linus Held 
#  @brief Entry point for the LPDDR4 safety analysis and visualization.
#  @version 1.0
#  @date 2025-12-25
# 

from Modules.System_Base import System_Base
from Modules.Core.Basic_Event import Basic_Event
from Modules.Core.Coverage_Block import Coverage_Block
from Modules.Core.Sum_Block import Sum_Block
from Modules.Core.Pipeline_Block import Pipeline_Block
from Modules.Interfaces.Faults import FAULTS

class LPDDR4_System(System_Base):
    """
    Concrete implementation of the LPDDR4 memory system safety model.
    Defines the hardware architecture by connecting logical blocks.
    """

    def configure_system(self):
        """
        Builds the LPDDR4 logic tree using the refactored core blocks.
        """

        mbe_event = Basic_Event(FAULTS.MBE, rate=15.5, is_spfm=True)
        az_event = Basic_Event(FAULTS.AZ, rate=5.2, is_spfm=True)

        mbe_logic = Coverage_Block(
            target_fault=FAULTS.MBE, 
            dc_rate_c_or_cR=0.90, 
            dc_rate_latent_cL=1.0
        )

        mbe_chain = Pipeline_Block("MBE_Safety_Chain", [mbe_event, mbe_logic])
        
        self.system_layout = Sum_Block("LPDDR4_Architecture", [
            mbe_chain,
            az_event
        ])

def main():
    TOTAL_SYSTEM_FIT = 100.0

    lpddr4 = LPDDR4_System("LPDDR4_Analysis", total_fit=TOTAL_SYSTEM_FIT)

    print(f"--- Starte Sicherheitsanalyse für: {lpddr4.name} ---")

    metrics = lpddr4.run_analysis()
    print("\nErgebnisse (Rein mathematisch):")
    print(f"  SPFM: {metrics['SPFM']*100:.2f}%")
    print(f"  LFM:  {metrics['LFM']*100:.2f}%")
    print(f"  ASIL: {metrics['ASIL_Achieved']}")

    print("\nGeneriere Architektur-Diagramm...")
    pdf_metrics = lpddr4.generate_pdf("LPDDR4_Safety_Architecture")
    
    print(f"PDF wurde erfolgreich erstellt. Finales ASIL-Level: {pdf_metrics['ASIL_Achieved']}")
    print("--- Analyse abgeschlossen ---")

if __name__ == "__main__":
    main()