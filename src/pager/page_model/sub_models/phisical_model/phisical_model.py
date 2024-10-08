from ..base_sub_model import BaseSubModel, BaseExtractor, BaseConverter
from typing import Dict, List
from ..dtype import ImageSegment, Block, Word


class PhisicalModel(BaseSubModel):
    def __init__(self) -> None:
        super().__init__()
        self.blocks: List[Block] = []
    
    def from_dict(self, input_model_dict: Dict):
        pass

    def to_dict(self) -> Dict:
        return {"blocks": [block.to_dict() for block in self.blocks]}

    def read_from_file(self, path_file: str) -> None:
        self.clean_model()
        phis_json = self._read_json(path_file)
        for block_dict in phis_json["blocks"]:
            self.blocks.append(Block(block_dict))

    def clean_model(self):
        self.blocks = []
    

class WordsToOneBlock(BaseConverter):
    def convert(self, input_model: BaseSubModel, output_model: BaseSubModel)-> None:
        word_list: List[Word] = input_model.words
        segment = ImageSegment(0, 0, 1, 1)
        segment.set_segment_max_segments([word.segment for word in word_list])
        block = Block(segment.get_segment_2p())
        block.set_words_from_dict([word.to_dict() for word in word_list])
        output_model.blocks.append(block)
