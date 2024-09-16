import unittest
import numpy as np
import json
from pager import PDFModel
from pager.metrics.levenshtein_distance import levenshtein_distance

class TestPDF(unittest.TestCase):
    pdf_model=PDFModel()
    pdf_model.read_from_file("files/text_header_table.pdf")    

    with open("files/text_header_table_jar.json") as f:
        true_dict = json.load(f) 

    def test_page_0(self) -> None:
        page0 = self.pdf_model.to_dict()
        tdk = self.true_dict['pages'][0]
        self.assertEqual(tdk, page0, f"{tdk} \n != \n {page0}")
    
    def test_page_end(self) -> None:
        while not self.pdf_model.is_final_page():
            self.pdf_model.next_page()
        page1 = self.pdf_model.to_dict()
        tdk = self.true_dict['pages'][-1]
        self.assertEqual(tdk, page1, f"{tdk} \n != \n {page1}")
    

    def test_count_page(self) -> None:
        self.assertEqual(self.pdf_model.count_page, len(self.true_dict['pages']))

    def test_text(self) -> None:
        page0 = self.pdf_model.to_dict()
        text = "" 
        with open('files/text_header_table_text.txt') as f:
            for line in f:
                text += " " + line[:-1] # delete \n
        text_ = ""
        for word in page0['words']:  
            text_ += " " +  word['text']
        ld = levenshtein_distance(text, text_)/len(text)
        self.assertLessEqual(ld, 0.01)
