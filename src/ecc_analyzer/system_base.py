"""Orchestrates the safety analysis and coordinates visualization via observers."""

# Copyright (c) 2025 Linus Held. All rights reserved.

from abc import ABC, abstractmethod
from typing import Any, Optional

from .core import AsilBlock, ObservableBlock
from .visualization import SafetyVisualizer


class SystemBase(ABC):
    """Abstract base class for a safety system model.

    It manages the system layout, triggers FIT rate calculations, and
    handles the generation of architectural visualizations.
    """

    def __init__(self, name: str, total_fit: float):
        """Initializes the system orchestrator.

        Args:
            name (str): The descriptive name of the system (e.g., "LPDDR4_System").
            total_fit (float): The total FIT rate used as the baseline for metric calculations.
        """
        self.name = name
        self.total_fit = total_fit
        self.system_layout = None
        self.asil_block = AsilBlock("Final_Evaluation")
        self.configure_system()

    @abstractmethod
    def configure_system(self):
        """Abstract method to define the internal hardware structure.

        Must be implemented by subclasses to set the `self.system_layout`.
        """
        pass

    def run_analysis(self) -> dict[str, Any]:
        """Performs a pure mathematical FIT calculation across the system.

        No visualization is triggered during this call.

        Returns:
            dict[str, Any]: A dictionary containing calculated metrics (SPFM, LFM, ASIL level).

        Raises:
            ValueError: If `configure_system` has not set a valid system layout.
        """
        if not self.system_layout:
            raise ValueError("System layout is not configured.")

        final_spfm, final_lfm = self.system_layout.compute_fit({}, {})

        return self.asil_block.compute_metrics(self.total_fit, final_spfm, final_lfm)

    def generate_pdf(self, filename: Optional[str] = None) -> dict[str, Any]:
        """Executes the analysis while simultaneously generating a PDF visualization.

        Uses the Observer Pattern to decouple logic from Graphviz commands.

        Args:
            filename (Optional[str]): Optional name for the output file.
                Defaults to "output_<system_name>".

        Returns:
            dict[str, Any]: The final system metrics dictionary.
        """
        if filename is None:
            filename = f"output_{self.name}"

        visualizer = SafetyVisualizer(self.name)

        observable_layout = ObservableBlock(self.system_layout)
        observable_layout.attach(visualizer)

        final_spfm, final_lfm, last_ports = observable_layout.run({}, {}, {})

        visualizer.on_block_computed(
            self.asil_block,
            last_ports,
            final_spfm,
            final_lfm,
            final_spfm,
            final_lfm,
        )

        visualizer.render(filename)

        return self.asil_block.compute_metrics(self.total_fit, final_spfm, final_lfm)
