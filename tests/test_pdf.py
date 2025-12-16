import unittest
import numpy as np
import json
from pager import PDFModel
from pager.metrics.levenshtein_distance import levenshtein_distance
from pager.doc_model import PrecisionPDFModel

class TestPDF(unittest.TestCase):
    pass
    # pdf_model=PDFModel()
    # precision_pdf = PrecisionPDFModel({"method": "w", "page_model": None})

    # with open("files/text_header_table_jar_words.json", 'r', encoding='utf-8') as f:
    #     true_dict_words = json.load(f) 
    
    # with open("files/text_header_table_jar_rows.json", 'r', encoding='utf-8') as f:
    #     true_dict_rows = json.load(f) 

    # def test_page_0_and_end(self) -> None:
    #     self.pdf_model.clean_model()

    #     self.precision_pdf.read_from_file("files/text_header_table.pdf", method='w')
    #     page0 = self.pdf_model.to_dict()
    #     while not self.pdf_model.is_final_page():
    #         self.pdf_model.next_page()
    #     page1 = self.pdf_model.to_dict()
    #     self.assertEqual(page1, page0, f"{page0} \n != \n {page1}")

    # def test_count_page(self) -> None:
    #     self.pdf_model.clean_model()
    #     self.pdf_model.read_from_file("files/text_header_table.pdf", method='w')
    #     self.assertEqual(self.pdf_model.count_page, len(self.true_dict_words['pages']))

    # def test_text(self) -> None:
    #     self.pdf_model.clean_model()
    #     self.pdf_model.read_from_file("files/text_header_table.pdf", method='w')
    #     page0 = self.pdf_model.to_dict()
    #     text = "" 
    #     with open('files/text_header_table_text.txt', 'r', encoding='utf-8') as f:
    #         for line in f:
    #             text += " " + line[:-1] # delete \n
    #     text_ = ""
    #     for word in page0['words']:  
    #         text_ += " " +  word['text']
    #     ld = levenshtein_distance(text, text_)/len(text)
    #     self.assertLessEqual(ld, 0.01)


    # def test_rows(self) -> None:
    #     self.pdf_model.clean_model()
    #     self.pdf_model.read_from_file("files/text_header_table.pdf", method='r')
    #     page0 = self.pdf_model.to_dict()
    #     text = "" 
    #     with open('files/text_header_table_text.txt', 'r', encoding='utf-8') as f:
    #         for line in f:
    #             text += " " + line[:-1] # delete \n
    #     text_ = ""
    #     for row in page0['blocks']:  
    #         text_ += " " +  row['text'][:-1] # delete \n
    #     ld = levenshtein_distance(text, text_)/len(text)
    #     self.assertLessEqual(ld, 0.01)
        