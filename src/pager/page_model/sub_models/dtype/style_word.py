from .image_segment import ImageSegment
from typing import Dict


class StyleWord:
    def __init__(self, dict_word):
        self.content: str  = dict_word['content'] 
        self.style_id: int = dict_word['style_id']
        seg = dict_word['segment']
        if "width" in seg.keys():
            self.segment = ImageSegment(dict_p_size=seg)
        else:
            self.segment = ImageSegment(dict_2p=seg)
        self.type_align: str = dict_word['type_align']

    def to_dict(self) -> Dict:
        dict_word = {
            "content": self.content,
            "style_id": self.style_id,
            "segment": self.segment.get_segment_2p(),
            "type_align": self.type_align
        }
        return dict_word
