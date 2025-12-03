from ..base_sub_model import BaseConverter
from ..pdf_model import PDFModel
from ..image_model import ImageModel
import numpy as np
from pdf2image import convert_from_path

class PDF2Img(BaseConverter):
    def convert(self, input_model: PDFModel, output_model: ImageModel):
        js_page = input_model.to_dict()
        w, h = js_page['width'], js_page['height']
        output_model.img = np.array(convert_from_path(input_model.path, size=(w,h))[input_model.num_page])
