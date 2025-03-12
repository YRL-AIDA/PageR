import unittest
from pager import (PageModel, PageModelUnit,
                   ImageModel, Image2WordsAndStyles,
                   WordsAndStylesModel, WordsAndStylesToSpGraph4N,
                          WordsAndStylesToSpDelaunayGraph, 
                   SpGraph4NModel)
from pager.page_model.sub_models.dtype import ImageSegment
import numpy as np
from dotenv import load_dotenv
import os
load_dotenv(override=True)
STYLE_MODEL = os.environ["PATH_STYLE_MODEL"]

class TestWordsAndStyles2PhisModel(unittest.TestCase):
    page_4n = PageModel(page_units=[
        PageModelUnit(id="image_model", 
                      sub_model=ImageModel(), 
                      extractors=[], 
                      converters={}),
        PageModelUnit(id="words_and_styles_model", 
                      sub_model=WordsAndStylesModel(), 
                      extractors=[], 
                      converters={"image_model": Image2WordsAndStyles({"path_model": STYLE_MODEL})}),
        PageModelUnit(id="graph_model", 
                      sub_model=SpGraph4NModel(), 
                      extractors=[], 
                      converters={"words_and_styles_model": WordsAndStylesToSpGraph4N(conf={"with_text": True})})
        ])
    page_delaunay= PageModel(page_units=[
        PageModelUnit(id="image_model", 
                      sub_model=ImageModel(), 
                      extractors=[], 
                      converters={}),
        PageModelUnit(id="words_and_styles_model", 
                      sub_model=WordsAndStylesModel(), 
                      extractors=[], 
                      converters={"image_model": Image2WordsAndStyles({"path_model": STYLE_MODEL})}),
        PageModelUnit(id="graph_model", 
                      sub_model=SpGraph4NModel(), 
                      extractors=[], 
                      converters={"words_and_styles_model": WordsAndStylesToSpDelaunayGraph(conf={"with_text": True})})
        ])

    page_4n.read_from_file('files/segment_test.png')
    page_4n.extract()
    g1 = page_4n.to_dict()    

    page_delaunay.read_from_file('files/segment_test.png')
    page_delaunay.extract()
    g2 = page_delaunay.to_dict()
    
    def test_size_nodes_feature_4n(self) -> None:
        N, M = np.array(self.g1['nodes_feature']).shape
        self.assertEqual(N, 12, f"Count nodes = {N}")
        # WORD=32 + STYLE=3 + POSITION=2
        self.assertEqual(M, 32+3+2, f"Count nodes = {M}")

    def test_size_nodes_feature_delaunay(self) -> None:
        N, M = np.array(self.g2['nodes_feature']).shape
        self.assertEqual(N, 12, f"Count nodes = {N}")
        # WORD=32 + STYLE=3 + POSITION=2
        self.assertEqual(M, 32+3+2, f"Count nodes = {M}")

        
