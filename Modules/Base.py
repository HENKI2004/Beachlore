from abc import ABC, abstractmethod
from .Block_Interface import Block_Interface

class Base(ABC):
    """
    Abstract base class representing a high-level hardware component.
    It manages the initial fault inputs and the root block that defines the component's logic.
    """

    def __init__(self, name: str, spfm_input: dict, lfm_input: dict):
        """
        Initializes the component and triggers the block configuration.
        
        @param name The name of the hardware component.
        @param spfm_input Initial dictionary of SPFM/dangerous fault rates.
        @param lfm_input Initial dictionary of LFM/latent fault rates.
        """
        self.name = name
        self.spfm_input = spfm_input.copy()
        self.lfm_input = lfm_input.copy()
        self.root_block: Block_Interface = None
        
        self.configure_blocks()

    @abstractmethod
    def configure_blocks(self):
        """
        Abstract method used to define the internal block structure of the component.
        Subclasses must assign a Pipeline_Block or Sum_Block to self.root_block.
        """
        pass

    def compute_fit(self) -> dict:
        """
        Starts the FIT rate calculation by passing the initial inputs to the root block.
        
        @return A dictionary containing the final 'SPFM' and 'LFM' results.
        """
        if self.root_block is None:
            return {'SPFM': self.spfm_input, 'LFM': self.lfm_input}

        final_spfm, final_lfm = self.root_block.compute_fit(self.spfm_input, self.lfm_input)

        return {
            'SPFM': final_spfm,
            'LFM': final_lfm
        }