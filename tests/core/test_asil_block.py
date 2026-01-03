import pytest

from ecc_analyzer.core import AsilBlock
from ecc_analyzer.interfaces import FaultType

# --- Asil Block ---


def test_asil_block_initialization():
    """Überprüft die korrekte Initialisierung des Namens."""
    block = AsilBlock("Final_Evaluator")
    assert block.name == "Final_Evaluator"


@pytest.mark.parametrize(
    "spfm, lfm, rf_sum, expected_asil",
    [
        (0.995, 0.95, 5.0, "ASIL D"),
        (0.98, 0.85, 50.0, "ASIL C"),
        (0.91, 0.65, 80.0, "ASIL B"),
        (0.80, 0.50, 500.0, "ASIL A"),
        (0.80, 0.50, 1500.0, "QM (Quality Management)"),
    ],
)
def test_determine_asil(spfm, lfm, rf_sum, expected_asil):
    """Testet die Logik zur Bestimmung des ASIL-Levels basierend auf den Anforderungen."""
    block = AsilBlock("Test")
    assert block._determine_asil(spfm, lfm, rf_sum) == expected_asil


def test_compute_metrics_calculation():
    """Überprüft die mathematische Berechnung von SPFM und LFM."""
    block = AsilBlock("MetricTest")

    lambda_total = 1000.0
    spfm_dict = {FaultType.SBE: 30.0, FaultType.DBE: 20.0}
    lfm_dict = {FaultType.MBE: 95.0}

    results = block.compute_metrics(lambda_total, spfm_dict, lfm_dict)

    assert results["SPFM"] == pytest.approx(0.95)
    assert results["LFM"] == pytest.approx(0.90)
    assert results["Lambda_RF_Sum"] == 50.0
    assert results["ASIL_Achieved"] == "ASIL B"


def test_compute_metrics_zero_total_fit():
    """Stellt sicher, dass das System nicht abstürzt, wenn die totale FIT-Rate 0 ist."""
    block = AsilBlock("ZeroTest")

    results = block.compute_metrics(0.0, {}, {})

    assert results["SPFM"] == 0.0
    assert results["LFM"] == 0.0
    assert results["ASIL_Achieved"] == "ASIL A"


def test_compute_metrics_full_coverage():
    """Testet den Fall einer perfekten Sicherheit (0 FIT Reste)."""
    block = AsilBlock("PerfectSystem")

    results = block.compute_metrics(100.0, {}, {})

    assert results["SPFM"] == 1.0
    assert results["LFM"] == 1.0
    assert results["ASIL_Achieved"] == "ASIL D"
