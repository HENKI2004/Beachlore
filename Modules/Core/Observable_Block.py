#  @file Observable_Block.py
#  @author Linus Held 
#  @brief Implements the wrapper for logic blocks with output port management.
#  @version 1.1
#  @date 2025-12-25
# 
#   @copyright Copyright (c) 2025 Linus Held. All rights reserved.

from ..Interfaces import Block_Interface, Observable_Interface, SafetyObserver

class Observable_Block(Observable_Interface):
    """
    A wrapper class that encapsulates a logic block and manages 
    both mathematical results and visual output ports. 
    """

    def __init__(self, logic_block: Block_Interface):
        """
        Initializes the observable wrapper. 
        @param logic_block The pure mathematical block to be wrapped. 
        """
        self.block = logic_block
        self._observers = []

    def attach(self, observer: SafetyObserver):
        """
        Registers an observer. 
        @param observer The SafetyObserver instance. 
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def run(self, spfm_in: dict, lfm_in: dict, input_ports: dict):
        """
        Executes calculation and collects output ports from the observer. 

        @param spfm_in Incoming SPFM fault rates. 
        @param lfm_in Incoming LFM fault rates. 
        @param input_ports Mapping of incoming node IDs. 
        @return A tuple of (spfm_out, lfm_out, output_ports).
        """ 
        spfm_out, lfm_out = self.block.compute_fit(spfm_in, lfm_in)

        output_ports = self.notify(input_ports, spfm_in, lfm_in, spfm_out, lfm_out)

        return spfm_out, lfm_out, output_ports

    def notify(self, input_ports: dict, spfm_in: dict, lfm_in: dict, spfm_out: dict, lfm_out: dict):
        """
        Broadcasts results and returns the visual ports created by the observer. 
        """
        last_created_ports = {}
        for observer in self._observers:
            ports = observer.on_block_computed(
                self.block, input_ports, spfm_in, lfm_in, spfm_out, lfm_out
            )
            if ports:
                last_created_ports = ports
        
        return last_created_ports