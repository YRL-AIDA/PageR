from typing import Dict, Tuple, List
import numpy as np

class Style:
    def __init__(self, dict_style):
        self.id = dict_style['id']
        self.size: float = 1.0
        self.font_type: str = None
        self.italic: bool = False
        self.width: float = 0.5
        self.color: Tuple[int] = (0, 0, 0)
        self.label: str = self.id
        self.font2vec: List[float] = None
        keys_style = dict_style.keys()
        for key in ["size", 'font_type', 'italic', 'width', 'color', 'label']:
            fun = eval("self.set_"+key)
            if key in keys_style:
                fun(dict_style[key])

    def set_size(self, size: float):
        self.size = size

    def set_font_type(self, font_type: str):
        self.font_type = font_type
    
    def set_italic(self, italic: bool):
        self.italic = italic

    def set_width(self, width: float):
        self.width = width

    def set_color(self, RGB:Tuple[int]):
        self.color = tuple(RGB)

    def set_label(self, label: str):
        self.label = label
    
    def set_font2vec(self, font2vec):
        if isinstance(font2vec, np.dtype):
            font2vec = font2vec.tolist()
        self.font2vec = font2vec
    
    def extract_vec(self):
        self.font2vec = [
            self.width,
            1.0 if self.italic else 0.0,
            self.color[0],
            self.color[1],
            self.color[2],
            self.size
        ]        

    def to_dict(self, is_vec=False) -> Dict:
        if is_vec:
            return {"font2vec": self.font2vec}

        self.extract_vec()
        dict_style = {
            "id": self.id,
            "size": self.size,
            "font_type": self.font_type,
            "italic": self.italic,
            "width": self.width,
            "color": list(self.color),
            "label": self.label
        }
        return dict_style
