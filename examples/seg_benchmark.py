from pager.benchmark.seg_detection.seg_detection_torchmetrics import  SegDetectionBenchmark
import os
import json
from pager import (PageModel, PageModelUnit,
                   ImageModel, ImageToWordsAndStyles,
                   WordsAndStylesModel, PhisicalModel, ImageToWordsAndCNNStyles,
                   )
from pager import WordsAndStylesToGNNpLinearBlocks
from pager import WordsAndStylesToGLAMBlocks
from pager import WordsToDBSCANBlocks

from dotenv import load_dotenv
load_dotenv(override=True)
GNN_MODEL = os.environ["PATH_TORCH_SEG_GNN_MODEL"]
LINEAR_MODEL = os.environ["PATH_TORCH_SEG_LINEAR_MODEL"]

GLAM_NODE_MODEL = os.getenv("PATH_TORCH_GLAM_NODE_MODEL")
GLAM_EDGE_MODEL = os.getenv("PATH_TORCH_GLAM_EDGE_MODEL")
PATH_STYLE_MODEL = os.environ["PATH_STYLE_MODEL"]

with open(os.environ["PATH_TORCH_GLAM_CONF_MODEL"], "r") as f:
    conf_glam = json.load(f)

conf_glam["path_node_gnn"] = GLAM_NODE_MODEL
conf_glam["path_edge_linear"] =  GLAM_EDGE_MODEL

if __name__ == '__main__':
    pages = {
        "DBSCANBlocks":
        PageModel(page_units=[
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
        ]),
        "GNNpLinearBlocks":
        PageModel(page_units=[
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
        ]),
        "GLAM-word":
        PageModel(page_units=[
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
                                  "k": 4 })}),
        PageModelUnit(id="phisical_model", 
                        sub_model=PhisicalModel(), 
                        extractors=[], 
                        converters={
                                "words_and_styles_model": WordsAndStylesToGLAMBlocks(conf_glam)
                        })
        ])
    }
    
    path_dataset = "seg_data"
    for name, page in pages.items():
        benchmark = SegDetectionBenchmark(path_dataset, page_model=page, name=name)