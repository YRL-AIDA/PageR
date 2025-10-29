from .image_segment import ImageSegment
from typing import Dict
from .word import Word
import numpy as np

class Row:
    def __init__(self, dict_row):
        self.segment:ImageSegment 
        self.text: str = ""
        #=========== style =========================
        self.style_id:int|None = dict_row["style_id"] if "style_id" in dict_row else None
        self.bold: float|None = None
        self.italic: float|None = None # Наклон 0 - нет, 1 - как линия.
        self.font_name: str|None = None
        self.size: int|None = None
        self.words: list[Word] = []

        if "words" in dict_row.keys():
            self.set_words(dict_row["words"])
        
        if  "width" in dict_row.keys() or "x_bottom_right" in dict_row.keys():
            self.set_segment(dict_row)
        elif "segment" in dict_row.keys():
            self.set_segment(dict_row["segment"])
        elif len(self.words) > 0:
            segment = ImageSegment(0, 0, 1, 1)
            segment.set_segment_max_segments([w.segment for w in self.words])
            self.set_segment(segment.get_segment_2p())
        
        if "text" in dict_row:
            self.set_text(dict_row["text"])
        if "content" in dict_row:
            self.set_text(dict_row["content"])
        self.set_style(dict_row)

    @property
    def content(self) -> str:
        return self.text

    def set_text(self, text: str):
        self.text = text
    
    def set_words(self, words: list[Dict]):
        self.words = [Word(w_json) for w_json in words]
        index = np.argsort([word.segment.x_top_left for word in self.words])
        self.words = [self.words[i] for i in index]

    def set_segment(self, dict_row: Dict):
        seg = dict_row["segment"] if "segment" in dict_row else dict_row
        self.segment = ImageSegment(dict_p_size = seg) if "width" in seg else ImageSegment(dict_2p = seg)

    def set_style(self, dict_row: Dict):
        if "bold" in dict_row:
            bold = dict_row["bold"]
            if type(bold) == bool:
                self.bold = 1.0 if bold else 0.0
            elif type(bold) in (float, int):
                self.bold = bold  
        
        if "italic" in dict_row:
            italic = dict_row["italic"]
            if type(italic) == bool:
                self.italic = 0.45 if italic else 0
            elif type(italic) in (float, int):
                self.italic = italic  
        if "size" in dict_row:
            self.size = dict_row["size"]
        elif "font_size" in dict_row:
            self.size = dict_row["font_size"]
        else:
            self.size = self.segment.height
        if "font_type" in dict_row:
            self.font_name = dict_row["font_type"]
        elif "font_name" in dict_row:
            self.font_name = dict_row["font_name"]
    
    def to_dict(self) -> Dict:
        dict_row = {
            "bold": self.bold,
            "italic": self.italic,
            "font_name": self.font_name,
            "size": self.size
        } if self.style_id is None else {
            "style_id": self.style_id
        }
        dict_row["text"] = self.text
        dict_row["segment"]= self.segment.get_segment_2p()
        return dict_row