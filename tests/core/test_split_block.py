import pytest

from ecc_analyzer.core import SplitBlock
from ecc_analyzer.interfaces import FaultType

# --- Split Block ---


def test_split_block_initialization():
    rates = {FaultType.SBE: 0.6, FaultType.DBE: 0.4}
    sb = SplitBlock("DRAM_Split", FaultType.OTH, rates, is_spfm=True)

    assert sb.name == "DRAM_Split"
    assert sb.fault_to_split == FaultType.OTH
    assert sb.distribution_rates == rates
    assert sb.is_spfm is True


def test_split_block_invalid_rates():
    invalid_rates = {FaultType.SBE: 0.7, FaultType.DBE: 0.4}
    with pytest.raises(ValueError, match="Sum of distribution rates"):
        SplitBlock("InvalidSplit", FaultType.OTH, invalid_rates)


def test_split_block_compute_fit_spfm():
    rates = {FaultType.SBE: 0.7, FaultType.DBE: 0.3}
    sb = SplitBlock("SPFM_Split", FaultType.OTH, rates, is_spfm=True)

    spfm_in = {FaultType.OTH: 100.0}
    lfm_in = {}

    spfm_out, lfm_out = sb.compute_fit(spfm_in, lfm_in)

    assert FaultType.OTH not in spfm_out
    assert spfm_out[FaultType.SBE] == 70.0
    assert spfm_out[FaultType.DBE] == 30.0
    assert lfm_out == {}


def test_split_block_compute_fit_lfm():
    rates = {FaultType.SBE: 0.5, FaultType.DBE: 0.5}
    sb = SplitBlock("LFM_Split", FaultType.OTH, rates, is_spfm=False)

    spfm_in = {}
    lfm_in = {FaultType.OTH: 50.0}

    spfm_out, lfm_out = sb.compute_fit(spfm_in, lfm_in)

    assert FaultType.OTH not in lfm_out
    assert lfm_out[FaultType.SBE] == 25.0
    assert lfm_out[FaultType.DBE] == 25.0
    assert spfm_out == {}


def test_split_block_missing_source():
    rates = {FaultType.SBE: 1.0}
    sb = SplitBlock("MissingSource", FaultType.OTH, rates)

    spfm_in = {FaultType.DBE: 10.0}
    spfm_out, _ = sb.compute_fit(spfm_in, {})

    assert spfm_out == spfm_in


def test_split_block_to_dict():
    rates = {FaultType.SBE: 1.0}
    sb = SplitBlock("ExportTest", FaultType.OTH, rates, is_spfm=False)

    expected = {"type": "SplitBlock", "name": "ExportTest", "fault_to_split": "OTH", "distribution_rates": {"SBE": 1.0}, "is_spfm": False}

    assert sb.to_dict() == expected
