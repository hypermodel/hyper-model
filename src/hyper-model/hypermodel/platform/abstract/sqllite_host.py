import pandas as pd
from abc import ABC, abstractmethod
from typing import List


class SQLLiteBase(ABC):# extends Abstract Base class

    @abstractmethod
    def create_merge_request(self,
                             reference: dict,
                             reference_path: str,
                             description: str = "Something awesome about the Model",
                             target_branch: str = "master",
                             labels: List[str] = ['model-bot']
                             ):
        pass
