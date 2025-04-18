from pager.page_model.page_model import PageModel, PageModelUnit
from pager.page_model.sub_models import PDFModel, PDF2WordsAndStyles, WordsAndStylesModel, ImageModel, PDF2Img
import os
import argparse
import matplotlib.pyplot as plt
from dotenv import load_dotenv
load_dotenv(override=True)

PATH_STYLE_MODEL = os.environ["PATH_STYLE_MODEL"]
page = PageModel(page_units=[
    PageModelUnit("pdf", PDFModel(), extractors=[], converters={}),
    PageModelUnit("ws", WordsAndStylesModel(), extractors=[], converters={"pdf": PDF2WordsAndStyles(
        conf={"path_model": PATH_STYLE_MODEL,
            "lang": "rus+eng", 
            "psm": 4, 
            "oem": 3,
            "onetone_delete": True,
            "k": 4}),
    }),
    PageModelUnit("img", ImageModel(), extractors=[], converters={"pdf": PDF2Img()}),
])

parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, nargs='?', required=True)
args = parser.parse_args()

page.read_from_file(args.i)
page.extract()
phis = page.to_dict()    


page.page_units[1].sub_model.show()
page.page_units[2].sub_model.show()
plt.show()
