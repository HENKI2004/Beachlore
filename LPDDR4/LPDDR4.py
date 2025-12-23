import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from Modules import System_Base, Pipeline_Block, Sum_Block, FAULTS
from Events import Events
from SEC import SEC
from DRAM_TRIM import DRAM_TRIM
from BUS_TRIM import BUS_TRIM
from SEC_DED import SEC_DED
from SEC_DED_TRIM import SEC_DED_TRIM
from Other_Components import Other_Components

class LPDDR4_System(System_Base):
    """
    Top-level system model for the LPDDR4 hardware architecture.
    Coordinates the connection of all sub-components and defines the overall system layout.
    """

    def configure_system(self):
        """
        Defines the hierarchical structure of the LPDDR4 system.
        Constructs the main DRAM processing chain and merges it with other hardware components.
        """
        main_chain = Pipeline_Block("DRAM_Path", [
            Events("Source"),
            SEC("SEC"),
            DRAM_TRIM("TRIM"),
            BUS_TRIM("BUS"),
            SEC_DED("SEC-DED"),
            SEC_DED_TRIM("SEC-DED-TRIM")
        ])

        self.system_layout = Sum_Block(self.name, [
            main_chain,
            Other_Components("Other_HW")
        ])

if __name__ == "__main__":
    lpddr4 = LPDDR4_System("LPDDR4_Full_System", total_fit=4220.0)
    
    metrics = lpddr4.run_analysis()
    
    print("=" * 45)
    print(f" FINAL SYSTEM METRICS: {lpddr4.name}")
    print("=" * 45)
    print(f" Total FIT Rate:          {lpddr4.total_fit:.2f} FIT")
    print(f" Residual FIT Rate (RF):  {metrics['Lambda_RF_Sum']:.2f} FIT")
    print("-" * 45)
    print(f" SPFM Metric:             {metrics['SPFM'] * 100.0:.2f}%")
    print(f" LFM Metric:              {metrics['LFM'] * 100.0:.2f}%")
    print("-" * 45)
    print(f" ACHIEVED ASIL:           {metrics['ASIL_Achieved']}")
    print("=" * 45)
    
    lpddr4.generate_pdf("LPDDR4_Safety_Architecture")