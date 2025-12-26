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
    ASIL_Block, Pipeline_Block, Sum_Block, Transformation_Block,
    Base
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
    COLOR_COMP_BG = "gray96"
    COLOR_COMP_BORDER = "gray80"
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
    PREFIX_CLUSTER_COMP = "cluster_comp_"
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
        self.dot.attr(rankdir='BT', nodesep='1.0', ranksep='0.8', splines='spline', newrank=self.TRUE) # line, spline, polyline, ortho, curved,  try this compound ??  
        self.dot.attr('node', fixedsize=self.TRUE, width=self.BLOCK_WIDTH_DEZIMAL, height=self.BLOCK_HEIGHT_DEZIMAL)
        self.dot.attr('edge', arrowhead='none')

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
        base_name = getattr(block, 'name', None) or getattr(block, 'fault_type', getattr(block, 'target_fault', getattr(block, 'fault_to_split', None))).name
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
        # 1. Sammle alle verarbeiteten Ergebnisse (z.B. von Split/Coverage)
        all_srcs = list(set(branch_ports))
        
        # 2. ENTSCHEIDUNG: Nur durchleiten, wenn NICHTS verarbeitet wurde.
        # Wenn die Liste 'all_srcs' leer ist (kein Block hat diesen Fehler angefasst),
        # dann und NUR DANN nutzen wir den originalen Eingang.
        if len(all_srcs) == 0 and original_port:
            all_srcs.append(original_port)

        # 3. Zeichnen (Logik wie gehabt)
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
                container.edge(src, f"{j_id}:{self.COMPASS_SOUTH}", color=color, minlen="2")
            
            return f"{j_id}:{self.COMPASS_NORTH}"
        
        elif len(all_srcs) == 1:
            # Nur ein Signal (entweder Ergebnis ODER Durchleitung) -> Direkt zurückgeben
            return all_srcs[0]
        
        return None
    
    # --- Main Logic --- 

    def on_block_computed(self, block, input_ports: dict, spfm_in: dict, lfm_in: dict, 
                          spfm_out: dict, lfm_out: dict, container = None,predecessors=None) -> dict:
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
        if container is None:
            container = self.dot

        if isinstance(block, Basic_Event):
            return self._draw_basic_event(block, spfm_out, lfm_out,container,predecessors)
        elif isinstance(block, Split_Block):
            return self._draw_split_block(block, input_ports, spfm_out, lfm_out,container)
        elif isinstance(block, Coverage_Block):
            return self._draw_coverage_block(block, input_ports, spfm_out, lfm_out,container)
        elif isinstance(block, ASIL_Block):
            return self._draw_asil_block(block, input_ports, spfm_out, lfm_out,container)
        elif isinstance(block, Pipeline_Block):
            return self._draw_pipeline_block(block, input_ports, spfm_in, lfm_in,container)
        elif isinstance(block, Sum_Block):
            return self._draw_sum_block(block, input_ports, spfm_out, lfm_out,container,predecessors)
        elif isinstance(block, Transformation_Block):
            return self._draw_transformation_block(block, input_ports, spfm_out, lfm_out,container)
        elif isinstance(block, Base):
            cluster_name = f"{self.PREFIX_CLUSTER_COMP}{id(block)}"
            with container.subgraph(name=cluster_name) as c:
                # Graue Box zeichnen
                full_label = f"{block.__class__.__name__}: {block.name}"
                c.attr(label=full_label, style='filled', color=self.COLOR_COMP_BORDER, bgcolor=self.COLOR_COMP_BG)
                
                # --- A. EINGANGS-PORTS ERSTELLEN (Unten) ---
                internal_inputs = {} 
                local_anchors = [] 
                
                with c.subgraph() as in_rank:
                    in_rank.attr(rank='same')
                    
                    for fault, paths in input_ports.items():
                        internal_inputs[fault] = {self.PATH_TYPE_RF: None, self.PATH_TYPE_LATENT: None}
                        
                        # --- Input für Residual Path (Rot) ---
                        if paths.get(self.PATH_TYPE_RF):
                            in_id = f"in_{id(block)}_{fault.name}_rf"
                            
                            # FIT-Wert holen
                            val = spfm_in.get(fault, 0.0)
                            label_text = f"In {fault.name}\n{val:.2f}"
                            
                            in_rank.node(in_id, label=label_text, shape="rect", height="0.2", 
                                         style="filled", fillcolor="white", fontsize="7", fixedsize="false",
                                         group=self._get_lane_id(fault.name, self.PATH_TYPE_RF))
                            
                            container.edge(paths[self.PATH_TYPE_RF], f"{in_id}:{self.COMPASS_SOUTH}", color=self.COLOR_RF)
                            internal_inputs[fault][self.PATH_TYPE_RF] = f"{in_id}:{self.COMPASS_NORTH}"
                            local_anchors.append(f"{in_id}:{self.COMPASS_NORTH}")

                        # --- Input für Latent Path (Blau) ---
                        if paths.get(self.PATH_TYPE_LATENT):
                            in_id_lat = f"in_{id(block)}_{fault.name}_lat"
                            
                            # FIT-Wert holen
                            val = lfm_in.get(fault, 0.0)
                            label_text = f"In {fault.name}\n{val:.2f}"
                            
                            in_rank.node(in_id_lat, label=label_text, shape="rect", height="0.2", 
                                         style="filled", fillcolor="white", fontsize="7", fixedsize="false",
                                         group=self._get_lane_id(fault.name, self.PATH_TYPE_LATENT))
                            
                            container.edge(paths[self.PATH_TYPE_LATENT], f"{in_id_lat}:{self.COMPASS_SOUTH}", color=self.COLOR_LATENT)
                            internal_inputs[fault][self.PATH_TYPE_LATENT] = f"{in_id_lat}:{self.COMPASS_NORTH}"
                            local_anchors.append(f"{in_id_lat}:{self.COMPASS_NORTH}")

                # --- B. INTERNE LOGIK BERECHNEN ---
                active_inputs = internal_inputs if internal_inputs else input_ports
                
                if local_anchors:
                    active_predecessors = local_anchors
                else:
                    active_predecessors = predecessors

                internal_results = self.on_block_computed(
                    block.root_block, active_inputs, spfm_in, lfm_in, spfm_out, lfm_out, 
                    container=c, predecessors=active_predecessors
                )

                # --- C. AUSGANGS-PORTS ERSTELLEN (Oben) ---
                final_outputs = {}
                
                with c.subgraph() as out_rank:
                    out_rank.attr(rank='same')
                    
                    for fault, paths in internal_results.items():
                        final_outputs[fault] = {self.PATH_TYPE_RF: None, self.PATH_TYPE_LATENT: None}
                        
                        # --- Output für Residual Path (Rot) ---
                        if paths.get(self.PATH_TYPE_RF):
                            out_id = f"out_{id(block)}_{fault.name}_rf"
                            
                            # FIT-Wert holen (vom Endergebnis spfm_out)
                            val = spfm_out.get(fault, 0.0)
                            label_text = f"Out {fault.name}\n{val:.2f}"
                            
                            out_rank.node(out_id, label=label_text, shape="rect", height="0.2", 
                                          style="filled", fillcolor="white", fontsize="7", fixedsize="false",
                                          group=self._get_lane_id(fault.name, self.PATH_TYPE_RF))
                            
                            c.edge(paths[self.PATH_TYPE_RF], f"{out_id}:{self.COMPASS_SOUTH}", color=self.COLOR_RF)
                            final_outputs[fault][self.PATH_TYPE_RF] = f"{out_id}:{self.COMPASS_NORTH}"

                        # --- Output für Latent Path (Blau) ---
                        if paths.get(self.PATH_TYPE_LATENT):
                            out_id_lat = f"out_{id(block)}_{fault.name}_lat"
                            
                            # FIT-Wert holen (vom Endergebnis lfm_out)
                            val = lfm_out.get(fault, 0.0)
                            label_text = f"Out {fault.name}\n{val:.2f}"
                            
                            out_rank.node(out_id_lat, label=label_text, shape="rect", height="0.2", 
                                          style="filled", fillcolor="white", fontsize="7", fixedsize="false",
                                          group=self._get_lane_id(fault.name, self.PATH_TYPE_LATENT))
                            
                            c.edge(paths[self.PATH_TYPE_LATENT], f"{out_id_lat}:{self.COMPASS_SOUTH}", color=self.COLOR_LATENT)
                            final_outputs[fault][self.PATH_TYPE_LATENT] = f"{out_id_lat}:{self.COMPASS_NORTH}"

                return final_outputs
        
        return input_ports

    def _draw_basic_event(self, block, spfm_out, lfm_out,container,predecessors= None) -> dict:
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
        label = f"{block.fault_type.name}\n{block.lambda_BE:.2f}"
        
        path_type = self.PATH_TYPE_RF if block.is_spfm else self.PATH_TYPE_LATENT
        group_id = self._get_lane_id(block.fault_type.name, path_type)
        color = self.COLOR_RF if block.is_spfm else self.COLOR_LATENT

        container.node(
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

        if predecessors: # maybe all predecssors
            container.edge(predecessors[0], f"{node_id}:{self.COMPASS_SOUTH}", style='invis')

        port_n = f"{node_id}:{self.COMPASS_NORTH}"

        return {
            block.fault_type: {
                self.PATH_TYPE_RF: port_n if block.is_spfm else None,
                self.PATH_TYPE_LATENT: port_n if not block.is_spfm else None
            }
        }

    def _draw_split_block(self, block, input_ports, spfm_out, lfm_out,container) -> dict:
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
        
        width_total = int(self.BLOCK_WIDTH_PIXEL)
        cell_width = width_total // num_targets
        
        cells = [
            f'<TD PORT="p_{tf.name}" WIDTH="{cell_width}" HEIGHT="{self.DATA_HEIGHT}" BGCOLOR="{self.COLOR_BG}">'
            f'<FONT POINT-SIZE="{self.FONT_SIZE_DATA}">{p*100:.1f}%</FONT></TD>'
            for tf, p in block.distribution_rates.items()
        ]
        
        label = f'''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" WIDTH="{width_total}" HEIGHT="{self.BLOCK_HEIGHT_PIXEL}" FIXEDSIZE="TRUE">
          <TR>{"".join(cells)}</TR>
          <TR>
            <TD COLSPAN="{num_targets}" WIDTH="{width_total}" HEIGHT="{self.HEADER_HEIGHT}" BGCOLOR="{self.COLOR_HEADER}"><B> Split {block.fault_to_split.name}</B></TD>
          </TR>
        </TABLE>>'''

        path_type = self.PATH_TYPE_RF if block.is_spfm else self.PATH_TYPE_LATENT
        group_id = self._get_lane_id(block.fault_to_split.name, path_type)

        container.node(node_id, label=label, shape="none", group=group_id)

        prev_ports = input_ports.get(block.fault_to_split, {})
        source_port = prev_ports.get(path_type)
        edge_color = self.COLOR_RF if block.is_spfm else self.COLOR_LATENT
        
        if source_port:
            container.edge(source_port, f"{node_id}:{self.COMPASS_SOUTH}", color=edge_color, minlen="2")

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

    def _draw_coverage_block(self, block, input_ports, spfm_out, lfm_out,container) -> dict:
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
        
        width_total = int(self.BLOCK_WIDTH_PIXEL)
        cell_width = width_total // 2
        
        label = f'''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" WIDTH="{width_total}" HEIGHT="{self.BLOCK_HEIGHT_PIXEL}" FIXEDSIZE="TRUE">
        <TR>
            <TD PORT="rf" WIDTH="{cell_width}" HEIGHT="{self.DATA_HEIGHT}" BGCOLOR="{self.COLOR_BG}"><FONT POINT-SIZE="{self.FONT_SIZE_DATA}">{rf_percent:.1f}%</FONT></TD>
            <TD PORT="latent" WIDTH="{cell_width}" HEIGHT="{self.DATA_HEIGHT}" BGCOLOR="{self.COLOR_BG}"><FONT POINT-SIZE="{self.FONT_SIZE_DATA}">{lat_percent:.1f}%</FONT></TD>
        </TR>
        <TR>
            <TD COLSPAN="2" WIDTH="{width_total}" HEIGHT="{self.HEADER_HEIGHT}" BGCOLOR="{self.COLOR_HEADER}"><B>Coverage</B></TD>
        </TR>
        </TABLE>>'''

        path_type = self.PATH_TYPE_RF if block.is_spfm else self.PATH_TYPE_LATENT
        group_id = self._get_lane_id(block.target_fault.name, path_type)

        container.node(node_id, label=label, shape="none", group=group_id)

        prev_ports = input_ports.get(block.target_fault, {})
        source_port = prev_ports.get(path_type)
        edge_color = self.COLOR_RF if block.is_spfm else self.COLOR_LATENT
        
        if source_port:
            container.edge(source_port, f"{node_id}:{self.COMPASS_SOUTH}", color=edge_color, minlen="2")

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

    def _draw_asil_block(self, block, input_ports, spfm_out, lfm_out,container) -> dict:
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
        with container.subgraph(name=cluster_name) as c:
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
                container.edge(final_rf_sum, f"{node_id}:{self.COMPASS_SOUTH}", 
                              color=self.COLOR_RF, penwidth="2")
            if final_lat_sum:
                container.edge(final_lat_sum, f"{node_id}:{self.COMPASS_SOUTH}", 
                              color=self.COLOR_LATENT, penwidth="2")

        return {}

    def _draw_pipeline_block(self, block, input_ports, spfm_in, lfm_in,container) -> dict:
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
        with container.subgraph(name=cluster_name) as c:
            c.attr(label=block.name, 
                   style=self.STYLE_DASHED, 
                   color=self.COLOR_HEADER, 
                   fontcolor=self.COLOR_TEXT_SECONDARY)

            for sub_block in block.blocks:

                anchors = []
                for p_dict in current_ports.values():
                    if p_dict.get(self.PATH_TYPE_RF): anchors.append(p_dict[self.PATH_TYPE_RF])
                    if p_dict.get(self.PATH_TYPE_LATENT): anchors.append(p_dict[self.PATH_TYPE_LATENT])

                next_spfm, next_lfm = sub_block.compute_fit(current_spfm, current_lfm)
                
                current_ports = self.on_block_computed(
                    sub_block, current_ports, 
                    current_spfm, current_lfm, 
                    next_spfm, next_lfm,
                    container = c,
                    predecessors=anchors
                )
                
                current_spfm, current_lfm = next_spfm, next_lfm

        return current_ports

    def _draw_sum_block(self, block, input_ports, spfm_out, lfm_out,container,predecessors= None) -> dict:
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
        
        # Sets um zu merken, welche Fehler "angefasst" (verarbeitet) wurden
        processed_rf = set()      # <--- NEU
        processed_lat = set()     # <--- NEU

        cluster_name = f"{self.PREFIX_CLUSTER_SUM}{id(block)}"
        with container.subgraph(name=cluster_name) as c:
            c.attr(label=block.name,
                   style=self.STYLE_DOTTED,
                   color=self.COLOR_HEADER,
                   fontcolor=self.COLOR_TEXT_SECONDARY)
            
            with c.subgraph() as logic_rank:
                # rank=same bleibt aus, damit Layout flexibel ist
                
                for sub_block in block.sub_blocks:
                    child_res = self.on_block_computed(
                        sub_block, input_ports, spfm_out, lfm_out, spfm_out, lfm_out, logic_rank, predecessors=predecessors
                    )
                    
                    # Prüfen, ob der Block ein "Verarbeiter" ist (der den Input modifiziert/ersetzt)
                    # Basic_Event ist KEIN Verarbeiter in diesem Sinne, da es additiv wirkt.
                    is_processing_block = isinstance(sub_block, (Coverage_Block, Split_Block, Transformation_Block, Pipeline_Block))

                    for fault, ports in child_res.items():
                        original_rf = input_ports.get(fault, {}).get(self.PATH_TYPE_RF)
                        original_lat = input_ports.get(fault, {}).get(self.PATH_TYPE_LATENT)
                        
                        is_source_block = isinstance(sub_block, Basic_Event) and sub_block.fault_type == fault

                        # --- RF PFAD ---
                        if ports.get(self.PATH_TYPE_RF):
                            # Wenn der Port anders ist als der Eingang, wurde er verändert oder neu erzeugt
                            has_changed = (ports[self.PATH_TYPE_RF] != original_rf)
                            
                            # Logik: Sammeln wenn es eine aktive Quelle ist ODER sich etwas geändert hat
                            if (is_source_block and sub_block.is_spfm) or has_changed:
                                rf_collect.setdefault(fault, []).append(ports[self.PATH_TYPE_RF])
                                
                                # Wenn es ein Verarbeiter war, merken wir uns das!
                                if is_processing_block and has_changed:   # <--- NEU
                                    processed_rf.add(fault)

                        # --- LATENT PFAD ---
                        if ports.get(self.PATH_TYPE_LATENT):
                            has_changed = (ports[self.PATH_TYPE_LATENT] != original_lat)
                            
                            if (is_source_block and not sub_block.is_spfm) or has_changed:
                                lat_collect.setdefault(fault, []).append(ports[self.PATH_TYPE_LATENT])
                                
                                if is_processing_block and has_changed:   # <--- NEU
                                    processed_lat.add(fault)

            final_ports = {}
            all_faults = set(input_ports.keys()) | set(rf_collect.keys()) | set(lat_collect.keys())

            for fault in all_faults:
                final_ports[fault] = {self.PATH_TYPE_RF: None, self.PATH_TYPE_LATENT: None}
                
                # --- LOGIK FÜR RF JUNCTION ---
                sources_rf = rf_collect.get(fault, [])
                orig_rf = input_ports.get(fault, {}).get(self.PATH_TYPE_RF)
                
                # SPEZIALFALL: Wenn der Fehler NICHT verarbeitet wurde (kein Coverage/Split),
                # aber wir Quellen haben (z.B. Basic Event) ODER gar nichts haben (Pass-Through),
                # dann müssen wir den Original-Eingang dazunehmen!
                if fault not in processed_rf and orig_rf:     # <--- KORREKTUR HIER
                    if orig_rf not in sources_rf:
                        sources_rf.append(orig_rf)

                final_ports[fault][self.PATH_TYPE_RF] = self._draw_junction(
                    c, fault, sources_rf, None,  # Original Port hier None, da wir es oben schon behandelt haben
                    self.COLOR_RF, self.PATH_TYPE_RF, id(block)
                )

                # --- LOGIK FÜR LATENT JUNCTION ---
                sources_lat = lat_collect.get(fault, [])
                orig_lat = input_ports.get(fault, {}).get(self.PATH_TYPE_LATENT)
                
                if fault not in processed_lat and orig_lat:   # <--- KORREKTUR HIER
                    if orig_lat not in sources_lat:
                        sources_lat.append(orig_lat)

                final_ports[fault][self.PATH_TYPE_LATENT] = self._draw_junction(
                    c, fault, sources_lat, None,
                    self.COLOR_LATENT, self.PATH_TYPE_LATENT, id(block)
                )

        return final_ports

    def _draw_transformation_block(self, block, input_ports, spfm_out, lfm_out,container) -> dict:
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
        
        # 1. Integer-Breite erzwingen (wie beim Coverage-Block)
        width_total = int(self.BLOCK_WIDTH_PIXEL)
        
        # 2. Label exakt nach Coverage-Vorlage
        # - FIXEDSIZE="TRUE"
        # - Kein <FONT> im Header
        # - Text gekürzt auf "Transf.", da "Transformation" > 72px breit ist!
        label = f'''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" WIDTH="{width_total}" HEIGHT="{self.BLOCK_HEIGHT_PIXEL}" FIXEDSIZE="TRUE">
        <TR>
            <TD PORT="out" WIDTH="{width_total}" HEIGHT="{self.DATA_HEIGHT}" BGCOLOR="{self.COLOR_BG}"><FONT POINT-SIZE="{self.FONT_SIZE_DATA}">{percent_label}</FONT></TD>
        </TR>
        <TR>
            <TD WIDTH="{width_total}" HEIGHT="{self.HEADER_HEIGHT}" BGCOLOR="{self.COLOR_HEADER}"><B>Transf.</B></TD>
        </TR>
        </TABLE>>'''

        group_id = self._get_lane_id(block.source.name, self.PATH_TYPE_RF)

        container.node(node_id, label=label, shape="none", group=group_id)

        source_ports = input_ports.get(block.source, {})
        source_node = source_ports.get(self.PATH_TYPE_RF)
        
        if source_node:
            container.edge(source_node, f"{node_id}:{self.COMPASS_SOUTH}", color=self.COLOR_RF, minlen="2")

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