import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from graphviz import Digraph
from Modules.Faults import FAULTS
from Modules.Sum_Block import Sum_Block
from Modules.Pipeline_Block import Pipeline_Block
from Modules.Asil_Block import ASIL_Block

# Importe der Komponenten
from LPDDR4.Events import Events
from LPDDR4.SEC import SEC
from LPDDR4.DRAM_TRIM import DRAM_TRIM
from LPDDR4.BUS_TRIM import BUS_TRIM
from LPDDR4.SEC_DED import SEC_DED
from LPDDR4.SEC_DED_TRIM import SEC_DED_TRIM
from LPDDR4.Other_Components import Other_Components

def test_viz():
    dot = Digraph(comment='Safety Model Test')

    # Orthogonales Layout für rechte Winkel und saubere Ankerpunkte
    dot.attr(rankdir='BT', splines='ortho', newrank='true', nodesep='0.6', ranksep='0.8')

    # 1. Die Hauptkette der LPDDR4-Hardware definieren
    main_chain = Pipeline_Block("LPDDR4_Chain", [
        Events("Source"),
        SEC("SEC"),
        DRAM_TRIM("Dram_Trim"),
        BUS_TRIM("BUS_TRIM"),
        SEC_DED("SEC_DED"),
        SEC_DED_TRIM("SEC_DED_TRIM")
    ])

    # 2. Zusammenführung: Hauptkette + Sonstige Komponenten
    # Der Sum_Block sorgt dafür, dass alle Pfade (SBE, DBE, OTH, etc.) 
    # nebeneinander existieren und für den ASIL-Block bereitgestellt werden.
    final_junction = Sum_Block("Final_System_Junction", [
        main_chain,
        Other_Components("Other_HW")
    ])

    # 3. Das komplette System inklusive finaler ASIL-Berechnung
    test_system = Pipeline_Block("Complete_System_Model", [
        final_junction,
        ASIL_Block("Final_ASIL_Calculation")
    ])

    # 4. Die Visualisierung generieren (Start mit leerem Port-Dictionary)
    test_system.to_dot(dot, {})

    # 5. Ergebnis speichern und anzeigen
    output_path = 'test_output_safety_model'
    dot.render(output_path, view=True, format='pdf')
    print(f"Visualisierung wurde als {output_path}.pdf gespeichert.")

if __name__ == "__main__":
    test_viz()