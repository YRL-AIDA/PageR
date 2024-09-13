from .image_segment import ImageSegment
from typing import Dict

class StyleWord:
    def __init__(self, dict_word):
        self.content: str  = dict_word['content'] 
        self.style_id: int = dict_word['style_id']
        self.y: int = dict_word['y']
        self.x: int = dict_word['x']
        self.type_align: str = dict_word['type_align']

    def to_dict(self) -> Dict:
        dict_word = {
            "content": self.content,
            "style_id": self.style_id,
            "y": self.y,
            "x": self.x,
            "type_align": self.type_align
        }
        return dict_word
