import unittest
import numpy as np
from pager import WordsAndStylesModel
import json 

class TestWordsAndStylesModel(unittest.TestCase):
    ws_model = WordsAndStylesModel()
    file_name = 'files/words_and_styles.json'   
    ws_model.read_from_file(file_name)
    dict_ = ws_model.to_dict()
    words = dict_['words']
    styles = dict_['styles']
    with open(file_name, 'r') as f:
        js = json.load(f)
    true_styles = js['styles']
    true_words = js['words']

    def test_len(self) -> None:
        self.assertEqual(len(self.words), len(self.true_words))
        self.assertEqual(len(self.styles), len(self.true_styles))

    def test_input_output(self) -> None:
        for true_dict, dict_ in zip(self.true_styles, self.styles):
            for key, val in true_dict.items():
                self.assertEqual(val, dict_[key])
        for true_dict, dict_ in zip(self.true_words, self.words):
            for key, val in true_dict.items():
                self.assertEqual(val, dict_[key])
