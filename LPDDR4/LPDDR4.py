import sys
import os
from collections import defaultdict

project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_root)

from Modules.Basic_Event import Basic_Event
from Modules.Asil_Block import ASIL_Block
from Modules.Base import FAULTS

from SEC import SEC
from DRAM_TRIM import DRAM_TRIM
from BUS_TRIM import BUS_TRIM
from SEC_DED import SEC_DED
from SEC_DED_TRIM import SEC_DED_TRIM
from Other_Components import Other_Components

def demonstrate_connection():
    

    DRAM_FIT = 2300.0
    OTHER_COMPONENTS_FIT = 1920 
    TOTAL_FIT = DRAM_FIT + OTHER_COMPONENTS_FIT

    SBE_RATE = 0.7 * DRAM_FIT       # 1610.0
    DBE_RATE = 0.0748 * DRAM_FIT    # 172.04
    MBE_RATE = 0.0748 * DRAM_FIT    # 172.04
    WD_RATE = 0.0748 * DRAM_FIT     # 172.04

  
    sbe_source = Basic_Event(FAULTS.SBE, SBE_RATE)
    dbe_source = Basic_Event(FAULTS.DBE, DBE_RATE)
    mbe_source = Basic_Event(FAULTS.MBE, MBE_RATE)
    wd_source = Basic_Event(FAULTS.WD, WD_RATE)
    

    spfm_input_rates = {
        sbe_source.output: sbe_source.compute_fit(),
        dbe_source.output: dbe_source.compute_fit(),
        mbe_source.output: mbe_source.compute_fit(),
        wd_source.output: wd_source.compute_fit()
    }

    lfm_input_rates = {}
    
    
    # Stufe 1: SEC
    sec = SEC("SEC", spfm_input_rates, lfm_input_rates)
    results_sec = sec.compute_fit()
    
    # Stufe 2: DRAM-TRIM
    trim = DRAM_TRIM("TRIM", results_sec["SPFM"], results_sec["LFM"])
    results_trim = trim.compute_fit()
    
    # Stufe 3: BUS-TRIM
    bus = BUS_TRIM("BUS", results_trim["SPFM"], results_trim["LFM"])
    results_bus = bus.compute_fit()
    
    # Stufe 4: SEC-DED 
    sec_ded = SEC_DED("SEC-DED", results_bus["SPFM"], results_bus["LFM"])
    results_sec_ded = sec_ded.compute_fit()

    # Stufe 5: SEC-DED-TRIM 
    sec_ded_trim = SEC_DED_TRIM("SEC-DED-TRIM", results_sec_ded["SPFM"], results_sec_ded["LFM"])
    results_final_dram = sec_ded_trim.compute_fit()

    # Stufe 6: Other Components 
    other_comp = Other_Components("OTHER", {}, {}) 
    results_other = other_comp.compute_fit()

    # --- 4. Finale Ergebnisse summieren ---
    final_spfm_rates = defaultdict(float)
    final_lfm_rates = defaultdict(float)

    # Alle SPFM-Ausgänge (Residual/Gefährlich) summieren
    for name, rate in results_final_dram['SPFM'].items():
        final_spfm_rates[name] += rate
    for name, rate in results_other['SPFM'].items():
        final_spfm_rates[name] += rate
        
    # Alle LFM-Ausgänge (Latent) summieren
    for name, rate in results_final_dram['LFM'].items():
        final_lfm_rates[name] += rate
    for name, rate in results_other['LFM'].items():
        final_lfm_rates[name] += rate

    # Gesamt-Summen für ASIL-Block berechnen
    lambda_dangerous_sum = sum(final_spfm_rates.values()) 
    lambda_latent_sum = sum(final_lfm_rates.values())     
    lambda_rf_sum = lambda_dangerous_sum 

    # --- 5. ASIL-Berechnung durchführen ---
    asil_calculator = ASIL_Block("Final_ASIL_Calculation")
    metrics = asil_calculator.compute_metrics(
        lambda_total = TOTAL_FIT,
        lambda_dangerous_sum = lambda_dangerous_sum,
        lambda_latent_sum = lambda_latent_sum,
        lambda_rf_sum = lambda_rf_sum
    )
    
    # --- 6. Ergebnisse ausgeben ---
    print(f"Total FIT Rate (Lambda_Total): {TOTAL_FIT:.2f} FIT\n")

    print("--- Final SPFM (Residual/Dangerous) Rates ---")
    for name, rate in final_spfm_rates.items():
        print(f"  {name.name}: {rate:.4f} FIT")
    print(f"==> Lambda_Dangerous_Sum (SPFM-Basis): {lambda_dangerous_sum:.4f} FIT\n")

    print("--- Final LFM (Latent) Rates ---")
    for name, rate in final_lfm_rates.items():
        print(f"  {name.name}: {rate:.4f} FIT")
    print(f"==> Lambda_Latent_Sum (LFM-Basis): {lambda_latent_sum:.4f} FIT\n")
    
    print("--- Final ISO 26262 Metrics ---")
    print(f"Single-Point Fault Metric (SPFM): {metrics['SPFM'] * 100.0:.2f}%")
    print(f"Latent Fault Metric (LFM):        {metrics['LFM'] * 100.0:.2f}%")
    print(f"Residual FIT Rate (Lambda_RF):    {metrics['Lambda_RF_Sum']:.2f} FIT")
    print(f"\n==> Achieved ASIL: {metrics['ASIL_Achieved']}")
        
demonstrate_connection()