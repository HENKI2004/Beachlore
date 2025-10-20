import sys
import os

project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_root)

from Modules.Basic_Event import Basic_Event
from SEC import SEC
from DRAM_TRIM import DRAM_TRIM
from BUS_TRIM import BUS_TRIM
from Modules.Base import FAULTS

def demonstrate_connection():
    
    SBE_RATE = 1610.0
    DBE_RATE = 172.0
    MBE_RATE = 172.0
    WD_RATE = 172.0

    sbe_source = Basic_Event(FAULTS.SBE, SBE_RATE)
    dbe_source = Basic_Event(FAULTS.DBE, DBE_RATE)
    mbe_source = Basic_Event(FAULTS.MBE, MBE_RATE)
    wd_source = Basic_Event(FAULTS.WD, WD_RATE)
    
    spfm_input_rates = {
        sbe_source.output: sbe_source.get_output_rate(),
        dbe_source.output: dbe_source.get_output_rate(),
        mbe_source.output: mbe_source.get_output_rate(),
        wd_source.output: wd_source.get_output_rate()
    }
    lfm_input_rates = {}
    
    sec = SEC("SEC",
            spfm_input_rates,
            lfm_input_rates)
    results = sec.computefit()
    trim = DRAM_TRIM("TRIM",
            results["SPFM"],
            results["LFM"])
    results = trim.computefit()
    bus = BUS_TRIM("BUS",
                results["SPFM"],
                results["LFM"])
    results = bus.computefit()
    
    print("--- Final FIT Results ---")  
    print(f"Total SPFM (Residual/Dangerous) Rates:")
    for name, rate in results['SPFM'].items():
        print(f"  {name}: {rate:.2f} FIT")

    print("\nTotal LFM (Latent) Rates:")
    for name, rate in results['LFM'].items():
        print(f"  {name}: {rate:.2f} FIT")
        
demonstrate_connection()