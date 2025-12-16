from .image_segment import ImageSegment
from typing import Dict

class Word:
    def __init__(self, dict_word):
        self.segment:ImageSegment 
        self.text: str = ""
        #=========== style =========================
        self.style_id:int|None = dict_word["style_id"] if "style_id" in dict_word else None
        self.bold: float|None = None
        self.italic: float|None = None # Наклон 0 - нет, 1 - как линия.
        self.font_name: str|None = None
        self.size: int|None = None


        if  "width" in dict_word.keys() or "x_bottom_right" in dict_word.keys():
            self.set_segment(dict_word)
        elif "segment" in dict_word.keys():
            self.set_segment(dict_word["segment"])
        if "text" in dict_word:
            self.set_text(dict_word["text"])
        if "content" in dict_word:
            self.set_text(dict_word["content"])
        self.set_style(dict_word)

    @property
    def content(self) -> str:
        return self.text

    def set_text(self, text: str):
        self.text = text
    
    def set_segment(self, dict_word: Dict):
        seg = dict_word["segment"] if "segment" in dict_word else dict_word
        self.segment = ImageSegment(dict_p_size = seg) if "width" in seg else ImageSegment(dict_2p = seg)

    def set_style(self, dict_word: Dict):
        if "bold" in dict_word:
            bold = dict_word["bold"]
            if type(bold) == bool:
                self.bold = 1.0 if bold else 0.0
            elif type(bold) in (float, int):
                self.bold = bold  
        
        if "italic" in dict_word:
            italic = dict_word["italic"]
            if type(italic) == bool:
                self.italic = 0.45 if italic else 0
            elif type(italic) in (float, int):
                self.italic = italic  
        if "size" in dict_word:
            self.size = dict_word["size"]
        elif "font_size" in dict_word:
            self.size = dict_word["font_size"]
        else:
            self.size = self.segment.height
        if "font_type" in dict_word:
            self.font_name = dict_word["font_type"]
        elif "font_name" in dict_word:
            self.font_name = dict_word["font_name"]
    
    def to_dict(self) -> Dict:
        dict_word = {
            "bold": self.bold,
            "italic": self.italic,
            "font_name": self.font_name,
            "size": self.size
        } if self.style_id is None else {
            "style_id": self.style_id
        }
        dict_word["text"] = self.text
        dict_word["segment"]= self.segment.get_segment_2p()
        return dict_word
    
