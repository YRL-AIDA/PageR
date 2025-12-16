import unittest
import numpy as np
from pager import RegionModel 
import json 
import os

class TestWordsAndStylesModel(unittest.TestCase):
    # TODO: заменить only_text_regions.json на более качественный файл.
    region_model = RegionModel()

    file_name = os.path.join('files','regions.json')
    region_model.read_from_file(file_name)
    dict_rows = region_model.to_dict()
    region_with_rows = region_model.regions.copy()
    dict_region_with_rows = dict_rows['regions']

    file_name = os.path.join('files','only_text_regions.json')
    region_model.read_from_file(file_name)
    dict_words = region_model.to_dict()
    region_with_words = region_model.regions.copy()
    dict_region_with_words = dict_words['regions']
 
    def test_count_regions(self) -> None:
       self.assertEqual(len(self.region_with_rows), 2)
       self.assertEqual(len(self.dict_region_with_rows), 2)
       self.assertEqual(len(self.region_with_words), 8)
       self.assertEqual(len(self.dict_region_with_words), 8)


    def test_exist_rows_in_regions(self) -> None:
        for region in self.region_with_rows:
            self.assertGreater(len(region.rows), 0)
        for region in self.region_with_words:
            self.assertGreater(len(region.rows), 0)
    
    def test_exist_words_in_regions(self) -> None:
        for i, region in enumerate(self.region_model.regions):
            self.assertGreater(len(region.words), 0)

    # def test_label_model(self) -> None:
    #     true_label = ['header', 'header', 'text', 'text', 'header', 'text', 'text', 'table']
    #     for i, block in enumerate(self.dict_regions):
    #         self.assertEqual(block["label"], true_label[i])

    # def test_start_end_words(self) -> None:
    #     word_start = self.dict_regions[3]["words"][0] 
    #     for key, val in word_start["segment"].items():
    #         word_start[key] = val
    #     word_end = self.dict_regions[3]["words"][-1]
    #     for key, val in word_end["segment"].items():
    #         word_end[key] = val
    #     true_word_start = {
    #             'x_top_left': 46,
    #             'x_bottom_right': 110,
    #             'y_top_left': 234,
    #             'y_bottom_right': 245,
    #             'text': 'Учитывая'}
    #     true_word_end = {
    #             'x_top_left': 215,
    #             'x_bottom_right': 300,
    #             'y_top_left': 377,
    #             'y_bottom_right': 391,
    #             'text': 'разоблачены.'}
    #     for key, val in true_word_start.items():
    #         self.assertEqual(word_start[key], val)
    #     for key, val in true_word_end.items():
    #         self.assertEqual(word_end[key], val)