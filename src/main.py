"""Zentraler Einstiegspunkt zur Ausführung der Sicherheitsanalysen (LPDDR4 & LPDDR5)."""

from ecc_analyzer.models.lpddr4 import Lpddr4System
from ecc_analyzer.models.lpddr5 import Lpddr5System


def run_analysis_for_system(system, pipeline_name_for_detail="DRAM_Path"):
    """Hilfsfunktion, um doppelten Code für Analyse und Ausgabe zu vermeiden."""

    print(f"\n{'=' * 60}")
    print(f" ANALYSE GESTARTET: {system.name}")
    print(f"{'=' * 60}")

    metrics = system.run_analysis()

    print(f"\n--- Pipeline Details ({pipeline_name_for_detail}) ---")
    print(f"{'Stufe':<20} | {'Fehlerart':<10} | {'SPFM (FIT)':<12} | {'LFM (FIT)':<12}")
    print("-" * 65)

    target_pipeline = None
    if system.system_layout and hasattr(system.system_layout, "sub_blocks"):
        for sub_block in system.system_layout.sub_blocks:
            if hasattr(sub_block, "name") and sub_block.name == pipeline_name_for_detail:
                target_pipeline = sub_block
                break

    if target_pipeline and hasattr(target_pipeline, "blocks"):
        current_spfm = {}
        current_lfm = {}

        for stage in target_pipeline.blocks:
            current_spfm, current_lfm = stage.compute_fit(current_spfm, current_lfm)
            all_faults = set(current_spfm.keys()) | set(current_lfm.keys())

            if not all_faults:
                print(f"{stage.name:<20} | {'-':<10} | {'0.00':<12} | {'0.00':<12}")
            else:
                first_line = True
                for fault in sorted(all_faults, key=lambda x: x.name):
                    label = stage.name if first_line else ""
                    s_val = current_spfm.get(fault, 0.0)
                    l_val = current_lfm.get(fault, 0.0)
                    print(f"{label:<20} | {fault.name:<10} | {s_val:<12.2f} | {l_val:<12.2f}")
                    first_line = False
            print("-" * 65)
    else:
        print(f"WARNUNG: Pipeline '{pipeline_name_for_detail}' nicht gefunden.")

    print(f"\nERGEBNIS FÜR {system.name}:")
    print(f" SPFM:             {metrics['SPFM'] * 100.0:.2f}%")
    print(f" LFM:              {metrics['LFM'] * 100.0:.2f}%")
    print(f" Residual (RF):    {metrics['Lambda_RF_Sum']:.2f} FIT")
    print(f" ASIL:             {metrics['ASIL_Achieved']}")
    print("=" * 60)

    pdf_name = f"{system.name}_Report"
    print(f"Generiere PDF: {pdf_name}.pdf ...")
    system.generate_pdf(pdf_name)
    print("Fertig.\n")


def main():
    lpddr4 = Lpddr4System("LPDDR4_System", total_fit=4220.0)
    run_analysis_for_system(lpddr4)

    lpddr5 = Lpddr5System("LPDDR5_System", total_fit=4200.0)
    run_analysis_for_system(lpddr5)


if __name__ == "__main__":
    main()
