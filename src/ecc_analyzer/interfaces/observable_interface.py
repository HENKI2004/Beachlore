#  @file Observable_Interface.py
#  @author Linus Held
#  @brief Defines the contract for observable components within the safety system.
#  @version 1.0
#  @date 2025-12-25
#
#   @copyright Copyright (c) 2025 Linus Held. All rights reserved.

from abc import ABC, abstractmethod

from .observer import SafetyObserver


class ObservableInterface(ABC):
    """
    Abstract interface for objects that need to be monitored by a SafetyObserver.
    It defines the mechanism for attaching observers and broadcasting calculation results.
    """

    @abstractmethod
    def attach(self, observer: SafetyObserver):
        """
        Registers a listener (observer) to receive notifications upon computation events.

        @param observer The SafetyObserver instance to be registered.
        """
        pass

    @abstractmethod
    def notify(
        self,
        input_ports: dict,
        spfm_in: dict,
        lfm_in: dict,
        spfm_out: dict,
        lfm_out: dict,
    ):
        """
        Broadcasts the computation results and visual context to all registered observers.

        @param input_ports Mapping of fault types to incoming node IDs for visualization.
        @param spfm_in Dictionary containing incoming residual/SPFM fault rates.
        @param lfm_in Dictionary containing incoming latent/LFM fault rates.
        @param spfm_out Dictionary containing the transformed outgoing SPFM fault rates.
        @param lfm_out Dictionary containing the transformed outgoing LFM fault rates.
        """
        pass
