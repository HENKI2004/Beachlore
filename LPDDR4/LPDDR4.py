import sys
import os

project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_root)

from Modules.Basic_Event import Basic_Event
from Modules.Asil_Block import ASIL_Block
from Modules.Coverage_Block import Coverage_Block
from Modules.Split_Block import Split_Block
from Modules.Sum_Block import Sum_Block
from SEC import SEC

def demonstrate_connection(
    SEC
):
    
    SBE_RATE = 1610.0
    DBE_RATE = 172.0
    MBE_RATE = 172.0
    WD_RATE = 172.0

    sbe_source = Basic_Event("SBE", SBE_RATE)
    dbe_source = Basic_Event("DBE", DBE_RATE)
    mbe_source = Basic_Event("MBE", MBE_RATE)
    wd_source = Basic_Event("WD", WD_RATE)
    
    spfm_input_rates = {
        sbe_source.name: sbe_source.get_output_rate(),
        dbe_source.name: dbe_source.get_output_rate(),
        mbe_source.name: mbe_source.get_output_rate(),
        wd_source.name: wd_source.get_output_rate()
    }
    lfm_input_rates = {}
    
    sec = SEC("SEC",
            spfm_input_rates,
            lfm_input_rates,
            Coverage_Block, 
            Split_Block, 
            Sum_Block, 
            Basic_Event)
    
    results = sec.computefit()
    print("--- Final FIT Results ---")  
    print(f"Total SPFM (Residual/Dangerous) Rates:")
    for name, rate in results['SPFM'].items():
        print(f"  {name}: {rate:.2f} FIT")

    print("\nTotal LFM (Latent) Rates:")
    for name, rate in results['LFM'].items():
        print(f"  {name}: {rate:.2f} FIT")
        
demonstrate_connection(SEC)