from typing import List, Set, Dict, Tuple, Optional


class PackageData:
    """
    A simple class to model a Column in a Table within a DataWarehouse or DataMart
    """

    artifacts: Dict[str, str]
    name: str

    def __init__(self):
        self.artifacts = dict()
        self.name = None
