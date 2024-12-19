import unittest
import numpy as np
import json
import os
from pager import MSWordModel
from pager.metrics.levenshtein_distance import levenshtein_distance

class TestMSWord(unittest.TestCase):
    msword_model  = MSWordModel()
    msword_model.read_from_file(os.path.join("files", "word.docx"))    

    def test_read_text(self) -> None:
        doc = self.msword_model.doc
        all_paras = doc.paragraphs
        self.assertEqual(all_paras[0].text, "Заголовок 1", all_paras[0])
        self.assertEqual(all_paras[1].text, "Подзаголовок", all_paras[1])
        self.assertEqual(all_paras[2].text, "Текст слово номер два.", all_paras[2])
        self.assertEqual(all_paras[3].text, "Список;", all_paras[3])
        self.assertEqual(all_paras[4].text, "лист.", all_paras[4])

    def test_read_style(self) -> None:
        doc = self.msword_model.doc
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
        

    