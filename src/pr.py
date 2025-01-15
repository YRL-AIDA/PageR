import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
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
                   WordsToDBSCANBlocks)
if __name__ == "__main__":
    page = PageModel(page_units=[
        PageModelUnit(id="image_model", 
                      sub_model=ImageModel(), 
                      extractors=[], 
                      converters={}),
        PageModelUnit(id="words_and_styles_model", 
                      sub_model=WordsAndStylesModel(), 
                      extractors=[], 
                      converters={"image_model": ImageToWordsAndStyles()}),
        PageModelUnit(id="phisical_model", 
                      sub_model=PhisicalModel(), 
                      extractors=[], 
                      converters={"words_and_styles_model": WordsToDBSCANBlocks()})
        ])


    page.read_from_file(sys.argv[1])
    page.extract()
    phis = page.to_dict()    
    name_class = ["no_struct", "text", "hea:der", "list", "table"]
    str_ = "".join([f"\n{'-'*10}{b['label']}{'-'*10}\n{b['text']}" for i, b in enumerate(phis['blocks'])])
    print(str_)

#    for b in phis['blocks']:
#        print(b)
 
