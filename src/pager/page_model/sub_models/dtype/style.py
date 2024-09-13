from typing import Dict, Tuple

class Style:
    def __init__(self, dict_style):
        self.id = dict_style['id']
        self.size: float = 1.0
        self.font_type: str = None
        self.italic: bool = False
        self.width: float = 0.5
        self.color: Tuple[int] = (0, 0, 0)
        self.label: str = self.id
        
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

    def to_dict(self) -> Dict:
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
