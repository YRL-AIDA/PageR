
import os
import argparse
import json 
from pager import (PageModel, PageModelUnit,
                   ImageModel, Image2WordsAndStyles,
                   WordsAndStylesModel, PhisicalModel, 
                   WordsAndStylesToGNNpLinearBlocks,
                   ImageToWordsAndCNNStyles,
                   WordsAndStylesToGLAMBlocks,
                   TrianglesSortBlock
                   )
from dotenv import load_dotenv
from pager.page_model.glam_model_20250415 import get_final_model

load_dotenv(override=True)
GNN_MODEL = os.environ["PATH_TORCH_SEG_GNN_MODEL"]
LINEAR_MODEL = os.environ["PATH_TORCH_SEG_LINEAR_MODEL"]

GLAM_NODE_MODEL = os.getenv("PATH_TORCH_GLAM_NODE_MODEL")
GLAM_EDGE_MODEL = os.getenv("PATH_TORCH_GLAM_EDGE_MODEL")
GLAM_MODEL = os.getenv("PATH_TORCH_GLAM_MODEL")
PATH_STYLE_MODEL = os.environ["PATH_STYLE_MODEL"]

with open(os.environ["PATH_TORCH_GLAM_CONF_MODEL"], "r") as f:
    conf_glam = json.load(f)

conf_glam["path_node_gnn"] = GLAM_NODE_MODEL
conf_glam["path_edge_linear"] =  GLAM_EDGE_MODEL

page =  PageModel(page_units=[
        PageModelUnit(id="image_model", 
                        sub_model=ImageModel(), 
                        extractors=[], 
                        converters={}),
        PageModelUnit(id="words_and_styles_model", 
                        sub_model=WordsAndStylesModel(), 
                        extractors=[], 
                        converters={"image_model": ImageToWordsAndCNNStyles(
                            conf={"path_model": PATH_STYLE_MODEL,
                                  "lang": "rus+eng", 
                                  "psm": 4, 
                                  "oem": 3,
                                  "onetone_delete": True,
                                  "k": 4})}),
        PageModelUnit(id="phisical_model", 
                        sub_model=PhisicalModel(), 
                        extractors=[TrianglesSortBlock()], 
                        converters={
                                "words_and_styles_model": WordsAndStylesToGLAMBlocks(conf_glam)
                        })
        ])

page = get_final_model({"GLAM_MODEL": GLAM_MODEL})
parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, nargs='?', required=True)
args = parser.parse_args()

page.read_from_file(args.i)
page.extract()
phis = page.to_dict()    

str_ = "\n"*5+"-"*30+"\n"+"\n".join([f"{i} - block ({b['label']}): \t {b['text']}" for i, b in enumerate(phis['blocks'])]) + "\n"+"-"*30
print(str_) 

import matplotlib.pyplot as plt
page.page_units[0].sub_model.show()
page.page_units[3].sub_model.show()
plt.show()