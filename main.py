#  @file main.py
#  @brief Zentraler Einstiegspunkt zur Ausführung der LPDDR4-Sicherheitsanalyse.

from LPDDR4.LPDDR4 import LPDDR4_System

def main():
    lpddr4 = LPDDR4_System("LPDDR4_Hardware_Analysis", total_fit=4220.0)

    print(f"--- Analyse gestartet für: {lpddr4.name} ---")

    metrics = lpddr4.run_analysis()

    print("=" * 45)
    print(f" SPFM Metrik:     {metrics['SPFM'] * 100.0:.2f}%")
    print(f" LFM Metrik:      {metrics['LFM'] * 100.0:.2f}%")
    print(f" Erreichtes ASIL: {metrics['ASIL_Achieved']}")
    print("=" * 45)

    print("Generiere Architektur-Diagramm...")
    lpddr4.generate_pdf("LPDDR4_Visualisierung_Final")
    print("PDF wurde erfolgreich erstellt.")

if __name__ == "__main__":
    main()