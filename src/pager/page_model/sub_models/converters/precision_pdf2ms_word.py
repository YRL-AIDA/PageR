from ..base_sub_model import BaseConverter
from ..pdf_model import PrecisionPDFModel
from ..ms_word_model import MSWordModel
from ..words_model import WordsModel
from ..dtype import Word
from ..base_sub_model import BaseSubModel, BaseExtractor, BaseConverter
from typing import Dict, List
import docx
from ..dtype import Block
from docx.enum.style import WD_STYLE_TYPE


class PrecisionPDFToMSWord(BaseConverter):
    def convert(self, input_model: PrecisionPDFModel, output_model: MSWordModel)-> None:
        pages: List[Dict] = input_model.pdf_json["pages"]
        output_model.doc = docx.Document()
        styles = output_model.doc.styles
        self.LABELS = {
            "text": "Normal",
            "header": "Heading 1",
            "list": "List",
            "table": "Normal",
            # "figure": "Normal",
        }
        for page in pages:
            self.add_page(output_model.doc, page, styles)
      

    def add_page(self, doc: docx.Document, page: Dict, styles)-> None:
        for regions in page["regions"]:
            label = regions["label"]
            text = regions["text"]
            if label != "figure":
                doc.add_paragraph(text).style = styles[self.LABELS[label]]
        doc.add_page_break()