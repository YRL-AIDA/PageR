from ..base_sub_model import BaseConverter
from ..region_model import RegionModel
from ..pdf_model import PDFModel
from ..dtype import Region

class PDF2OnlyFigBlocks(BaseConverter):
    def convert(self, input_model:PDFModel, output_model:RegionModel):
        images = input_model.to_dict()['images']
        for image in images:
            # TODO: сделать FigBlock
            # TODO: маленькие блоки возможно важные элементы!!!
            if image['segment']['height'] < 1 or image['segment']['width'] < 1:
                continue
            reg = Region(image)
            reg.set_label('figure')
            output_model.regions.append(reg)