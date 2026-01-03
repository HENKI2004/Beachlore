import pytest

from ecc_analyzer.core import CoverageBlock, PipelineBlock
from ecc_analyzer.core.basic_event import BasicEvent
from ecc_analyzer.interfaces import FaultType

# --- Pipeline Block ---


def test_pipeline_block_initialization():
    be1 = BasicEvent(FaultType.SBE, 10.0)
    be2 = BasicEvent(FaultType.DBE, 20.0)
    sub_blocks = [be1, be2]
    name = "TestPipeline"

    pipeline = PipelineBlock(name=name, sub_blocks=sub_blocks)

    assert pipeline.name == name
    assert pipeline.sub_blocks == sub_blocks


def test_pipeline_block_sequential_processing():
    be_source = BasicEvent(FaultType.SBE, 100.0)
    coverage = CoverageBlock(FaultType.SBE, dc_rate_c_or_cR=0.9, dc_rate_latent_cL=0.9)
    be_extra = BasicEvent(FaultType.SBE, 5.0)

    pipeline = PipelineBlock("Sequential_Test", [be_source, coverage, be_extra])

    spfm_out, lfm_out = pipeline.compute_fit({}, {})

    assert spfm_out[FaultType.SBE] == pytest.approx(15.0)
    assert lfm_out[FaultType.SBE] == pytest.approx(10.0)


def test_pipeline_block_empty():
    pipeline = PipelineBlock("EmptyPipeline", [])

    spfm_in = {FaultType.SBE: 50.0}
    lfm_in = {FaultType.DBE: 30.0}

    spfm_out, lfm_out = pipeline.compute_fit(spfm_in, lfm_in)

    assert spfm_out == spfm_in
    assert lfm_out == lfm_in


def test_pipeline_block_to_dict():
    be = BasicEvent(FaultType.SBE, 10.0, is_spfm=True)
    pipeline = PipelineBlock(name="SerialExport", sub_blocks=[be])

    expected = {"type": "PipelineBlock", "name": "SerialExport", "sub_blocks": [{"type": "BasicEvent", "fault_type": "SBE", "rate": 10.0, "is_spfm": True}]}

    assert pipeline.to_dict() == expected
