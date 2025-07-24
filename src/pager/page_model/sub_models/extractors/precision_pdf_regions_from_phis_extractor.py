from ..base_sub_model import BaseExtractor
from ..pdf_model import PrecisionPDFModel
from ..phisical_model import PhisicalModel
from ..exceptions import ConteinNumPage
from ..dtype.block import Word


class PrecisionPDFRegionsFromPhisExtractor(BaseExtractor):
    def __init__(self, phis_model:PhisicalModel):
        self.phis_model = phis_model
        

    def extract(self, model:PrecisionPDFModel):
        if not "num_page" in model.__dict__:
            raise ConteinNumPage()
        
        model.pdf_json["pages"][model.num_page]['regions'] = [{"x_top_left": block.segment.x_top_left,
                                                               "y_top_left": block.segment.y_top_left,
                                                               "width": block.segment.width,
                                                               "height":block.segment.height,
                                                               "text": block.get_text(),
                                                               "label": block.label
                                                              } 
                                                              for block in self.phis_model.blocks]
        