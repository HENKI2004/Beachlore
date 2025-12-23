import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)
    
from Modules.Asil_Block import ASIL_Block
from Modules.Faults import FAULTS

from SEC import SEC
from DRAM_TRIM import DRAM_TRIM
from BUS_TRIM import BUS_TRIM
from SEC_DED import SEC_DED
from SEC_DED_TRIM import SEC_DED_TRIM
from Other_Components import Other_Components

def demonstrate_connection():
    DRAM_FIT = 2300.0
    TOTAL_FIT = DRAM_FIT + 1920 

    current_spfm = {
        FAULTS.SBE: 0.7 * DRAM_FIT,
        FAULTS.DBE: 0.0748 * DRAM_FIT,
        FAULTS.MBE: 0.0748 * DRAM_FIT,
        FAULTS.WD: 0.0748 * DRAM_FIT
    }
    current_lfm = {}

    chain = [
        SEC("SEC"),
        DRAM_TRIM("TRIM"),
        BUS_TRIM("BUS"),
        SEC_DED("SEC-DED"),
        SEC_DED_TRIM("SEC-DED-TRIM")
    ]

    print(f"Initial Total FIT: {TOTAL_FIT}\n")

    for component in chain:
        current_spfm, current_lfm = component.compute_fit(current_spfm, current_lfm)
        
        print(f"--- Stage: {component.name} ---")
        print(f"  Residual SPFM Sum: {sum(current_spfm.values()):.2f} FIT")
        print(f"  Latent LFM Sum:   {sum(current_lfm.values()):.2f} FIT")
        print(f"  Details SPFM: {current_spfm}\n")
        print(f"  Details SPFM: {current_lfm} \n")

    other_comp = Other_Components("OTHER")

    other_res_spfm, other_res_lfm = other_comp.compute_fit({}, {})

    final_spfm = current_spfm.copy()
    for fault, rate in other_res_spfm.items():
        final_spfm[fault] = final_spfm.get(fault, 0.0) + rate
        
    final_lfm = current_lfm.copy()
    for fault, rate in other_res_lfm.items():
        final_lfm[fault] = final_lfm.get(fault, 0.0) + rate

    asil_calculator = ASIL_Block("Final_ASIL_Calculation")
    metrics = asil_calculator.compute_metrics(TOTAL_FIT, final_spfm, final_lfm)
    
    print("=" * 40)
    print("FINAL SYSTEM METRICS (ISO 26262)")
    print("=" * 40)
    print(f"Total FIT Rate:      {TOTAL_FIT:.2f}")
    print(f"Residual FIT (RF):   {metrics['Lambda_RF_Sum']:.2f} FIT")
    print(f"SPFM Metric:         {metrics['SPFM'] * 100:.2f}%")
    print(f"LFM Metric:          {metrics['LFM'] * 100:.2f}%")
    print(f"Achieved ASIL:       {metrics['ASIL_Achieved']}")
    print("=" * 40)

if __name__ == "__main__":
    demonstrate_connection()