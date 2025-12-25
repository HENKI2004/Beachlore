from enum import Enum, auto

class FAULTS(Enum):
    """
    Enumeration of supported fault types within the safety model.
    Each member represents a specific failure mode used for FIT rate calculations and visualization.
    """
    SBE = auto()
    DBE = auto()
    TBE = auto()
    MBE = auto()
    WD = auto()
    AZ = auto()
    SB = auto()
    SDB = auto() 
    OTH = auto() 
    SBE_IF = auto()