import os
from dotenv import load_dotenv
load_dotenv()

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
GNN_MODEL = os.environ["PATH_TORCH_SEG_GNN_MODEL"]
LINEAR_MODEL = os.environ["PATH_TORCH_SEG_LINEAR_MODEL"]
"""
pr - Page Read

> python pr.py path_file.format
>
> ---------- header ----------- 
> header
> ---------- text -----------
> text text text
> ---------- list -----------
> 1. list
> 2. list
"""
import sys
from pager import (PageModel, PageModelUnit,
                   ImageModel, ImageToWordsAndStyles,
                   WordsAndStylesModel, PhisicalModel, 
                   )
from pager import WordsAndStylesToGNNpLinearBlocks
# from pager import WordsToDBSCANBlocks

if __name__ == "__main__":
    # page = PageModel(page_units=[
    #     PageModelUnit(id="image_model", 
    #                   sub_model=ImageModel(), 
    #                   extractors=[], 
    #                   converters={}),
    #     PageModelUnit(id="words_and_styles_model", 
    #                   sub_model=WordsAndStylesModel(), 
    #                   extractors=[], 
    #                   converters={"image_model": ImageToWordsAndStyles()}),
    #     # PageModelUnit(id="phisical_model", 
    #     #               sub_model=PhisicalModel(), 
    #     #               extractors=[], 
    #     #               converters={"words_and_styles_model": WordsToDBSCANBlocks()})
    #     PageModelUnit(id="phisical_model", 
    #                   sub_model=PhisicalModel(), 
    #                   extractors=[], 
    #                   converters={"words_and_styles_model": WordsAndStylesToGNNpLinearBlocks(conf={
    #                       "path_node_gnn": GNN_MODEL,
    #                       "path_edge_linear": LINEAR_MODEL,
    #                       "seg_k": 0.5
    #                   })})
    #     ])

    from pager import WordsAndStylesToGLAMBlocks,ImageToWordsAndCNNStyles

    GLAM_NODE_MODEL = os.environ["PATH_TORCH_GLAM_NODE_MODEL"]
    GLAM_EDGE_MODEL = os.environ["PATH_TORCH_GLAM_EDGE_MODEL"]
    PATH_STYLE_MODEL = os.environ["PATH_STYLE_MODEL"]
    page = PageModel(page_units=[
    PageModelUnit(id="image_model", 
                  sub_model=ImageModel(), 
                  extractors=[], 
                  converters={}),
    PageModelUnit(id="words_and_styles_model", 
                  sub_model=WordsAndStylesModel(), 
                  extractors=[], 
                  converters={"image_model": ImageToWordsAndCNNStyles(conf={"path_model": PATH_STYLE_MODEL,"lang": "rus", "psm": 4, "oem": 3, "k": 4 })}),
    PageModelUnit(id="phisical_model", 
                  sub_model=PhisicalModel(), 
                  extractors=[], 
                  converters={
                          "words_and_styles_model": WordsAndStylesToGLAMBlocks(conf={
                          "path_node_gnn": GLAM_NODE_MODEL,
                          "path_edge_linear": GLAM_EDGE_MODEL,
                          "H1": [128, 128, 128, 128, 128],
                          "H2": [128],
                          "seg_k": 0.5
                  })})
    ])

    page.read_from_file(sys.argv[1])
    page.extract()
    phis = page.to_dict()    
    name_class = ["no_struct", "text", "hea:der", "list", "table"]
    str_ = "".join([f"\n{'-'*10}{b['label']}{'-'*10}\n{b['text']}" for i, b in enumerate(phis['blocks'])])
    print(str_)

#    for b in phis['blocks']:
#        print(b)
 
