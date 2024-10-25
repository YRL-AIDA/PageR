from .image_segment import ImageSegment
from typing import Dict

class Word:
    def __init__(self, dict_word):
        self.segment = ImageSegment(dict_p_size = dict_word) if "width" in dict_word else ImageSegment(dict_2p = dict_word)
        
        self.text = ""
        if "text" in dict_word.keys():
            self.set_text(dict_word["text"])
        
        self.bold = None
        if "bold" in dict_word.keys():
            self.set_bold(dict_word["bold"])

    def set_text(self, text: str):
        self.text = text

    def set_bold(self, bold: float):
        self.bold = bold
    
    def to_dict(self) -> Dict:
        any_date = {
            "text": self.text
        }
        if self.bold is not None:
            any_date["bold"] = round(self.bold, 4) 
        segment = self.segment.get_segment_2p()
        dict_word = dict(list(segment.items()) + list(any_date.items()))
        return dict_word
