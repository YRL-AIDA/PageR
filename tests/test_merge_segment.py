import unittest
from pager.page_model.sub_models.utils import merge_segment
from pager.page_model.sub_models.dtype import ImageSegment

class TestMergeSegment(unittest.TestCase):
    def test_merge_segment(self):
        segs = [ImageSegment(0, 0, 2, 3), #0
                ImageSegment(3, 0, 4, 1), #0
                ImageSegment(1, 7, 8, 8), #1
                ImageSegment(5, 0, 9, 3), #0
                ImageSegment(1, 2, 6, 6), #0
                ImageSegment(7, 3, 9, 6), #0
                ImageSegment(4, 3, 5, 4), #0
                ImageSegment(10, 10, 11, 11), #2
               ]
        
        list_ind = merge_segment(segs)
        true_list = [0, 0, 1, 0, 0, 0, 0, 2]
        self.assertEqual(list_ind, true_list, (list_ind, true_list))