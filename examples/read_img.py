
import os
import argparse

from pager import (PageModel, PageModelUnit,
                   ImageModel, ImageToWordsAndStyles,
                   WordsAndStylesModel, PhisicalModel, 
                   WordsAndStylesToGNNpLinearBlocks
                   )
from dotenv import load_dotenv
load_dotenv()
GNN_MODEL = os.environ["PATH_TORCH_SEG_GNN_MODEL"]
LINEAR_MODEL = os.environ["PATH_TORCH_SEG_LINEAR_MODEL"]

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
                      converters={"words_and_styles_model": WordsAndStylesToGNNpLinearBlocks(conf={
                          "path_node_gnn": GNN_MODEL,
                          "path_edge_linear": LINEAR_MODEL,
                          "seg_k": 0.5
                      })})
        ])


parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, nargs='?', required=True)
args = parser.parse_args()

page.read_from_file(args.i)
page.extract()
phis = page.to_dict()    

str_ = "\n"*5+"-"*30+"\n"+"\n".join([f"{i} - block ({b['label']}): \t {b['text']}" for i, b in enumerate(phis['blocks'])]) + "\n"+"-"*30
print(str_) 
