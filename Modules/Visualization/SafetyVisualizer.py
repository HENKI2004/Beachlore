#  @file SafetyVisualizer.py
#  @author Linus Held 
#  @brief Implementation of the Graphviz-based safety observer.
#  @version 1.0
#  @date 2025-12-25
# 
#   @copyright Copyright (c) 2025 Linus Held. All rights reserved.

from graphviz import Digraph
from ..Interfaces import SafetyObserver
from ..Core import (
    Split_Block, Coverage_Block, Basic_Event, 
    Asil_Block, Pipeline_Block, Sum_Block, Transformation_Block
)

class SafetyVisualizer(SafetyObserver):
    """
    Concrete observer that generates a Graphviz visualization of the safety architecture.
    It maps logical blocks to visual representations and manages the layout.
    """

    def __init__(self, name: str):
        """
        Initializes the visualizer with a Graphviz Digraph.
        @param name The name of the resulting diagram.
        """
        self.dot = Digraph(name=name)
        self.dot.attr(rankdir='BT', nodesep='1.0', ranksep='0.6', splines='line')
        self.dot.attr('node', fixedsize='true')

    def on_block_computed(self, block, input_ports: dict, spfm_in: dict, lfm_in: dict, spfm_out: dict, lfm_out: dict) -> dict:
        """
        Draws the specific block based on its type and returns the output port mapping.
        """
        if isinstance(block, Basic_Event):
            return self._draw_basic_event(block, spfm_out)
        elif isinstance(block, Split_Block):
            return self._draw_split_block(block, input_ports, spfm_out, lfm_out)
        elif isinstance(block, Coverage_Block):
            return self._draw_coverage_block(block, input_ports, spfm_out, lfm_out)
        elif isinstance(block, Asil_Block):
            return self._draw_asil_block(block, input_ports, spfm_out, lfm_out)
        elif isinstance(block, Pipeline_Block):
            # Pass input rates because pipeline propagates them through children
            return self._draw_pipeline_block(block, input_ports, spfm_in, lfm_in)
        elif isinstance(block, Sum_Block):
            return self._draw_sum_block(block, input_ports, spfm_out, lfm_out)
        elif isinstance(block, Transformation_Block):
            return self._draw_transformation_block(block, input_ports, spfm_out, lfm_out)
        
        return input_ports

    def _draw_basic_event(self, block, spfm_out) -> dict:
        """
        Draws a circle for a FIT source (e.g., MBE, AZ).
        @return Mapping of fault types to the created node output port.
        """
        # Logic: Create circle node, use spfm_out for label
        return {}

    def _draw_split_block(self, block, input_ports, spfm_out, lfm_out) -> dict:
        """
        Draws the HTML-style table for a Split_Block and connects input edges.
        @return Mapping of fault types to the table output ports.
        """
        # Logic: Create HTML table node, connect input_ports:rf/latent to :s
        return {}

    def _draw_coverage_block(self, block, input_ports, spfm_out, lfm_out) -> dict:
        """
        Draws a diagnostic coverage block (usually a square or specialized table).
        """
        # Logic: Create coverage node, connect input_ports:rf/latent to :s
        return {}

    def _draw_asil_block(self, block, input_ports, spfm_out, lfm_out) -> dict:
        """
        Draws the final ASIL evaluation box with calculated metrics.
        """
        # Logic: Create large box at rank='sink', connect inputs
        return {}

    def _draw_pipeline_block(self, block, input_ports, spfm_in, lfm_in) -> dict:
        """
        Orchestrates the visualization of a sequential chain of blocks.
        """
        # Logic: This method triggers the drawing of child blocks in sequence
        return {}

    def _draw_sum_block(self, block, input_ports, spfm_out, lfm_out) -> dict:
        """
        Draws a parallel aggregation block including '+' summation nodes and subgraphs.
        """
        # Logic: Create subgraph, draw children, draw '+' nodes at rank='same'
        return {}

    def _draw_transformation_block(self, block, input_ports, spfm_out, lfm_out) -> dict:
        """
        Draws a block that transforms fault types (e.g. SBE to DBE).
        """
        # Logic: Create a transformation node, connect inputs to outputs
        return {}

    def render(self, filename: str):
        """
        Exports the current graph to a PDF file.
        @param filename The path/name for the exported file.
        """
        self.dot.render(filename, view=True)