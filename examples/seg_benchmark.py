from pager.benchmark.seg_detection.seg_detection import  SegDetectionBenchmark
import os
from pager import (PageModel, PageModelUnit,
                   ImageModel, ImageToWordsAndStyles,
                   WordsAndStylesModel, PhisicalModel, 
                   )
from pager import WordsAndStylesToGNNpLinearBlocks
from pager import WordsToDBSCANBlocks
GNN_MODEL = os.environ["PATH_TORCH_SEG_GNN_MODEL"]
LINEAR_MODEL = os.environ["PATH_TORCH_SEG_LINEAR_MODEL"]

if __name__ == '__main__':
    

    page = PageModel(page_units=[
        PageModelUnit(id="image_model", 
                      sub_model=ImageModel(), 
                      extractors=[], 
                      converters={}),
        PageModelUnit(id="words_and_styles_model", 
                      sub_model=WordsAndStylesModel(), 
                      extractors=[], 
                      converters={"image_model": ImageToWordsAndStyles(conf= {"k": 4})}),
        PageModelUnit(id="phisical_model", 
                      sub_model=PhisicalModel(), 
                      extractors=[], 
                      converters={"words_and_styles_model": WordsToDBSCANBlocks()})
        # PageModelUnit(id="phisical_model", 
        #               sub_model=PhisicalModel(), 
        #               extractors=[], 
        #               converters={"words_and_styles_model": WordsAndStylesToGNNpLinearBlocks(conf={
        #                   "path_node_gnn": GNN_MODEL,
        #                   "path_edge_linear": LINEAR_MODEL,
        #                   "seg_k": 0.5
        #               })})
        ])
    path_dataset = "seg_data"
    benchmark = SegDetectionBenchmark(path_dataset, page_model=page)
    