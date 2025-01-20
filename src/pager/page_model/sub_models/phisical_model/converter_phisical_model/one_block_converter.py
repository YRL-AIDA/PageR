from ...base_sub_model import BaseSubModel, BaseConverter
from ...dtype import ImageSegment, Block, Word
from typing import List

class WordsToOneBlock(BaseConverter):
    def convert(self, input_model: BaseSubModel, output_model: BaseSubModel)-> None:
        word_list: List[Word] = input_model.words
        segment = ImageSegment(0, 0, 1, 1)
        segment.set_segment_max_segments([word.segment for word in word_list])
        block = Block(segment.get_segment_2p())
        block.set_words_from_dict([word.to_dict() for word in word_list])
        output_model.blocks.append(block)