
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import argparse

from pager import (PageModel, PageModelUnit,
                   ImageModel, ImageToWordsAndStyles,
                   WordsAndStylesModel, PhisicalModel, 
                   WordsAndStylesToGNNBlocks)

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
                      converters={"words_and_styles_model": WordsAndStylesToGNNBlocks()})
        ])


parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, nargs='?', required=True)
args = parser.parse_args()

page.read_from_file(args.i)
page.extract()
phis = page.to_dict()    

str_ = "\n"*5+"-"*30+"\n"+"\n".join([f"{i} - block ({b['label']}): \t {b['text']}" for i, b in enumerate(phis['blocks'])]) + "\n"+"-"*30
print(str_) 
