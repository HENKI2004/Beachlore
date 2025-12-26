"""Implements the wrapper for logic blocks with output port management."""

# Copyright (c) 2025 Linus Held. All rights reserved.

from ..interfaces import BlockInterface, FaultType, ObservableInterface, SafetyObserver


class ObservableBlock(ObservableInterface):
    """A wrapper class that encapsulates a logic block.

    Manages both mathematical results (via the wrapped block) and visual output
    ports (via observers).
    """

    def __init__(self, logic_block: BlockInterface):
        """Initializes the observable wrapper.

        Args:
            logic_block (BlockInterface): The pure mathematical block to be wrapped.
        """
        self.block = logic_block
        self._observers = []

    def attach(self, observer: SafetyObserver):
        """Registers an observer.

        Args:
            observer (SafetyObserver): The SafetyObserver instance to be registered.
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def run(
        self,
        spfm_in: dict[FaultType, float],
        lfm_in: dict[FaultType, float],
        input_ports: dict,
    ) -> tuple[dict[FaultType, float], dict[FaultType, float], dict]:
        """Executes calculation and collects output ports from the observer.

        Args:
            spfm_in (dict[FaultType, float]): Incoming SPFM fault rates.
            lfm_in (dict[FaultType, float]): Incoming LFM fault rates.
            input_ports (dict): Mapping of incoming node IDs for visualization.

        Returns:
            tuple[dict[FaultType, float], dict[FaultType, float], dict]: A tuple containing:
                - Updated SPFM rates.
                - Updated LFM rates.
                - Output ports dictionary from the observer.
        """
        spfm_out, lfm_out = self.block.compute_fit(spfm_in, lfm_in)

        output_ports = self.notify(input_ports, spfm_in, lfm_in, spfm_out, lfm_out)

        return spfm_out, lfm_out, output_ports

    def notify(
        self,
        input_ports: dict,
        spfm_in: dict[FaultType, float],
        lfm_in: dict[FaultType, float],
        spfm_out: dict[FaultType, float],
        lfm_out: dict[FaultType, float],
    ) -> dict:
        """Broadcasts results and returns the visual ports created by the observer.

        Args:
            input_ports (dict): Incoming visual ports.
            spfm_in (dict[FaultType, float]): Incoming SPFM rates.
            lfm_in (dict[FaultType, float]): Incoming LFM rates.
            spfm_out (dict[FaultType, float]): Outgoing SPFM rates.
            lfm_out (dict[FaultType, float]): Outgoing LFM rates.

        Returns:
            dict: The visual output ports created by the observers.
        """
        last_created_ports = {}
        for observer in self._observers:
            ports = observer.on_block_computed(self.block, input_ports, spfm_in, lfm_in, spfm_out, lfm_out)
            if ports:
                last_created_ports = ports

        return last_created_ports
