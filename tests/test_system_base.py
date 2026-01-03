import json

import pytest

from ecc_analyzer.core import BasicEvent, SumBlock
from ecc_analyzer.interfaces import FaultType
from ecc_analyzer.system_base import SystemBase


class MockSafetySystem(SystemBase):
    """Concrete implementation of SystemBase for testing purposes."""

    def configure_system(self):
        """Standard configuration for testing."""
        if self.system_layout is None:
            self.system_layout = SumBlock("TestLayout", [BasicEvent(FaultType.SBE, 100.0)])


def test_system_base_initialization():
    """Verify that SystemBase initializes with name and total FIT correctly."""
    system = MockSafetySystem("TestSystem", total_fit=1000.0)
    assert system.name == "TestSystem"
    assert system.total_fit == 1000.0
    assert system.asil_block.name == "Final_Evaluation"


def test_system_base_run_analysis_unconfigured():
    """Verify that run_analysis raises ValueError if no layout is set."""
    system = MockSafetySystem("EmptySystem", total_fit=1000.0)
    system.system_layout = None
    with pytest.raises(ValueError, match="System layout is not configured."):
        system.run_analysis()


def test_system_base_run_analysis_results():
    """Verify that run_analysis returns expected metrics."""
    system = MockSafetySystem("AnalysisSystem", total_fit=1000.0)
    metrics = system.run_analysis()

    assert metrics["SPFM"] == pytest.approx(0.90)
    assert metrics["Lambda_RF_Sum"] == 100.0
    assert "ASIL_Achieved" in metrics


def test_system_base_json_io(tmp_path):
    """Verify saving to and loading from a JSON file."""
    system_save = MockSafetySystem("SaveSystem", total_fit=500.0)
    file_path = tmp_path / "system.json"

    system_save.save_to_json(str(file_path))

    assert file_path.exists()
    with open(file_path, "r") as f:
        data = json.load(f)
    assert data["type"] == "SumBlock"

    system_load = MockSafetySystem("LoadSystem", total_fit=500.0)
    system_load.load_from_json(str(file_path))

    assert system_load.system_layout.name == "TestLayout"
    assert len(system_load.system_layout.sub_blocks) == 1
    assert system_load.system_layout.sub_blocks[0].lambda_BE == 100.0


def test_system_base_yaml_io(tmp_path):
    """Verify saving to and loading from a YAML file."""
    system_save = MockSafetySystem("YamlSystem", total_fit=500.0)
    file_path = tmp_path / "system.yaml"

    system_save.save_to_yaml(str(file_path))

    assert file_path.exists()

    system_load = MockSafetySystem("LoadYaml", total_fit=500.0)
    system_load.load_from_yaml(str(file_path))

    assert system_load.system_layout.name == "TestLayout"
    assert system_load.system_layout.sub_blocks[0].fault_type == FaultType.SBE
