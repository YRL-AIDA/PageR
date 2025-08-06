from abc import ABC
from typing import List
import numpy as np
import matplotlib .pyplot as plt
# from ..paragraph import Paragraph
from .image_segment import ImageSegment
from .word import Word
from .row import Row
from .sortable_image_segment import Top2BottomLeft2RightImageSegment
# from ..extractors.block_extractors import BaseRandomWalkClassificator, BaseRandomDeepNodeClassificator

# CLASSIFICATOR = {
#     "walk_rnd": BaseRandomWalkClassificator,
#     "deep_rnd": BaseRandomDeepNodeClassificator,
# }

class Block(ABC):
    def __init__(self, dict_block):
       
        # self.paragraphs: List[Paragraph] = []
        self.words: List[Word] = []
        self.rows: List[Row] = []
        
        self.label = None
        if "label" in dict_block.keys():
            self.label = dict_block["label"]
        if "words" in dict_block.keys():
            self.words = [Word(word) for word in dict_block['words']]
        if "rows" in dict_block.keys():
            self.rows = [Row(row) for row in dict_block['rows']]
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

    def set_rows_from_dict(self, list_rows: List[dict]):
        self.rows = []
        for dict_row in list_rows:
            row = Row(dict_row)
            self.rows.append(row)

    def sort_words(self):
        self._sort_segments([w.segment for w in self.words], self.words)

    def _sort_segments(self, segs, elements):
        bboxes = [Top2BottomLeft2RightImageSegment.converter(seg) for seg in segs]
        #TODO: change sort
        for i in range(len(bboxes)):
            for j in range(len(bboxes)):
                if bboxes[i] < bboxes[j]:
                    bboxes[i], bboxes[j] = bboxes[j], bboxes[i]
                    elements[i], elements[j] = elements[j], elements[i]
    

    def set_label(self, text: str):
        self.label = text

    def get_text(self):
        self.sort_words()
        str_ = ""
        if len(self.words) != 0:
            for word in self.words:
                str_ += word.text + ' '
        elif len(self.rows) != 0:
            for row in self.rows:
                str_ += row.text + ' '
        return str_
    
    def to_dict(self):
        block_dict = self.segment.get_segment_2p()
        block_dict["text"] = self.get_text()
        if self.label is not None:
            block_dict["label"] = self.label
        block_dict["words"] = [word.to_dict() for word in self.words]
        block_dict["rows"] = [row.to_dict() for row in self.rows]
        return block_dict
    
class BlockWithoutWords(Exception):
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return "Count words in block is Zero"


class TableBlock(Block):
    def __init__(self, dict_block, img_table, dict_grid, dict_cells):
        super().__init__(dict_block)
        self.img_table = img_table
        self.grid = dict_grid
        self.cells = dict_cells
    
    def to_dict(self):
        block_dict = self.segment.get_segment_2p()
        block_dict["text"] = self.get_text()
        if self.label is not None:
            block_dict["label"] = self.label
        block_dict["words"] = [word.to_dict() for word in self.words]
        block_dict["cells"] = self.cells
        block_dict["grid"] = self.grid
        return block_dict
    
    def show(self):
        seg = self.segment.get_segment_2p()
        x0 = seg['x_top_left']
        x1 = seg['x_bottom_right']
        y0 = seg['y_top_left']
        y1 = seg['y_bottom_right']
        for c in self.grid['columns']:
            plt.plot([x0+c, x0+c], [y0, y1])
        for r in self.grid['rows']:
            plt.plot([x0, x1], [y0+r, y0+r])