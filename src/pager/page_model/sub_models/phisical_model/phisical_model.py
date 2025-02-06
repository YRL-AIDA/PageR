from ..base_sub_model import BaseSubModel
from typing import Dict, List
from ..dtype import Block


class PhisicalModel(BaseSubModel):
    def __init__(self) -> None:
        super().__init__()
        self.blocks: List[Block] = []
    
    def from_dict(self, input_model_dict: Dict):
        for block_dict in input_model_dict["blocks"]:
            self.blocks.append(Block(block_dict))

    def to_dict(self) -> Dict:
        return {"blocks": [block.to_dict() for block in self.blocks]}

    def read_from_file(self, path_file: str) -> None:
        phis_json = self._read_json(path_file)
        for block_dict in phis_json["blocks"]:
            self.blocks.append(Block(block_dict))

    def clean_model(self):
        self.blocks = []
            
