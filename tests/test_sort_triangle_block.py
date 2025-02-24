import unittest
import os

from pager import TrianglesSortBlock, PhisicalModel
from pager.page_model.sub_models.dtype import ImageSegment, Block, Left2RightTop2BottomImageSegment

class TestSort(unittest.TestCase):
    sorter = TrianglesSortBlock()
    phis = PhisicalModel()
    data = [
        [{"x_top_left": 1, "x_bottom_right": 85, "y_top_left": 60, "y_bottom_right": 65, "label": "4"},
         {"x_top_left": 50, "x_bottom_right": 95, "y_top_left": 20, "y_bottom_right": 58, "label": "3"}, 
         {"x_top_left": 1, "x_bottom_right": 45, "y_top_left": 20, "y_bottom_right": 39, "label": "1"}, 
         {"x_top_left": 10, "x_bottom_right": 45, "y_top_left": 40, "y_bottom_right": 59, "label": "2"}, 
         {"x_top_left": 1, "x_bottom_right": 95, "y_top_left": 1, "y_bottom_right": 15, "label": "0"} ],
         # С такой сортировкой не может справиться:
        # [{"x_top_left": 21, "x_bottom_right": 49, "y_top_left": 11, "y_bottom_right": 29, "label": "4"},
        #  {"x_top_left": 1, "x_bottom_right": 49, "y_top_left": 1, "y_bottom_right": 9, "label": "0"},
        #  {"x_top_left": 21, "x_bottom_right": 29, "y_top_left": 31, "y_bottom_right": 39, "label": "5"},
        #  {"x_top_left": 1, "x_bottom_right": 9, "y_top_left": 21, "y_bottom_right": 39, "label": "2"},
        #  {"x_top_left": 1, "x_bottom_right": 19, "y_top_left": 11, "y_bottom_right": 19, "label": "1"},
        #  {"x_top_left": 11, "x_bottom_right": 19, "y_top_left": 21, "y_bottom_right": 39, "label": "3"},
        #  {"x_top_left": 31, "x_bottom_right": 39, "y_top_left": 31, "y_bottom_right": 39, "label": "6"},
        #  {"x_top_left": 41, "x_bottom_right": 49, "y_top_left": 31, "y_bottom_right": 39, "label": "7"}],
        [{"x_top_left": 1, "x_bottom_right": 59, "y_top_left": 1, "y_bottom_right": 9, "label": "0"},
         {"x_top_left": 1, "x_bottom_right": 39, "y_top_left": 11, "y_bottom_right": 19, "label": "1"},
         {"x_top_left": 41, "x_bottom_right": 59, "y_top_left": 11, "y_bottom_right": 39, "label": "4"},
         {"x_top_left": 41, "x_bottom_right": 59, "y_top_left": 41, "y_bottom_right": 49, "label": "5"},
         {"x_top_left": 1, "x_bottom_right": 19, "y_top_left": 21, "y_bottom_right": 49, "label": "2"},
         {"x_top_left": 21, "x_bottom_right": 39, "y_top_left": 21, "y_bottom_right": 49, "label": "3"}]
    ]

    def test_sort_read(self):
        for i, data_i in enumerate(self.data):
            self.phis.blocks = [Block(d) for d in data_i]
            self.sorter.extract(self.phis)
            sorted_text = [b.label for b in self.phis.blocks]
            self.assertEqual(sorted_text, [str(i) for i in range(len(data_i))], 
                             f"FAILED IN {i+1}")

    