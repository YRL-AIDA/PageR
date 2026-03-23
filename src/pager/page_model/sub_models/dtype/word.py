from .image_segment import ImageSegment
from typing import Dict
from .font import Font


class Word:
    def __init__(self, dict_word):
        self.segment:ImageSegment 
        self.text: str = ""
        #=========== style =========================
        self.style_id:int|None = dict_word["style_id"] if "style_id" in dict_word else None
        

        if  "width" in dict_word.keys() or "x_bottom_right" in dict_word.keys():
            self.set_segment(dict_word)
        elif "segment" in dict_word.keys():
            self.set_segment(dict_word["segment"])
        if "text" in dict_word:
            self.set_text(dict_word["text"])
        if "content" in dict_word:
            self.set_text(dict_word["content"])

        self.font = None
        if "font" in dict_word:
            self.set_font(dict_word["font"])

    @property
    def content(self) -> str:
        return self.text

    def set_text(self, text: str):
        self.text = text
    
    def set_segment(self, dict_word: Dict):
        seg = dict_word["segment"] if "segment" in dict_word else dict_word
        self.segment = ImageSegment(dict_p_size = seg) if "width" in seg else ImageSegment(dict_2p = seg)

    def set_font(self, dict_font: Dict):
        self.font = Font(dict_font)

    def to_dict(self) -> Dict:
        dict_word = {
            "style_id": self.style_id
        }
        dict_word["font"] = self.font.to_dict()
        dict_word["text"] = self.text
        dict_word["segment"]= self.segment.get_segment_2p()
        return dict_word
    
