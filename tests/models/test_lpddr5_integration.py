import pytest

from ecc_analyzer.interfaces import FaultType
from ecc_analyzer.models.lpddr5 import Events, Lpddr5System


def test_lpddr5_system_initialization():
    """Verify that the LPDDR5 system initializes with the correct name and total FIT."""
    system = Lpddr5System("LPDDR5_Test_Unit", total_fit=5000.0)
    assert system.name == "LPDDR5_Test_Unit"
    assert system.total_fit == 5000.0
    assert system.system_layout is not None


def test_lpddr5_events_injection():
    """Verify the primary failure rate injection in the LPDDR5 Events component."""
    events = Events("DRAM_Source_Test")

    spfm_out, lfm_out = events.compute_fit({}, {})

    assert spfm_out[FaultType.SBE] == pytest.approx(1610.0)
    assert spfm_out[FaultType.DBE] == pytest.approx(172.04)
    assert spfm_out[FaultType.MBE] == pytest.approx(172.04)
    assert spfm_out[FaultType.WD] == pytest.approx(172.04)


def test_lpddr5_full_analysis_run():
    """Perform a full analysis run on the LPDDR5 model and check for metric consistency."""
    total_system_fit = 10000.0
    system = Lpddr5System("Full_LPDDR5_Analysis", total_fit=total_system_fit)

    results = system.run_analysis()

    assert "SPFM" in results
    assert "LFM" in results
    assert "ASIL_Achieved" in results
    assert "Lambda_RF_Sum" in results

    assert 0.0 <= results["SPFM"] <= 1.0
    assert results["Lambda_RF_Sum"] <= total_system_fit


def test_lpddr5_system_structure():
    """Verify the hierarchical composition of the LPDDR5 system layout."""
    system = Lpddr5System("Structure_Test", total_fit=0.0)

    layout = system.system_layout
    assert layout.name == "Structure_Test"
    assert len(layout.sub_blocks) == 2

    dram_path = layout.sub_blocks[0]
    assert dram_path.name == "DRAM_Path"
    assert len(dram_path.sub_blocks) == 7
