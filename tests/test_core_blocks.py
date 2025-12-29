import pytest

from ecc_analyzer.core import CoverageBlock, SumBlock, TransformationBlock
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

    # SBE: 100 (init) + 10 (be1) + 5 (be2) = 115
    assert spfm_out[FaultType.SBE] == 115.0
    # DBE: 50 (init) + 20 (be3) = 70
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


# --- Coverage Block ---


def test_coverage_block_reduction():
    """Verify that CoverageBlock correctly reduces SPFM and LFM rates."""
    # 90% coverage for Residual (SPFM), 60% for Latent (LFM)
    cb = CoverageBlock(target_fault=FaultType.SBE, dc_rate_c_or_cR=0.9, dc_rate_latent_cL=0.6)

    # Starting with 100 FIT for both
    spfm_in = {FaultType.SBE: 100.0}
    lfm_in = {FaultType.SBE: 100.0}

    spfm_out, lfm_out = cb.compute_fit(spfm_in, lfm_in)

    # Residual: 100 * (1 - 0.9) = 10.0
    assert spfm_out[FaultType.SBE] == pytest.approx(10.0)
    # Latent: 100 * (1 - 0.6) +100 = 140.0
    assert lfm_out[FaultType.SBE] == pytest.approx(140.0)


def test_transformation_logic():
    """Verify that rates are moved from source to target fault type."""
    tb = TransformationBlock(source_fault=FaultType.SBE, target_fault=FaultType.MBE, factor=1.0)

    spfm_in = {FaultType.SBE: 50.0}
    spfm_out, _ = tb.compute_fit(spfm_in, {})

    # Source should be empty (or 0), Target should have the FIT
    assert spfm_out.get(FaultType.SBE, 0) == 50
    assert spfm_out[FaultType.MBE] == 50.0
