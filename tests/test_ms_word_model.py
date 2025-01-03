import unittest
import numpy as np
import json
import os
from pager import MSWordModel
from pager.metrics.levenshtein_distance import levenshtein_distance

class TestMSWord(unittest.TestCase):
    msword_model_output  = MSWordModel()
    msword_model_input = MSWordModel()
    msword_model_output.read_from_file(os.path.join("files", "word.docx"))    

    def test_read_text(self) -> None:
        doc = self.msword_model_output.doc
        all_paras = doc.paragraphs
        self.assertEqual(all_paras[0].text, "Заголовок 1", all_paras[0])
        self.assertEqual(all_paras[1].text, "Подзаголовок", all_paras[1])
        self.assertEqual(all_paras[2].text, "Текст слово номер два.", all_paras[2])
        self.assertEqual(all_paras[3].text, "Список;", all_paras[3])
        self.assertEqual(all_paras[4].text, "лист.", all_paras[4])

    def test_read_style(self) -> None:
        doc = self.msword_model_output.doc
        all_paras = doc.paragraphs
        header1 = all_paras[0].style
        header2 = all_paras[1].style
        text = all_paras[2].style
        list_1 = all_paras[3].style
        list_2 = all_paras[4].style
        self.assertEqual(header1.name , "Heading 1", header1)
        self.assertEqual(header2.name, "Heading 2", header2)
        self.assertEqual(text.name, "Body Text", text)
        self.assertEqual(list_1.name, "Normal", list_1)
        self.assertEqual(list_1, list_2)

    def test_to_dict(self) -> None:
        res = self.msword_model_output.to_dict()
        self.assertIn("styles", res.keys(), res.keys())
        self.assertEqual(len(res["styles"]), 4, res.keys())
        self.assertIn("blocks", res.keys(), res.keys())
        self.assertEqual(len(res["blocks"]), 5, res.keys())

    def test_from_dict(self) -> None:
        self.msword_model_input.from_dict(self.msword_model_output.to_dict())
        path = os.path.join("files", "tmp_word.docx")
        if path in  os.listdir("files"):
            os.remove(path)
        self.msword_model_input.save_doc(path)
        self.assertIn("tmp_word.docx", os.listdir("files"))




    