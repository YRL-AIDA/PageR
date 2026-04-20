from .image_segment import ImageSegment
from typing import Dict, List
from .word import Word
import numpy as np
from .font import Font
class Row:
    def __init__(self, dict_row):
        self.segment:ImageSegment 
        self.words: List[Word] = []
        #=========== style =========================
        self.style_id:int|None = dict_row["style_id"] if "style_id" in dict_row else None
        

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
        elif "content" in dict_row:
            self.set_text(dict_row["content"])
        elif len(self.words) > 0:
            self.set_text_from_words(self.words)

        self.font = None
        if "font" in dict_row:
            self.set_font(dict_row['font'])
        elif len(self.words) > 0:
            self.set_font_from_words(self.words)

    @property
    def content(self) -> str:
        return self.text

    def set_text(self, text: str):
        self.text = text
    
    def set_text_from_words(self, words: list[Word]):
        self.text = " ".join([word.text for word in words])
            
    def set_font_from_words(self, words: list[Word]):
        fonts = [word.font.to_dict() for word in words]
        self.font = Font({
            'name': fonts[0]['name'],
            'width': float(np.mean([f['width'] for f in fonts])),
            'italic': float(np.mean([f['italic'] for f in fonts])),
            'size': float(np.max([f['size'] for f in fonts]))
        })


    def set_words(self, words: list[Dict]):
        self.words = [Word(w_json) for w_json in words]
        index = np.argsort([word.segment.x_top_left for word in self.words])
        self.words = [self.words[i] for i in index]

    def set_segment(self, dict_row: Dict):
        seg = dict_row["segment"] if "segment" in dict_row else dict_row
        self.segment = ImageSegment(dict_p_size = seg) if "width" in seg else ImageSegment(dict_2p = seg)

    def set_font(self, dict_font: Dict):
        self.font = Font(dict_font)
    
    def to_dict(self) -> Dict:
        dict_row = dict()
        if self.style_id:
            dict_row["style_id"] = self.style_id
        dict_row = {
            "font": self.font.to_dict() if self.font is not None else None ,
            "words": [w.to_dict() for w in self.words]
        } 
        dict_row["text"] = self.text
        dict_row["segment"]= self.segment.get_segment_2p()
        return dict_row
    
    def get_words(self) -> list[Word]:
        if len(self.words) == 0:
            raise NoWordsInfoException()
        else:
            return self.words
    
    def __repr__(self):
        
        return f"<rows text: '{self.text}', segment: {self.segment.__repr__()} (words: {len(self.words)})>"

class NoWordsInfoException(Exception):
    def  __str__(self):
        return "No words info found in the rows"