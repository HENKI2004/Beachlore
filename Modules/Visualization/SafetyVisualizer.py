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

    # --- Layout Constants ---
    BLOCK_WIDTH_PIXEL = "72"
    BLOCK_HEIGHT_PIXEL = "72"
    BLOCK_WIDTH_DEZIMAL = "1.0"
    BLOCK_HEIGHT_DEZIMAL = "1.0"

    HEADER_HEIGHT = "32"
    DATA_HEIGHT = "40"

    # --- Style Constants ---
    COLOR_HEADER = "gray90"
    COLOR_BG = "white"
    COLOR_RF = "red"
    COLOR_LATENT = "blue"
    COLOR_TEXT_SECONDARY = "gray50"
    STYLE_DOTTED = "dotted"
    STYLE_DASHED = "dashed"
    
    FONT_SIZE_HEADER = "9"
    FONT_SIZE_DATA = "8"

    # --- Graphviz Attributes ---
    BASIC_EVENT_SHAPE = "circle"
    TRUE = "true"
    FALSE = "false"
    COMPASS_NORTH = "n"
    COMPASS_SOUTH = "s"

    # --- ID & Group Prefixes ---
    PREFIX_NODE_BE = "be_"
    PREFIX_NODE_SPLIT = "split_"
    PREFIX_NODE_COV = "cov_"
    PREFIX_NODE_TRANS = "trans_"
    PREFIX_NODE_ASIL = "asil_"
    PREFIX_CLUSTER_SUM = "cluster_sum_"
    PREFIX_CLUSTER_PIPE = "cluster_pipe_"
    PREFIX_LANE = "lane_"
    RANK_SAME = "same"

    # --- Summation Node Constants ---
    PREFIX_NODE_SUM = "sum_"
    SUM_NODE_SHAPE = "circle"
    SUM_NODE_SIZE = "0.3"
    SUM_FONT_SIZE = "10"
    LABEL_PLUS = "+"

    # --- Key Constants ---
    PATH_TYPE_RF = "rf"
    PATH_TYPE_LATENT = "latent"

    def __init__(self, name: str):
        """
        Initializes the visualizer with a Graphviz Digraph.
        @param name The name of the resulting diagram.
        """
        self.dot = Digraph(name=name)
        self.dot.attr(rankdir='BT', nodesep='1.0', ranksep='0.8', splines='line', newrank=self.TRUE)
        self.dot.attr('node', fixedsize=self.TRUE, width=self.BLOCK_WIDTH_DEZIMAL, height=self.BLOCK_HEIGHT_DEZIMAL)

    # --- Helper Methods ---

    def _get_node_id(self, prefix: str, block) -> str:
        """
        Generates a consistent and unique identifier for a Graphviz node.
        The ID is constructed using a block-specific prefix, the fault or block name, 
        and the unique object memory address to prevent collisions.

        @param prefix The type-specific prefix (e.g., PREFIX_NODE_BE).
        @param block The block instance for which the ID is generated.
        @return A unique string identifier for the node.
        """
        base_name = block.fault_type.name if hasattr(block, 'fault_type') else block.name
        return f"{prefix}{base_name}_{id(block)}"

    def _get_lane_id(self, fault_name: str, path_type: str) -> str:
        """
        Generates a consistent group identifier for vertical alignment (Lanes).
        Nodes sharing the same group ID are forced into the same vertical column by Graphviz.

        @param fault_name The name of the fault type (e.g., "SBE").
        @param path_type The category of the path (PATH_TYPE_RF or PATH_TYPE_LATENT).
        @return A string identifier used for the 'group' attribute in Graphviz nodes.
        """
        return f"{self.PREFIX_LANE}{fault_name}_{path_type}"
    
    def _draw_junction(self, container, fault, branch_ports: list, original_port: str, 
                       color: str, path_type: str, block_id: int) -> str:
        """
        Helper method to manage the convergence of multiple fault paths.
        If more than one path exists (e.g., from multiple parallel sub-blocks or 
        a bypass), it creates a '+' summation node. If only one path exists, 
        it returns that path directly to avoid unnecessary visual clutter.

        @param container The Graphviz container (Digraph or Subgraph) to draw in.
        @param fault The fault type (Enum) being processed.
        @param branch_ports List of outgoing port IDs from the parallel sub-blocks.
        @param original_port The incoming port ID from before the summation block.
        @param color The color for the node and edges (COLOR_RF or COLOR_LATENT).
        @param path_type The type of the path (PATH_TYPE_RF or PATH_TYPE_LATENT).
        @param block_id Unique identifier of the parent Sum_Block for ID generation.
        @return The port ID of the junction output (or the single input path).
        """
        all_srcs = list(set(branch_ports))
        if original_port and original_port not in all_srcs:
            all_srcs.append(original_port)

        if len(all_srcs) > 1:
            j_id = f"{self.PREFIX_NODE_SUM}{fault.name}_{path_type}_{block_id}"
            group_id = self._get_lane_id(fault.name, path_type)
            
            container.node(
                j_id, label=self.LABEL_PLUS, shape=self.SUM_NODE_SHAPE, 
                width=self.SUM_NODE_SIZE, height=self.SUM_NODE_SIZE, 
                fixedsize=self.TRUE, color=color, fontcolor=color, 
                fontsize=self.SUM_FONT_SIZE, group=group_id
            )
            
            for src in all_srcs:
                self.dot.edge(src, f"{j_id}:{self.COMPASS_SOUTH}", color=color, minlen="2")
            
            return f"{j_id}:{self.COMPASS_NORTH}"
        
        elif len(all_srcs) == 1:
            return all_srcs[0]
        
        return None
    
    # --- Main Logic --- 

    def on_block_computed(self, block, input_ports: dict, spfm_in: dict, lfm_in: dict, 
                          spfm_out: dict, lfm_out: dict) -> dict:
        """
        Main entry point for the observer, triggered after a hardware block completes its 
        FIT rate transformation. This method identifies the block type and delegates the 
        drawing task to the specific internal visualization method.

        It ensures that the mathematical results (FIT rates) are correctly mapped to 
        visual elements and manages the propagation of Graphviz port IDs.

        @param block The instance of the logic block being processed (e.g., Sum_Block, Basic_Event).
        @param input_ports Mapping of fault types to incoming Graphviz node/port IDs.
        @param spfm_in Dictionary of incoming residual/SPFM FIT rates (before transformation).
        @param lfm_in Dictionary of incoming latent/LFM FIT rates (before transformation).
        @param spfm_out Updated dictionary of outgoing residual/SPFM FIT rates.
        @param lfm_out Updated dictionary of outgoing latent/LFM FIT rates.
        @return A dictionary containing the newly created output ports for the next block in the chain.
        """

        if isinstance(block, Basic_Event):
            return self._draw_basic_event(block, spfm_out, lfm_out)
        elif isinstance(block, Split_Block):
            return self._draw_split_block(block, input_ports, spfm_out, lfm_out)
        elif isinstance(block, Coverage_Block):
            return self._draw_coverage_block(block, input_ports, spfm_out, lfm_out)
        elif isinstance(block, Asil_Block):
            return self._draw_asil_block(block, input_ports, spfm_out, lfm_out)
        elif isinstance(block, Pipeline_Block):
            return self._draw_pipeline_block(block, input_ports, spfm_in, lfm_in)
        elif isinstance(block, Sum_Block):
            return self._draw_sum_block(block, input_ports, spfm_out, lfm_out)
        elif isinstance(block, Transformation_Block):
            return self._draw_transformation_block(block, input_ports, spfm_out, lfm_out)
        
        return input_ports

    def _draw_basic_event(self, block, spfm_out, lfm_out) -> dict:
        """
        Draws a circle for a FIT source (Basic Event).
        Enforces fixed sizing and strict lane alignment.

        @param block The Basic_Event instance.
        @param spfm_out Calculated output dictionary for residual rates.
        @param lfm_out Calculated output dictionary for latent rates.
        @return Mapping of fault types to the created node output port.
        """
        node_id = self._get_node_id(self.PREFIX_NODE_BE, block)
        
        fit_val = spfm_out.get(block.fault_type, 0.0) if block.is_spfm else lfm_out.get(block.fault_type, 0.0)
        label = f"{block.fault_type.name}\n{fit_val:.2f}"
        
        path_type = self.PATH_TYPE_RF if block.is_spfm else self.PATH_TYPE_LATENT
        group_id = self._get_lane_id(block.fault_type.name, path_type)
        color = self.COLOR_RF if block.is_spfm else self.COLOR_LATENT

        self.dot.node(
            node_id, 
            label=label, 
            shape=self.BASIC_EVENT_SHAPE, 
            width=self.BLOCK_WIDTH_DEZIMAL,           
            height=self.BLOCK_HEIGHT_DEZIMAL,          
            fixedsize=self.TRUE, 
            color=color,
            fontcolor=color,
            group=group_id,
            fontsize=self.FONT_SIZE_HEADER
        )

        port_n = f"{node_id}:{self.COMPASS_NORTH}"

        return {
            block.fault_type: {
                self.PATH_TYPE_RF: port_n if block.is_spfm else None,
                self.PATH_TYPE_LATENT: port_n if not block.is_spfm else None
            }
        }

    def _draw_split_block(self, block, input_ports, spfm_out, lfm_out) -> dict:
        """
        Draws a Split_Block as a fixed-size HTML table. The table displays the 
        distribution percentages in the top row and the block name in the header row.
        Incoming edges are connected to the southern port, and unique output ports 
        are generated for each target fault type.

        @param block The Split_Block instance containing distribution rates.
        @param input_ports Current mapping of fault types to node/port IDs.
        @param spfm_out Updated dictionary of outgoing residual FIT rates.
        @param lfm_out Updated dictionary of outgoing latent FIT rates.
        @return Updated dictionary of output ports for the next block in the chain.
        """
        node_id = self._get_node_id(self.PREFIX_NODE_SPLIT, block)
        
        num_targets = len(block.distribution_rates)
        cell_width = int(self.BLOCK_WIDTH_PIXEL) // num_targets
        
        cells_html = ""
        for target_fault, probability in block.distribution_rates.items():
            cells_html += (
                f'<TD PORT="p_{target_fault.name}" WIDTH="{cell_width}" HEIGHT="{self.DATA_HEIGHT}" BGCOLOR="{self.COLOR_BG}">'
                f'<FONT POINT-SIZE="{self.FONT_SIZE_DATA}">{probability*100:.1f}%</FONT></TD>'
            )

        label = f'''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" WIDTH="{self.BLOCK_WIDTH_PIXEL}" HEIGHT="{self.BLOCK_HEIGHT_PIXEL}" FIXEDSIZE="{self.TRUE}">
          <TR>{cells_html}</TR>
          <TR>
            <TD COLSPAN="{num_targets}" WIDTH="{self.BLOCK_WIDTH_PIXEL}" HEIGHT="{self.HEADER_HEIGHT}" BGCOLOR="{self.COLOR_HEADER}">
              <FONT POINT-SIZE="{self.FONT_SIZE_HEADER}"><B>Split: {block.fault_to_split.name}</B></FONT>
            </TD>
          </TR>
        </TABLE>>'''

        path_type = self.PATH_TYPE_RF if block.is_spfm else self.PATH_TYPE_LATENT
        group_id = self._get_lane_id(block.fault_to_split.name, path_type)

        self.dot.node(node_id, label=label, shape="none", group=group_id)

        prev_ports = input_ports.get(block.fault_to_split, {})
        source_port = prev_ports.get(path_type)
        edge_color = self.COLOR_RF if block.is_spfm else self.COLOR_LATENT
        
        if source_port:
            self.dot.edge(source_port, f"{node_id}:{self.COMPASS_SOUTH}", color=edge_color, minlen="2")

        new_ports = input_ports.copy()
        for target_fault in block.distribution_rates.keys():
            port_ref = f"{node_id}:p_{target_fault.name}:{self.COMPASS_NORTH}"
            
            prev_target_ports = input_ports.get(target_fault, {self.PATH_TYPE_RF: None, self.PATH_TYPE_LATENT: None})
            
            if block.is_spfm:
                new_ports[target_fault] = {
                    self.PATH_TYPE_RF: port_ref,
                    self.PATH_TYPE_LATENT: prev_target_ports[self.PATH_TYPE_LATENT]
                }
            else:
                new_ports[target_fault] = {
                    self.PATH_TYPE_RF: prev_target_ports[self.PATH_TYPE_RF],
                    self.PATH_TYPE_LATENT: port_ref
                }
        
        return new_ports

    def _draw_coverage_block(self, block, input_ports, spfm_out, lfm_out) -> dict:
        """
        Draws a Coverage_Block as a fixed-size HTML table. This block visually 
        represents the diagnostic coverage by splitting an incoming fault path 
        into a residual portion and a latent portion.
        
        The table shows the percentages for both paths in the top row and 
        the "Coverage" label in the header row.

        @param block The Coverage_Block instance.
        @param input_ports Current mapping of fault types to node/port IDs.
        @param spfm_out Updated dictionary of outgoing residual FIT rates.
        @param lfm_out Updated dictionary of outgoing latent FIT rates.
        @return Updated dictionary of output ports, now containing both rf and latent anchors.
        """
        node_id = self._get_node_id(self.PREFIX_NODE_COV, block)
        
        rf_percent = (1.0 - block.c_R) * 100
        lat_percent = (1.0 - block.c_L) * 100
        
        cell_width = int(self.BLOCK_WIDTH_PIXEL) // 2
        
        label = f'''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" WIDTH="{self.BLOCK_WIDTH_PIXEL}" HEIGHT="{self.BLOCK_HEIGHT_PIXEL}" FIXEDSIZE="{self.TRUE}">
          <TR>
            <TD PORT="rf" WIDTH="{cell_width}" HEIGHT="{self.DATA_HEIGHT}" BGCOLOR="{self.COLOR_BG}">
                <FONT POINT-SIZE="{self.FONT_SIZE_DATA}">{rf_percent:.1f}%</FONT>
            </TD>
            <TD PORT="latent" WIDTH="{cell_width}" HEIGHT="{self.DATA_HEIGHT}" BGCOLOR="{self.COLOR_BG}">
                <FONT POINT-SIZE="{self.FONT_SIZE_DATA}">{lat_percent:.1f}%</FONT>
            </TD>
          </TR>
          <TR>
            <TD COLSPAN="2" WIDTH="{self.BLOCK_WIDTH_PIXEL}" HEIGHT="{self.HEADER_HEIGHT}" BGCOLOR="{self.COLOR_HEADER}">
              <FONT POINT-SIZE="{self.FONT_SIZE_HEADER}"><B>Coverage</B></FONT>
            </TD>
          </TR>
        </TABLE>>'''

        path_type = self.PATH_TYPE_RF if block.is_spfm else self.PATH_TYPE_LATENT
        group_id = self._get_lane_id(block.target_fault.name, path_type)

        self.dot.node(node_id, label=label, shape="none", group=group_id)

        prev_ports = input_ports.get(block.target_fault, {})
        source_port = prev_ports.get(path_type)
        edge_color = self.COLOR_RF if block.is_spfm else self.COLOR_LATENT
        
        if source_port:
            self.dot.edge(source_port, f"{node_id}:{self.COMPASS_SOUTH}", color=edge_color, minlen="2")

        new_ports = input_ports.copy()
        
        port_rf = f"{node_id}:rf:{self.COMPASS_NORTH}"
        port_lat = f"{node_id}:latent:{self.COMPASS_NORTH}"
        
        if block.is_spfm:
            new_ports[block.target_fault] = {
                self.PATH_TYPE_RF: port_rf,
                self.PATH_TYPE_LATENT: port_lat
            }
        else:
            new_ports[block.target_fault] = {
                self.PATH_TYPE_RF: prev_ports.get(self.PATH_TYPE_RF),
                self.PATH_TYPE_LATENT: port_lat
            }
        
        return new_ports

    def _draw_asil_block(self, block, input_ports, spfm_out, lfm_out) -> dict:
        """
        Draws the final ASIL evaluation block at the end of the chain. 
        It aggregates all remaining fault paths into central summation nodes 
        and places the evaluation box at the very top (sink) of the graph.

        @param block The ASIL_Block instance.
        @param input_ports Current mapping of all active fault paths.
        @param spfm_out Final residual FIT rates for all faults.
        @param lfm_out Final latent FIT rates for all faults.
        @return An empty dictionary as this is the terminal node of the graph.
        """
        node_id = self._get_node_id(self.PREFIX_NODE_ASIL, block)
        
        all_rf_srcs = []
        all_lat_srcs = []
        for ports in input_ports.values():
            if ports.get(self.PATH_TYPE_RF):
                all_rf_srcs.append(ports[self.PATH_TYPE_RF])
            if ports.get(self.PATH_TYPE_LATENT):
                all_lat_srcs.append(ports[self.PATH_TYPE_LATENT])

        cluster_name = f"cluster_final_{id(block)}"
        with self.dot.subgraph(name=cluster_name) as c:
            c.attr(label="Final ASIL Evaluation", 
                   style=self.STYLE_DASHED, 
                   color=self.COLOR_HEADER, 
                   fontcolor=self.COLOR_TEXT_SECONDARY)
            
            final_rf_sum = self._draw_junction(
                c, type('Final', (), {'name': 'TOTAL'})(), all_rf_srcs, None, 
                self.COLOR_RF, self.PATH_TYPE_RF, id(block)
            )
            
            final_lat_sum = self._draw_junction(
                c, type('Final', (), {'name': 'TOTAL'})(), all_lat_srcs, None, 
                self.COLOR_LATENT, self.PATH_TYPE_LATENT, id(block)
            )

            with c.subgraph() as s:
                s.attr(rank='sink')
                s.node(
                    node_id, 
                    label="Calculate\nASIL Metrics", 
                    shape="rectangle",
                    width=self.BLOCK_WIDTH_DEZIMAL, 
                    height=self.BLOCK_HEIGHT_DEZIMAL,
                    style="filled", 
                    fillcolor=self.COLOR_BG,
                    penwidth="2"
                )

            if final_rf_sum:
                self.dot.edge(final_rf_sum, f"{node_id}:{self.COMPASS_SOUTH}", 
                              color=self.COLOR_RF, penwidth="2")
            if final_lat_sum:
                self.dot.edge(final_lat_sum, f"{node_id}:{self.COMPASS_SOUTH}", 
                              color=self.COLOR_LATENT, penwidth="2")

        return {}

    def _draw_pipeline_block(self, block, input_ports, spfm_in, lfm_in) -> dict:
        """
        Orchestrates the visualization of a sequential chain of blocks.
        It creates a dashed cluster to group the sequence and ensures that 
        the output ports of one block are correctly linked to the input of the next.

        @param block The Pipeline_Block instance.
        @param input_ports Initial incoming port IDs for the pipeline.
        @param spfm_in Initial residual FIT rates entering the pipeline.
        @param lfm_in Initial latent FIT rates entering the pipeline.
        @return The output ports of the final block in the sequence.
        """
        current_ports = input_ports
        current_spfm = spfm_in
        current_lfm = lfm_in

        cluster_name = f"{self.PREFIX_CLUSTER_PIPE}{id(block)}"
        with self.dot.subgraph(name=cluster_name) as c:
            c.attr(label=block.name, 
                   style=self.STYLE_DASHED, 
                   color=self.COLOR_HEADER, 
                   fontcolor=self.COLOR_TEXT_SECONDARY)

            for sub_block in block.blocks:
                next_spfm, next_lfm = sub_block.compute_fit(current_spfm, current_lfm)
                
                current_ports = self.on_block_computed(
                    sub_block, current_ports, 
                    current_spfm, current_lfm, 
                    next_spfm, next_lfm
                )
                
                current_spfm, current_lfm = next_spfm, next_lfm

        return current_ports

    def _draw_sum_block(self, block, input_ports, spfm_out, lfm_out) -> dict:
        """
        Draws a parallel aggregation block. It creates a dotted cluster to group
        sub-blocks, ensures children are aligned horizontally, and places '+' 
        summation nodes to join the fault paths.

        @param block The Sum_Block instance containing sub-blocks.
        @param input_ports Mapping of incoming node IDs.
        @param spfm_out Final residual rates after summation.
        @param lfm_out Final latent rates after summation.
        @return Mapping of fault types to the final summation node ports.
        """
        rf_collect = {}
        lat_collect = {}

        cluster_name = f"{self.PREFIX_CLUSTER_SUM}{id(block)}"
        with self.dot.subgraph(name=cluster_name) as c:
            c.attr(label=block.name,
                    style=self.STYLE_DOTTED,
                    color=self.COLOR_HEADER,
                    fontcolor=self.COLOR_TEXT_SECONDARY)
            
            with c.subgraph() as logic_rank:
                logic_rank.attr(rank=self.RANK_SAME)
                
                for sub_block in block.sub_blocks:
                    child_res = self.on_block_computed(
                        sub_block, input_ports, spfm_out, lfm_out, spfm_out, lfm_out
                    )
                    
                    for fault, ports in child_res.items():
                        if ports.get(self.PATH_TYPE_RF):
                            rf_collect.setdefault(fault, []).append(ports[self.PATH_TYPE_RF])
                        if ports.get(self.PATH_TYPE_LATENT):
                            lat_collect.setdefault(fault, []).append(ports[self.PATH_TYPE_LATENT])

            final_ports = {}
            all_faults = set(input_ports.keys()) | set(rf_collect.keys()) | set(lat_collect.keys())

            for fault in all_faults:
                final_ports[fault] = {self.PATH_TYPE_RF: None, self.PATH_TYPE_LATENT: None}
                
                final_ports[fault][self.PATH_TYPE_RF] = self._draw_junction(
                    c, fault, rf_collect.get(fault, []), 
                    input_ports.get(fault, {}).get(self.PATH_TYPE_RF), 
                    self.COLOR_RF, self.PATH_TYPE_RF, id(block)
                )

                final_ports[fault][self.PATH_TYPE_LATENT] = self._draw_junction(
                    c, fault, lat_collect.get(fault, []), 
                    input_ports.get(fault, {}).get(self.PATH_TYPE_LATENT), 
                    self.COLOR_LATENT, self.PATH_TYPE_LATENT, id(block)
                )

        return final_ports

    def _draw_transformation_block(self, block, input_ports, spfm_out, lfm_out) -> dict:
        """
        Draws a Transformation_Block as a fixed-size HTML table. This block represents 
        the transfer of a FIT rate portion from a source fault type to a target fault 
        type (e.g., SBE propagating to DBE).

        The table displays the transformation factor in the top row and the 
        "Transformation" label in the header row.

        @param block The Transformation_Block instance.
        @param input_ports Current mapping of fault types to node/port IDs.
        @param spfm_out Updated dictionary of outgoing residual FIT rates.
        @param lfm_out Updated dictionary of outgoing latent FIT rates.
        @return Updated dictionary of output ports for the target fault type.
        """
        node_id = f"{self.PREFIX_NODE_TRANS}{block.source.name}_to_{block.target.name}_{id(block)}"
        
        percent_label = f"{block.factor * 100:.1f}%"
        
        label = f'''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" WIDTH="{self.BLOCK_WIDTH_PIXEL}" HEIGHT="{self.BLOCK_HEIGHT_PIXEL}" FIXEDSIZE="{self.TRUE}">
          <TR>
            <TD PORT="out" WIDTH="{self.BLOCK_WIDTH_PIXEL}" HEIGHT="{self.DATA_HEIGHT}" BGCOLOR="{self.COLOR_BG}">
                <FONT POINT-SIZE="{self.FONT_SIZE_DATA}">{percent_label}</FONT>
            </TD>
          </TR>
          <TR>
            <TD WIDTH="{self.BLOCK_WIDTH_PIXEL}" HEIGHT="{self.HEADER_HEIGHT}" BGCOLOR="{self.COLOR_HEADER}">
              <FONT POINT-SIZE="{self.FONT_SIZE_HEADER}"><B>Transformation</B></FONT>
            </TD>
          </TR>
        </TABLE>>'''

        group_id = self._get_lane_id(block.source.name, self.PATH_TYPE_RF)

        self.dot.node(node_id, label=label, shape="none", group=group_id)

        source_ports = input_ports.get(block.source, {})
        source_node = source_ports.get(self.PATH_TYPE_RF)
        
        if source_node:
            self.dot.edge(source_node, f"{node_id}:{self.COMPASS_SOUTH}", color=self.COLOR_RF, minlen="2")

        new_ports = input_ports.copy()
        
        prev_target_ports = input_ports.get(block.target, {self.PATH_TYPE_RF: None, self.PATH_TYPE_LATENT: None})
        
        new_ports[block.target] = {
            self.PATH_TYPE_RF: f"{node_id}:out:{self.COMPASS_NORTH}",
            self.PATH_TYPE_LATENT: prev_target_ports[self.PATH_TYPE_LATENT]
        }
        
        return new_ports

    def render(self, filename: str):
        """
        Exports the current graph to a PDF file.
        @param filename The path/name for the exported file.
        """
        self.dot.render(filename, view=True)