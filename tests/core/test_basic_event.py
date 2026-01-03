from ecc_analyzer.core.basic_event import BasicEvent
from ecc_analyzer.interfaces import FaultType

# --- Basic Event ---


def test_basic_event_initialization():
    """Verify that BasicEvent attributes are set correctly, including defaults."""
    be = BasicEvent(fault_type=FaultType.SBE, rate=120.5, is_spfm=False)
    assert be.lambda_BE == 120.5
    assert be.fault_type == FaultType.SBE
    assert be.is_spfm is False

    be_default = BasicEvent(FaultType.SBE, 100.0)
    assert be_default.is_spfm is True


def test_basic_event_compute_fit_accumulation():
    """Verify compute_fit correctly adds to existing rates (accumulation)."""
    be = BasicEvent(FaultType.SBE, 50.0, is_spfm=True)

    spfm_in = {FaultType.SBE: 100.0}
    lfm_in = {FaultType.SBE: 10.0}

    spfm_out, lfm_out = be.compute_fit(spfm_in, lfm_in)

    assert spfm_out[FaultType.SBE] == 150.0
    assert lfm_out[FaultType.SBE] == 10.0


def test_basic_event_to_dict():
    """Verify the serialization logic for BlockFactory compatibility."""
    be = BasicEvent(FaultType.DBE, 75.0, is_spfm=True)
    expected_dict = {"type": "BasicEvent", "fault_type": FaultType.DBE.name, "rate": 75.0, "is_spfm": True}
    assert be.to_dict() == expected_dict
