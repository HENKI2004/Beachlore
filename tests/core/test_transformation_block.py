from ecc_analyzer.core import TransformationBlock
from ecc_analyzer.interfaces import FaultType

# --- Transformation Block ---


def test_transformation_block_initialization():
    tb = TransformationBlock(source_fault=FaultType.SBE, target_fault=FaultType.MBE, factor=0.5)

    assert tb.source == FaultType.SBE
    assert tb.target == FaultType.MBE
    assert tb.factor == 0.5


def test_transformation_block_compute_fit_accumulation():
    tb = TransformationBlock(source_fault=FaultType.SBE, target_fault=FaultType.MBE, factor=0.5)

    spfm_in = {FaultType.SBE: 100.0, FaultType.MBE: 10.0}
    lfm_in = {FaultType.SBE: 5.0}

    spfm_out, lfm_out = tb.compute_fit(spfm_in, lfm_in)

    assert spfm_out[FaultType.SBE] == 100.0
    assert spfm_out[FaultType.MBE] == 60.0
    assert lfm_out == lfm_in
    assert lfm_out is not lfm_in


def test_transformation_block_missing_source():
    tb = TransformationBlock(FaultType.SBE, FaultType.MBE, 1.0)

    spfm_in = {FaultType.DBE: 20.0}
    spfm_out, _ = tb.compute_fit(spfm_in, {})

    assert spfm_out == spfm_in


def test_transformation_block_to_dict():
    tb = TransformationBlock(source_fault=FaultType.TBE, target_fault=FaultType.MBE, factor=0.56)

    expected = {"type": "TransformationBlock", "source_fault": "TBE", "target_fault": "MBE", "factor": 0.56}

    assert tb.to_dict() == expected
