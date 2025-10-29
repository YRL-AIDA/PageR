from .word import Word
from .row import Row
from .block import Block
from .image_segment import ImageSegment
from .sortable_image_segment import Top2BottomLeft2RightImageSegment, Left2RightTop2BottomImageSegment
from .segment_relationship import Graph
from .style import Style
from .region import Region


import warnings
class StyleWord(Word):
   def __init__(self, dict_word):
       warnings.warn("use Word (StyleWord deleting)")
       super().__init__(dict_word)

class Block(Region):
   def __init__(self, dict_block):
       warnings.warn("use Region (Block deleting)")
       super().__init__(dict_block)
       
   