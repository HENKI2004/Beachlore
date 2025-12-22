import sys
import os
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

    # Define initial rates directly as a dictionary
    spfm_input_rates = {
        FAULTS.SBE: 0.7 * DRAM_FIT,
        FAULTS.DBE: 0.0748 * DRAM_FIT,
        FAULTS.MBE: 0.0748 * DRAM_FIT,
        FAULTS.WD: 0.0748 * DRAM_FIT
    }
    lfm_input_rates = {}
    
    # Run the chain
    sec = SEC("SEC", spfm_input_rates, lfm_input_rates)
    res = sec.compute_fit()
    
    trim = DRAM_TRIM("TRIM", res["SPFM"], res["LFM"])
    res = trim.compute_fit()
    
    bus = BUS_TRIM("BUS", res["SPFM"], res["LFM"])
    res = bus.compute_fit()
    
    sec_ded = SEC_DED("SEC-DED", res["SPFM"], res["LFM"])
    res = sec_ded.compute_fit()

    sec_ded_trim = SEC_DED_TRIM("SEC-DED-TRIM", res["SPFM"], res["LFM"])
    final_dram = sec_ded_trim.compute_fit()

    other_comp = Other_Components("OTHER", {}, {}) 
    other_res = other_comp.compute_fit()

    # Aggregate dictionaries (Combine main chain and other components)
    final_spfm = final_dram['SPFM'].copy()
    for fault, rate in other_res['SPFM'].items():
        final_spfm[fault] = final_spfm.get(fault, 0.0) + rate
        
    final_lfm = final_dram['LFM'].copy()
    for fault, rate in other_res['LFM'].items():
        final_lfm[fault] = final_lfm.get(fault, 0.0) + rate

    # ASIL Calculation (Uses the new dictionary-based interface)
    asil_calculator = ASIL_Block("Final_ASIL_Calculation")
    metrics = asil_calculator.compute_metrics(TOTAL_FIT, final_spfm, final_lfm)
    
    # Output
    print(f"Total FIT: {TOTAL_FIT:.2f}\n")
    print(f"SPFM Metric: {metrics['SPFM'] * 100:.2f}%")
    print(f"LFM Metric: {metrics['LFM'] * 100:.2f}%")
    print(f"ASIL: {metrics['ASIL_Achieved']}")

if __name__ == "__main__":
    demonstrate_connection()