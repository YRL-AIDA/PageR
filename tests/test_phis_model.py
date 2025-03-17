import unittest
import numpy as np
from pager import PhisicalModel

class TestPhisicalModel(unittest.TestCase):
    phis_model=PhisicalModel()
    phis_model.read_from_file('files/blocks.json')
    dict_ = phis_model.to_dict()
    blocks = dict_['blocks']
 
    def test_len_blocks(self) -> None:
       self.assertEqual(len(self.blocks), 8)
    

    def test_count_words(self) -> None:
        true_len = [2, 2, 36, 72, 2, 68, 23, 20]
        for i, block in enumerate(self.blocks):
            self.assertEqual(len(block["words"]), true_len[i])

    def test_label_model(self) -> None:
        true_label = ['header', 'header', 'text', 'text', 'header', 'text', 'text', 'table']
        for i, block in enumerate(self.blocks):
            self.assertEqual(block["label"], true_label[i])

    def test_start_end_words(self) -> None:
        word_start = self.blocks[3]["words"][0] 
        for key, val in word_start["segment"].items():
            word_start[key] = val
        word_end = self.blocks[3]["words"][-1]
        for key, val in word_end["segment"].items():
            word_end[key] = val
        true_word_start = {
                'x_top_left': 46,
                'x_bottom_right': 110,
                'y_top_left': 234,
                'y_bottom_right': 245,
                'text': 'Учитывая'}
        true_word_end = {
                'x_top_left': 215,
                'x_bottom_right': 300,
                'y_top_left': 377,
                'y_bottom_right': 391,
                'text': 'разоблачены.'}
        for key, val in true_word_start.items():
            self.assertEqual(word_start[key], val)
        for key, val in true_word_end.items():
            self.assertEqual(word_end[key], val)
        
