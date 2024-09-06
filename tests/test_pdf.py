import unittest
import numpy as np
import json
from pager import PDFModel


class TestPDF(unittest.TestCase):
    pdf_model=PDFModel()
    with open("files/text_header_table_jar.json") as f:
        true_dict = json.load(f) 

    def test_(self) -> None:
        self.pdf_model.read_from_file("files/text_header_table.pdf")
        
        model_dict = self.pdf_model.to_dict()
        for key in self.true_dict.keys():        
            tdk = self.true_dict[key]
            mdk = model_dict[key]
            self.assertEqual(tdk, mdk, f"{tdk} \n != \n {mdk}")



