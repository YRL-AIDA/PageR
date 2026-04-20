from ..base_doc_model import BaseDocModel
from abc import ABC, abstractmethod


class BaseConverter(ABC):
    @abstractmethod
    def convert(self, input_model:BaseDocModel, output_model:BaseDocModel):
        pass