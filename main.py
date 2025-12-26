#  @file main.py
#  @brief Zentraler Einstiegspunkt zur Ausführung der LPDDR4-Sicherheitsanalyse mit Detail-Ausgabe.

from LPDDR4.LPDDR4 import LPDDR4_System

def main():
    # 1. System initialisieren
    # Stelle sicher, dass total_fit korrekt definiert ist
    lpddr4 = LPDDR4_System("LPDDR4", total_fit=4220.0)

    print(f"--- Analyse gestartet für: {lpddr4.name} ---")

    # 2. Gesamtanalyse durchführen (für Metriken)
    metrics = lpddr4.run_analysis()

    # 3. Detaillierte Ausgabe der Pipeline-Stufen (DRAM_Path)
    print("\n" + "=" * 60)
    print(f"{'PIPELINE STUFEN-ANALYSE (DRAM_Path)':^60}")
    print("=" * 60)
    print(f"{'Stufe':<15} | {'Fehlerart':<10} | {'SPFM (FIT)':<12} | {'LFM (FIT)':<12}")
    print("-" * 60)

    # Wir suchen den "DRAM_Path" Pipeline-Block innerhalb des System-Layouts
    dram_path_pipeline = None
    
    # Das System Layout ist ein Sum_Block, wir suchen in dessen Unterblöcken
    if lpddr4.system_layout and hasattr(lpddr4.system_layout, 'sub_blocks'):
        for sub_block in lpddr4.system_layout.sub_blocks:
            if hasattr(sub_block, 'name') and sub_block.name == "DRAM_Path":
                dram_path_pipeline = sub_block
                break
    
    if dram_path_pipeline and hasattr(dram_path_pipeline, 'blocks'):
        # Startwerte für die Pipeline-Simulation (leer am Anfang)
        current_spfm = {}
        current_lfm = {}

        # Iteriere durch jeden Block in der Pipeline (Source -> SEC -> ...)
        for stage in dram_path_pipeline.blocks:
            # Berechne das Ergebnis dieser spezifischen Stufe basierend auf dem Vorwert
            current_spfm, current_lfm = stage.compute_fit(current_spfm, current_lfm)
            
            # Sammle alle Fehlerarten, die an diesem Punkt existieren
            all_faults = set(current_spfm.keys()) | set(current_lfm.keys())
            
            if not all_faults:
                print(f"{stage.name:<15} | {'-':<10} | {'0.00':<12} | {'0.00':<12}")
            else:
                first_line = True
                # Sortiere Fehler für konsistente Ausgabe (z.B. DBE, MBE, SBE...)
                for fault in sorted(all_faults, key=lambda x: x.name):
                    stage_label = stage.name if first_line else ""
                    spfm_val = current_spfm.get(fault, 0.0)
                    lfm_val = current_lfm.get(fault, 0.0)
                    
                    print(f"{stage_label:<15} | {fault.name:<10} | {spfm_val:<12.2f} | {lfm_val:<12.2f}")
                    first_line = False
            
            print("-" * 60)
    else:
        print("WARNUNG: Konnte Pipeline 'DRAM_Path' für Detailanalyse nicht finden.")

    # 4. Zusammenfassung und PDF
    print("\n" + "=" * 60)
    print(f" GESAMT-ERGEBNIS")
    print("=" * 60)
    print(f" SPFM Metrik:      {metrics['SPFM'] * 100.0:.2f}%")
    print(f" LFM Metrik:       {metrics['LFM'] * 100.0:.2f}%")
    print(f" Erreichtes ASIL:  {metrics['ASIL_Achieved']}")
    print("=" * 60)

    print("\nGeneriere Architektur-Diagramm...")
    lpddr4.generate_pdf("LPDDR4_Visualisierung_Final")
    print("PDF wurde erfolgreich erstellt.")

if __name__ == "__main__":
    main()