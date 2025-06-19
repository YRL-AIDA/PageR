from ..base_sub_model import BaseConverter
from ..pdf_model import PrecisionPDFModel
from ..phisical_model import PhisicalModel
from ..dtype import Word, ImageSegment, Block

class PDF2PageBlocks(BaseConverter):
    def convert(self, input_model: PrecisionPDFModel, output_model: PhisicalModel):
        page_json = input_model.to_dict()
        block_list = self.get_blocks(page_json['pages'])
        output_model.blocks = block_list

    def get_blocks(self, pages_list):
        return [self.get_block(page) for page in pages_list]
    
    def get_block(self, page):
        words = []
        number_page = page["number"]
        for word in page["words"]:
            if word["height"] < 1 or word["width"] < 1:
                continue
            word["segment"] = word
            word_el = Word(word)
            word_el.segment.add_info("number_page", number_page)
            words.append(word_el)

        seg = ImageSegment(0,0,1,1)
        seg.set_segment_max_segments([w.segment for w in words])
        seg.add_info("number_page", number_page)
        block = Block({})
        block.segment = seg
        block.words = words
        block.label = "text"
        return block
    
