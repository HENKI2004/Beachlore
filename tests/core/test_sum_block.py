from ecc_analyzer.core import SumBlock
from ecc_analyzer.core.basic_event import BasicEvent
from ecc_analyzer.interfaces import FaultType

# --- Sum Block ---


def test_sum_block_initialization():
    """Verify that SumBlock attributes are set correctly."""
    be1 = BasicEvent(FaultType.SBE, 10.0)
    sub_blocks = [be1]
    name = "TestSum"

    sb = SumBlock(name=name, sub_blocks=sub_blocks)

    assert sb.name == name
    assert sb.sub_blocks == sub_blocks


def test_sum_block_compute_fit_complex():
    """Verify SumBlock aggregates multiple fault types for both SPFM and LFM."""
    be1 = BasicEvent(FaultType.SBE, 10.0, is_spfm=True)
    be2 = BasicEvent(FaultType.SBE, 5.0, is_spfm=True)
    be3 = BasicEvent(FaultType.DBE, 20.0, is_spfm=False)

    sb = SumBlock(name="ComplexSum", sub_blocks=[be1, be2, be3])

    spfm_in = {FaultType.SBE: 100.0}
    lfm_in = {FaultType.DBE: 50.0}

    spfm_out, lfm_out = sb.compute_fit(spfm_in, lfm_in)

    assert spfm_out[FaultType.SBE] == 115.0
    assert lfm_out[FaultType.DBE] == 70.0


def test_sum_block_empty():
    """Verify SumBlock handles an empty list of sub-blocks."""
    sb = SumBlock(name="EmptySum", sub_blocks=[])

    spfm_in = {FaultType.SBE: 10.0}
    lfm_in = {FaultType.DBE: 5.0}

    spfm_out, lfm_out = sb.compute_fit(spfm_in, lfm_in)

    assert spfm_out == spfm_in
    assert lfm_out == lfm_in


def test_sum_block_to_dict():
    """Verify serialization of SumBlock and its recursive children."""
    be = BasicEvent(FaultType.SBE, 10.0, is_spfm=True)
    sb = SumBlock(name="ParentSum", sub_blocks=[be])

    expected = {"type": "SumBlock", "name": "ParentSum", "sub_blocks": [{"type": "BasicEvent", "fault_type": FaultType.SBE.name, "rate": 10.0, "is_spfm": True}]}
    assert sb.to_dict() == expected
