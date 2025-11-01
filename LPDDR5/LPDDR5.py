# Beachlore/LPDDR5/LPDDR5.py

import sys
import os
from collections import defaultdict

# --- Setup Project Root ---
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# --- Import Module ---
from Modules.Basic_Event import Basic_Event
from Modules.Asil_Block import ASIL_Block
from Modules.Base import FAULTS

# --- Import LPDDR5 Komponenten ---
# (Stelle sicher, dass alle diese Dateien in Beachlore/LPDDR5/ existieren)
from SEC import SEC
from DRAM_TRIM import DRAM_TRIM
from BUS_TRIM import BUS_TRIM
from LINK_ECC import LINK_ECC  
from SEC_DED import SEC_DED
from SEC_DED_TRIM import SEC_DED_TRIM
from Other_Components import Other_Components 

def demonstrate_lpddr5_connection():
    
    # --- 1. System-Parameter definieren ---
    # Wir nehmen die LPDDR4 DRAM-Raten an, da das Paper [11] zitiert [cite: 366]
    DRAM_FIT = 2300.0
    SBE_RATE = 0.7 * DRAM_FIT       # 1610.0
    DBE_RATE = 0.0748 * DRAM_FIT    # 172.04
    MBE_RATE = 0.0748 * DRAM_FIT    # 172.04
    WD_RATE = 0.0748 * DRAM_FIT     # 172.04
    
    # Der SBE_IF-Fehler (vom LINK_ECC-Block)
    # HINWEIS: Wir verwenden 5.05 FIT als Platzhalter.
    # Der Wert im Paper (5.050e9 FIT) [cite: 386] ist widersprüchlich.
    SBE_IF_RATE = 5.05 
    
    # Der "Other" Block ist nur eine 9.5 FIT RF-Quelle 
    OTHER_RF_RATE = 9.5
    
    # Gesamt-FIT für die Metrikberechnung
    # (Summe der *Basis*-Fehlerquellen)
    TOTAL_FIT = DRAM_FIT + SBE_IF_RATE

    # --- 2. Basic Events (DRAM-Quellen) instanziieren ---
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
    
    # --- 3. Komponenten-Kette durchlaufen (LPDDR5-Modell) ---
    
    # Stufe 1: SEC
    sec = SEC("SEC", spfm_input_rates, lfm_input_rates)
    results_sec = sec.compute_fit()

    # Stufe 2: DRAM-TRIM
    trim = DRAM_TRIM("TRIM", results_sec["SPFM"], {})
    results_trim = trim.compute_fit()
    
    # Stufe 3: BUS-TRIM
    bus = BUS_TRIM("BUS", results_trim["SPFM"], {})
    results_bus = bus.compute_fit()
    
    # Stufe 4: LINK-ECC (NEU)
    # Dieses Modul fügt seine *eigene* SBE_IF-Quelle hinzu
    link_ecc = LINK_ECC("LINK-ECC", results_bus["SPFM"], {})
    results_link_ecc = link_ecc.compute_fit()

    # Stufe 5: SEC-DED
    sec_ded = SEC_DED("SEC-DED", results_link_ecc["SPFM"], {})
    results_sec_ded = sec_ded.compute_fit()
    
    # Stufe 6: SEC-DED-TRIM
    sec_ded_trim = SEC_DED_TRIM("SEC-DED-TRIM", results_sec_ded["SPFM"], {})
    results_final_dram = sec_ded_trim.compute_fit()
    
    # Stufe 7: Other Components (parallel)
    other_comp = Other_Components("OTHER", {}, {})
    results_other = other_comp.compute_fit()

    # --- 4. Finale Ergebnisse summieren ---
    final_spfm_rates = defaultdict(float)
    final_lfm_rates = defaultdict(float)

    for name, rate in results_final_dram['SPFM'].items():
        final_spfm_rates[name] += rate
    for name, rate in results_other['SPFM'].items():
        final_spfm_rates[name] += rate
        
    
    for name, rate in results_sec["LFM"].items():
        final_lfm_rates[name] += rate
    for name, rate in results_trim["LFM"].items():
        final_lfm_rates[name] += rate
    for name, rate in results_bus["LFM"].items():
        final_lfm_rates[name] += rate
    for name, rate in results_link_ecc["LFM"].items():
        final_lfm_rates[name] += rate
    for name, rate in results_sec_ded["LFM"].items():
        final_lfm_rates[name] += rate
    for name, rate in results_final_dram['LFM'].items():
        final_lfm_rates[name] += rate
    for name, rate in results_other['LFM'].items():
        final_lfm_rates[name] += rate

    lambda_dangerous_sum = sum(final_spfm_rates.values())
    lambda_latent_sum = sum(final_lfm_rates.values())
    lambda_rf_sum = lambda_dangerous_sum 

    # --- 5. ASIL-Berechnung ---
    asil_calculator = ASIL_Block("Final_ASIL_Calculation")
    metrics = asil_calculator.compute_metrics(
        lambda_total = TOTAL_FIT,
        lambda_dangerous_sum = lambda_dangerous_sum,
        lambda_latent_sum = lambda_latent_sum,
        lambda_rf_sum = lambda_rf_sum
    )
    
    # --- 6. Ergebnisse ausgeben ---
    print(f"--- LPDDR5 Safety Analysis (Steiner et al., 2025) ---")
    print(f"Total FIT Rate (Lambda_Total): {TOTAL_FIT:.2f} FIT")
    print(f"(DRAM={DRAM_FIT:.2f} + SBE_IF={SBE_IF_RATE:.2f})\n")

    print("--- Final SPFM (Residual/Dangerous) Rates ---")
    for name, rate in sorted(final_spfm_rates.items(), key=lambda item: item[0].name):
        print(f"  {name.name}: {rate:.4f} FIT")
    print(f"==> Lambda_Dangerous_Sum (SPFM-Basis): {lambda_dangerous_sum:.4f} FIT\n")

    print("--- Final LFM (Latent) Rates ---")
    for name, rate in sorted(final_lfm_rates.items(), key=lambda item: item[0].name):
        print(f"  {name.name}: {rate:.4f} FIT")
    print(f"==> Lambda_Latent_Sum (LFM-Basis): {lambda_latent_sum:.4f} FIT\n")
    
    print("--- Final ISO 26262 Metrics (Calculated) ---")
    print(f"Single-Point Fault Metric (SPFM): {metrics['SPFM'] * 100.0:.2f}%")
    print(f"Latent Fault Metric (LFM):        {metrics['LFM'] * 100.0:.2f}%")
    print(f"Residual FIT Rate (Lambda_RF):    {metrics['Lambda_RF_Sum']:.2f} FIT")
    print(f"\n==> Achieved ASIL: {metrics['ASIL_Achieved']}\n")
    
    print("--- HINWEIS ZU DEN PAPER-WERTEN ---")
    print(f"Die im LPDDR5-Paper (Abb. 5) [cite: 435] gezeigten Metriken")
    print(f"(SPFM=80.45%, LFM=54.86%) sind mathematisch nicht mit")
    print(f"den Komponentenwerten (RF=411.9 [cite: 419], LFM=1696.3 [cite: 434], Other=9.5 )")
    print(f"und den Formeln des Papers [cite: 203, 205] vereinbar.")
    print(f"Die obigen Ergebnisse replizieren die *Architektur* und *Logik* des Papers.")

demonstrate_lpddr5_connection()