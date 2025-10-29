import unittest
import numpy as np
from pager import RegionModel 
import json 
import os

class TestWordsAndStylesModel(unittest.TestCase):
    region_model = RegionModel()
    file_name = os.path.join('files','regions.json')
    region_model.read_from_file(file_name)
    dict_ = region_model.to_dict()
    region = dict_['regions']

    with open(file_name, 'r') as f:
        js = json.load(f)

    true_regions = js['regions']

    def test_len(self) -> None:
        self.assertEqual(len(self.region), len(self.true_regions))

    def test_input_output(self) -> None:
        for true_dict, dict_ in zip(self.true_regions, self.region):
            for key, val in true_dict.items():
                self.assertEqual(val, dict_[key])