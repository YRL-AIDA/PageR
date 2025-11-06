from ..base_sub_model import BaseConverter
from ..region_model import RegionModel
from ..pdf_model import PDFModel
from ..dtype import Block

class PDF2OnlyFigBlocks(BaseConverter):
    def convert(self, input_model:PDFModel, output_model:RegionModel):
        images = input_model.to_dict()['images']
        for image in images:
            # TODO: сделать FigBlock
            # TODO: маленькие блоки возможно важные элементы!!!
            if image['height'] < 1 or image['width'] < 1:
                continue
            block = Block(image)
            block.set_label('figure')
            output_model.blocks.append(block)