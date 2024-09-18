from abc import ABC
from typing import List
# from ..paragraph import Paragraph
from .image_segment import ImageSegment
from .word import Word
# from ..extractors.block_extractors import BaseRandomWalkClassificator, BaseRandomDeepNodeClassificator

# CLASSIFICATOR = {
#     "walk_rnd": BaseRandomWalkClassificator,
#     "deep_rnd": BaseRandomDeepNodeClassificator,
# }

class Block(ABC):
    def __init__(self, dict_block):
       
        # self.paragraphs: List[Paragraph] = []
        self.words: List[Word] = []
        self.label = None
        if "label" in dict_block.keys():
            self.label = dict_block["label"]
        if "words" in dict_block.keys():
            self.words = [Word(word) for word in dict_block['words']]
        if  "width" in dict_block.keys() or "x_bottom_right" in dict_block.keys():
            self.segment = ImageSegment(dict_p_size = dict_block) if "width" in dict_block else ImageSegment(dict_2p = dict_block)
        elif len(self.words) > 0:
            self.segment = ImageSegment(0, 0, 1, 1)
            self.segment.set_segment_max_segments([w.segment for w in self.words])

    def extract_place_in_block_for_word_segments(self):
        block_h = self.segment.get_height()
        block_w = self.segment.get_width()
        block_dict = self.segment.get_segment_2p()
        x0, y0 = block_dict["x_top_left"],block_dict["y_top_left"] 
        for word in self.words:
            word_dict = word.segment.get_segment_2p()
            x1, y1 = word_dict["x_top_left"],word_dict["y_top_left"]
            word.segment.add_info("place_in_block",((x1-x0)/block_w, (y1-y0)/block_h))

    def extract_bold_for_word_segments(self):
        for word in self.words:
            word.segment.add_info("bold", [word.bold])

    # def classification(self, conf):
    #     classificator = CLASSIFICATOR[conf["type"]](conf["conf"])
    #     classificator.classification(self)


    def set_words_from_dict(self, list_words: List[dict]):
        self.words = []
        for dict_word in list_words:
            word = Word(dict_word)
            self.words.append(word)
    
    def set_label(self, text: str):
        self.label = text

    def get_text(self):
        str_ = ""
        for word in self.words:
            str_ += word.text + ' '
        return str_
    
    def to_dict(self):
        block_dict = self.segment.get_segment_2p()
        block_dict["text"] = self.get_text()
        if self.label is not None:
            block_dict["label"] = self.label
        block_dict["words"] = [word.to_dict() for word in self.words]
        return block_dict
    
class BlockWithoutWords(Exception):
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return "Count words in block is Zero"
