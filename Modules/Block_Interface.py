from abc import ABC, abstractmethod

class Block_Interface(ABC):
    """
    Abstract interface defining the mandatory structure for all logic blocks.
    Every block in the system must implement this interface to ensure modularity and nesting.
    """

    @abstractmethod
    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        """
        Transforms the input fault rate dictionaries according to the block's specific logic.

        @param spfm_rates Dictionary containing current SPFM/residual fault rates.
        @param lfm_rates Dictionary containing current LFM/latent fault rates.
        @return A tuple of updated (spfm_rates, lfm_rates) dictionaries.
        """
        pass

    @abstractmethod
    def to_dot(self, dot, input_ports: dict) -> dict:
        """
        Generates Graphviz visualization ports for the block.

        @param dot The Graphviz Digraph object to draw on.
        @param input_ports Mapping of fault types to their incoming node IDs.
        @return An updated dictionary containing the outgoing ports of this block.
        """
        pass