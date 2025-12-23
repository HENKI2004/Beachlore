# Modules/Base.py
from abc import ABC, abstractmethod
from .Block_Interface import Block_Interface

class Base(Block_Interface, ABC):
    def __init__(self, name: str):
        self.name = name
        self.root_block: Block_Interface = None
        self.configure_blocks()

    @abstractmethod
    def configure_blocks(self):
        pass

    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        """Ermöglicht es, die Komponente in einer Pipeline zu nutzen."""
        if self.root_block is None:
            return spfm_rates.copy(), lfm_rates.copy()
        return self.root_block.compute_fit(spfm_rates, lfm_rates)