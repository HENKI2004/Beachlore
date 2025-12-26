# 
#  @file LPDDR4.py
#  @author Linus Held 
#  @brief Top-level system model for the LPDDR4 hardware architecture.
#  @version 2.0
#  @date 2025-12-25
# 
#  @copyright Copyright (c) 2025 Linus Held. All rights reserved.
# 

import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from Modules import System_Base
from Modules.Core import Pipeline_Block, Sum_Block
from Modules.Interfaces import FAULTS

from .Events import Events
from .SEC import SEC
from .DRAM_TRIM import DRAM_TRIM
from .BUS_TRIM import BUS_TRIM
from .SEC_DED import SEC_DED
from .SEC_DED_TRIM import SEC_DED_TRIM
from .Other_Components import Other_Components

class LPDDR4_System(System_Base):
    """
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
    # 1. System initialisieren
    # Der total_fit Wert dient hier nur als Platzhalter für die Initialisierung
    lpddr4 = LPDDR4_System("LPDDR4", total_fit=4220.0)

    print(f"\n{'='*70}")
    print(f" DEBUG-ANALYSE: {lpddr4.name}")
    print(f" (Werte nach jeder Verarbeitungsstufe)")
    print(f"{'='*70}")
    
    # Kopfzeile der Tabelle
    print(f"{'Block':<20} | {'Fehler':<10} | {'SPFM (FIT)':<12} | {'LFM (FIT)':<12}")
    print(f"{'-'*70}")

    # 2. Pipeline "DRAM_Path" im System suchen
    pipeline = None
    if lpddr4.system_layout and hasattr(lpddr4.system_layout, 'sub_blocks'):
        for block in lpddr4.system_layout.sub_blocks:
            if getattr(block, 'name', '') == "DRAM_Path":
                pipeline = block
                break
    
    # 3. Pipeline schrittweise durchrechnen
    if pipeline:
        # Startwerte (leer)
        current_spfm = {}
        current_lfm = {}

        for stage in pipeline.blocks:
            # Berechnung für den aktuellen Block
            # Wir nutzen compute_fit, das (hoffentlich) zustandslos arbeitet
            current_spfm, current_lfm = stage.compute_fit(current_spfm, current_lfm)
            
            # Welche Fehlerarten gibt es aktuell?
            all_faults = set(current_spfm.keys()) | set(current_lfm.keys())
            
            if not all_faults:
                print(f"{stage.name:<20} | {'-':<10} | {'0.00':<12} | {'0.00':<12}")
            else:
                first_line = True
                # Sortieren (z.B. alphabetisch oder nach Enum-Wert, hier Name)
                for fault in sorted(all_faults, key=lambda x: x.name):
                    block_name = stage.name if first_line else ""
                    spfm_val = current_spfm.get(fault, 0.0)
                    lfm_val = current_lfm.get(fault, 0.0)
                    
                    print(f"{block_name:<20} | {fault.name:<10} | {spfm_val:<12.2f} | {lfm_val:<12.2f}")
                    first_line = False
            
            print(f"{'-'*70}")
    else:
        print("FEHLER: Konnte Pipeline 'DRAM_Path' nicht im System finden.")
    
    print("\nFertig.")
