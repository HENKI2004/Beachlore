from ecc_analyzer.core import BasicEvent, ObservableBlock
from ecc_analyzer.interfaces import FaultType, SafetyObserver


class MockVisualizer(SafetyObserver):
    def __init__(self):
        self.received_data = []

    def on_block_computed(self, block, input_ports, spfm_in, lfm_in, spfm_out, lfm_out):
        """
        Record the data sent by the ObservableBlock.
        Matches the required signature from ObservableBlock.notify.
        """
        self.received_data.append({"name": block.__class__.__name__, "in_spfm": spfm_in, "out_spfm": spfm_out})
        return {}


def test_observable_block_notification():
    """Verify that ObservableBlock correctly notifies observers during computation."""
    raw_block = BasicEvent(FaultType.SBE, 100.0)
    observable = ObservableBlock(raw_block)

    mock_visualizer = MockVisualizer()
    observable.attach(mock_visualizer)

    spfm_in = {FaultType.DBE: 10.0}
    observable.compute_fit(spfm_in, {}, {})

    assert len(mock_visualizer.received_data) == 1
    data = mock_visualizer.received_data[0]
    assert data["name"] == "BasicEvent"
    assert data["in_spfm"][FaultType.DBE] == 10.0
    assert data["out_spfm"][FaultType.SBE] == 100.0
    assert data["out_spfm"][FaultType.DBE] == 10.0


def test_observable_block_detachment():
    """Verify that detached observers no longer receive updates."""
    observable = ObservableBlock(BasicEvent(FaultType.SBE, 10.0))
    mock_visualizer = MockVisualizer()

    observable.attach(mock_visualizer)
    observable.detach(mock_visualizer)

    observable.compute_fit({}, {}, {})
    assert len(mock_visualizer.received_data) == 0
