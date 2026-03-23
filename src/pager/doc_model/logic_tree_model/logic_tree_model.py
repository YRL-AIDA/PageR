from ..base_doc_model import BaseDocModel
from typing import Dict, List
from ..dtype import Document
from pager.page_model.sub_models.dtype import Region


class LogicTreeModel(BaseDocModel):
    def __init__(self, conf=None):
        self.document: Document
        self.regions: List[Region]
        self.edges: Dict

    def to_dict(self) -> Dict:
        return {
            "nodes": {
                "document": {
                },
                "regions": {id_reg: reg.to_dict()
                    for id_reg, reg  in enumerate(self.regions)
                }
            },
            "edges": self.edges
        }
