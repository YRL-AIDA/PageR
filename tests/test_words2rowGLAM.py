import unittest
# from pager import (PageModel, PageModelUnit,
#                    ImageModel, Image2WordsAndStyles,
#                    WordsAndStylesModel, PhisicalModel, 
#                    WordsToDBSCANBlocks)
# from pager.page_model.sub_models.dtype import ImageSegment
# from pager.metrics.uoi import segmenter_UoI as UoI, AP_and_AR_from_TP_FP_FN, TP_FP_FN_UoI
# from dotenv import load_dotenv
import os
# load_dotenv(override=True)
# STYLE_MODEL = os.environ["PATH_STYLE_MODEL"]

from pager.page_model.sub_models.converters import Words2Rows
from pager import WordsModel, RowsModel

class TestWords2RowsGLAM(unittest.TestCase):
    words2rows = Words2Rows()

    words = WordsModel()
    rows_true = RowsModel()

    file_name = os.path.join('files','words.json')
    words.read_from_file(file_name)
    
    rows_model = RowsModel()

    def test_convert(self):
        self.words2rows.convert(self.words, self.rows_model)
        self.assertEqual(len(self.rows_model.rows),2)
