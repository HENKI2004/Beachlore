"""File to define a model via an external config file"""

from pathlib import Path

from .system_base import SystemBase


class GenericSafetySystem(SystemBase):
    """A system that defines its hardware structure via an external config file."""

    def __init__(self, name: str, total_fit: float, config_path: str):
        """Initializes a new safety system from an external configuration file.

        Args:
            name (str): The descriptive name of the hardware system.
            total_fit (float): The total failure rate (FIT) of the system used
                to calculate relative metrics.
            config_path (str): The path to the JSON or YAML file containing
                the system's hardware block layout.
        """
        self.config_path = config_path
        super().__init__(name, total_fit)

    def configure_system(self):
        """Reconstructs the layout from the provided configuration file.

        Determines the file format (JSON or YAML) based on the extension of
        the config_path and executes the corresponding loading logic.

        Raises:
            ValueError: If the file extension is not supported.
        """
        extension = Path(self.config_path).suffix.lower()

        if extension == ".json":
            self.load_from_json(self.config_path)
        elif extension in [".yaml", ".yml"]:
            self.load_from_yaml(self.config_path)
        else:
            raise ValueError(f"Unsupported file format: '{extension}'. Please provide a .json, .yaml, or .yml file.")
