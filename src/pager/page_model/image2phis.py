from .page_model import PageModel, PageModelUnit
from .sub_models import ImageModel, WordsAndStylesModel, PhisicalModel, Image2WordsAndStyles, TrianglesSortBlock,WordsAndStylesToGLAMBlocks
from .sub_models.extractors import TableExtractor
from .sub_models.base_sub_model import AddArgsFromModelExtractor
import os
import json
from dotenv import load_dotenv
load_dotenv(override=True)



class Image2Phis(PageModel):
    def __init__(self):
        GLAM_NODE_MODEL = os.getenv("PATH_TORCH_GLAM_NODE_MODEL")
        GLAM_EDGE_MODEL = os.getenv("PATH_TORCH_GLAM_EDGE_MODEL")
        PATH_STYLE_MODEL = os.getenv("PATH_STYLE_MODEL")

        with open(os.getenv("PATH_TORCH_GLAM_CONF_MODEL"), "r") as f:
            conf_glam = json.load(f)
        conf_glam["path_node_gnn"] = GLAM_NODE_MODEL
        conf_glam["path_edge_linear"] =  GLAM_EDGE_MODEL
        image_model = ImageModel()
        super().__init__(page_units=[
        PageModelUnit(id="image_model", 
                        sub_model=image_model, 
                        extractors=[], 
                        converters={}),
        PageModelUnit(id="words_and_styles_model", 
                        sub_model=WordsAndStylesModel(), 
                        extractors=[], 
                        converters={"image_model": Image2WordsAndStyles(
                            conf={"path_model": PATH_STYLE_MODEL,
                                  "lang": "rus+eng", 
                                  "psm": 4, 
                                  "oem": 3,
                                  "onetone_delete": True,
                                  "k": 4})}),
        PageModelUnit(id="phisical_model", 
                        sub_model=PhisicalModel(), 
                        extractors=[TrianglesSortBlock(),
                                    AddArgsFromModelExtractor([image_model]),
                                    TableExtractor()], 
                        converters={
                                "words_and_styles_model": WordsAndStylesToGLAMBlocks(conf_glam)
                        })
        ])