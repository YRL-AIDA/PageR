import unittest
import numpy as np
import json
from pager import PDFModel
from pager.metrics.levenshtein_distance import levenshtein_distance

class TestPDF(unittest.TestCase):
    pdf_model=PDFModel()
    pdf_model.read_from_file("files/text_header_table.pdf")    

    with open("files/text_header_table_jar.json", 'r', encoding='utf-8') as f:
        true_dict = json.load(f) 

    def test_page_0_and_end(self) -> None:
        page0 = self.pdf_model.to_dict()
        while not self.pdf_model.is_final_page():
            self.pdf_model.next_page()
        page1 = self.pdf_model.to_dict()
        self.assertEqual(page1, page0, f"{page0} \n != \n {page1}")

    def test_count_page(self) -> None:
        self.assertEqual(self.pdf_model.count_page, len(self.true_dict['pages']))

    def test_text(self) -> None:
        page0 = self.pdf_model.to_dict()
        text = "" 
        with open('files/text_header_table_text.txt', 'r', encoding='utf-8') as f:
            for line in f:
                text += " " + line[:-1] # delete \n
        text_ = ""
        for word in page0['words']:  
            text_ += " " +  word['text']
        ld = levenshtein_distance(text, text_)/len(text)
        self.assertLessEqual(ld, 0.01)
