import pytest

from ecc_analyzer.core import CoverageBlock
from ecc_analyzer.interfaces import FaultType

# --- Coverage Block ---


def test_coverage_block_initialization_defaults():
    """Prüft die Standard-Initialisierung und die automatische Berechnung von c_L."""
    cb = CoverageBlock(target_fault=FaultType.SBE, dc_rate_c_or_cR=0.9)
    assert cb.target_fault == FaultType.SBE
    assert cb.c_R == 0.9
    assert cb.c_L == pytest.approx(0.1)
    assert cb.is_spfm is True


def test_coverage_block_initialization_custom_cl():
    """Prüft die Initialisierung mit einem explizit gesetzten c_L Wert."""
    cb = CoverageBlock(target_fault=FaultType.DBE, dc_rate_c_or_cR=0.9, dc_rate_latent_cL=0.6, is_spfm=False)
    assert cb.c_R == 0.9
    assert cb.c_L == 0.6
    assert cb.is_spfm is False


def test_coverage_block_compute_fit_spfm_path():
    """Verifiziert die Aufteilung von FIT-Raten im SPFM-Pfad in Residual (SPFM) und Latent (LFM)."""
    cb = CoverageBlock(FaultType.SBE, dc_rate_c_or_cR=0.9, dc_rate_latent_cL=0.8, is_spfm=True)

    spfm_in = {FaultType.SBE: 100.0}
    lfm_in = {FaultType.SBE: 0.0}

    spfm_out, lfm_out = cb.compute_fit(spfm_in, lfm_in)

    assert spfm_out[FaultType.SBE] == pytest.approx(10.0)
    assert lfm_out[FaultType.SBE] == pytest.approx(20.0)


def test_coverage_block_compute_fit_lfm_path():
    """Verifiziert die Reduktion von FIT-Raten im reinen LFM-Pfad."""
    cb = CoverageBlock(FaultType.DBE, dc_rate_c_or_cR=0.7, is_spfm=False)

    spfm_in = {}
    lfm_in = {FaultType.DBE: 50.0}

    spfm_out, lfm_out = cb.compute_fit(spfm_in, lfm_in)

    assert FaultType.DBE not in spfm_out
    assert lfm_out[FaultType.DBE] == pytest.approx(15.0)


def test_coverage_block_compute_fit_no_target():
    """Stellt sicher, dass die Raten unverändert bleiben, wenn der Fehlertyp nicht existiert."""
    cb = CoverageBlock(FaultType.MBE, dc_rate_c_or_cR=0.9)

    spfm_in = {FaultType.SBE: 10.0}
    lfm_in = {FaultType.SBE: 5.0}

    spfm_out, lfm_out = cb.compute_fit(spfm_in, lfm_in)

    assert spfm_out == spfm_in
    assert lfm_out == lfm_in


def test_coverage_block_to_dict():
    """Prüft die Serialisierung für den Export/Import via BlockFactory."""
    cb = CoverageBlock(FaultType.SBE, dc_rate_c_or_cR=0.9, dc_rate_latent_cL=0.1, is_spfm=True)
    expected = {"type": "CoverageBlock", "target_fault": "SBE", "dc_rate_c_or_cR": 0.9, "dc_rate_latent_cL": 0.1, "is_spfm": True}
    assert cb.to_dict() == expected
