import sys
import os

# Pfad zum Hauptverzeichnis hinzufügen
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# Importe aus den Modules (Paket-Import funktioniert hier)
from Modules import System_Base, Pipeline_Block, Sum_Block, FAULTS

# Lokale Importe (Da diese Dateien im gleichen Ordner liegen)
from Events import Events
from SEC import SEC
from DRAM_TRIM import DRAM_TRIM
from BUS_TRIM import BUS_TRIM
from SEC_DED import SEC_DED
from SEC_DED_TRIM import SEC_DED_TRIM
from Other_Components import Other_Components

class LPDDR4_System(System_Base):
    def configure_system(self):
        # Die Hauptkette der LPDDR4-Hardware
        main_chain = Pipeline_Block("DRAM_Path", [
            Events("Source"),
            SEC("SEC"),
            DRAM_TRIM("TRIM"),
            BUS_TRIM("BUS"),
            SEC_DED("SEC-DED"),
            SEC_DED_TRIM("SEC-DED-TRIM")
        ])

        # Zusammenführung mit Other Components (wie in deinem Sum_Block Wunsch)
        self.system_layout = Sum_Block(self.name, [
            main_chain,
            Other_Components("Other_HW")
        ])

# --- Ausführung ---
if __name__ == "__main__":
    # DRAM_FIT (2300) + Other (1920) = 4220
    lpddr4 = LPDDR4_System("LPDDR4_Full_System", total_fit=4220.0)
    
    # 1. Rechnen
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
    
    # 2. PDF erstellen
    lpddr4.generate_pdf("LPDDR4_Safety_Architecture")