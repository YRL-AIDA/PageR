from abc import ABC
from typing import List
import numpy as np
import matplotlib .pyplot as plt
# from ..paragraph import Paragraph
from .image_segment import ImageSegment
from .row import Row

class Region(ABC):
    def __init__(self, dict_region):
        # print('set regions from dict', dict_region)
        # self.paragraphs: List[Paragraph] = []
        self.rows: List[Row] = []
        self.label = None


        if "label" in dict_region.keys():
            self.set_label(dict_region["label"])
        if "rows" in dict_region.keys():
            self.set_rows_from_dict(dict_region['rows'])
        if  "width" in dict_region.keys() or "x_bottom_right" in dict_region.keys():
            self.set_segment(dict_region)
        elif "segment" in dict_region.keys():
            self.set_segment(dict_region["segment"])
        elif len(self.rows) > 0:
            segment = ImageSegment(0, 0, 1, 1)
            segment.set_segment_max_segments([r.segment for r in self.rows])
            self.set_segment(segment.get_segment_2p())
    
    def set_label(self, label:str):
        self.label = label

    def set_rows_from_dict(self, list_rows: List[dict]):
        self.rows = [Row(row) for row in list_rows]
        index = np.argsort([row.segment.y_top_left for row in self.rows])
        self.rows = [self.rows[i] for i in index]
    
    def set_segment(self, dict_region):
        self.segment = ImageSegment(dict_p_size = dict_region) if "width" in dict_region else ImageSegment(dict_2p = dict_region)

    @property
    def text(self):
        if len(self.rows) > 0:
            return " ".join([row.content for row in self.rows])
        else:
            return ""
    
    @property
    def words(self):
        words = []
        for row in self.rows:
            words.extend(row.get_words())
        return words

    def to_dict(self):
        block_dict ={
            "segment": self.segment.get_segment_2p(),
            "text": self.text,
            "rows": [row.to_dict() for row in self.rows]
        }
        if self.label is not None:
            block_dict["label"] = self.label
        
        return block_dict
    
