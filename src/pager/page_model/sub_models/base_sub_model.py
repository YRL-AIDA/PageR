from abc import ABC, abstractmethod
from typing import Dict


class BaseSubModel(ABC):
    @abstractmethod
    def from_dict(self, input_model_dict: Dict):
        pass

    @abstractmethod
    def to_dict(self) -> Dict:
        pass
    
    @abstractmethod
    def read_from_file(self, path_file: str) -> None:
        pass

class BaseConverter(ABC):
    @abstractmethod
    def convert(self, input_model: BaseSubModel, output_model: BaseSubModel)-> None:
        pass


class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, model: BaseSubModel) -> None:
        pass

class BasePrinter(ABC):
    pass

class BaseLoger(ABC):
    pass


    