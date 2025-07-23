import os
import shutil
import logging
import uuid
import json 

import uvicorn
from fastapi import FastAPI, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware

from pager import PageModel, PageModelUnit
from pager.page_model.sub_models import PrecisionPDFModel, ImageModel, Image2PrecisionPDF
from pager import WordsModel, WordsAndStylesModel, ImageAndWords2WordsAndStyles

from pager.page_model.sub_models.extractors  import WordsFromPrecisionPDFExtractor
from pager import AddArgsFromModelExtractor

from pager import PhisicalModel, TrianglesSortBlock, WordsAndStylesToGLAMBlocks

NAME_DIR_IMAGES = "image_pages"


logger = logging.getLogger(__name__)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все домены (для разработки)
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)

GLAM_NODE_MODEL = os.getenv("PATH_TORCH_GLAM_NODE_MODEL")
GLAM_EDGE_MODEL = os.getenv("PATH_TORCH_GLAM_EDGE_MODEL")
PATH_STYLE_MODEL = os.getenv("PATH_STYLE_MODEL")

with open(os.getenv("PATH_TORCH_GLAM_CONF_MODEL"), "r") as f:
    conf_glam = json.load(f)
conf_glam["path_node_gnn"] = GLAM_NODE_MODEL
conf_glam["path_edge_linear"] =  GLAM_EDGE_MODEL

image_model = ImageModel()

precision_pdf = PrecisionPDFModel()
precision_pdf.num_page = 0

words_model = WordsModel()

wimg2ws = ImageAndWords2WordsAndStyles({
    "path_model": os.environ["PATH_STYLE_MODEL"]
})

words_unit = PageModelUnit("words", words_model, extractors=[
        WordsFromPrecisionPDFExtractor(precision_pdf),
        AddArgsFromModelExtractor([image_model])
        ], converters={})
ws_unit = PageModelUnit("ws", WordsAndStylesModel(), extractors=[], converters={"words":wimg2ws})

phis_unit = PageModelUnit(id="phisical_model", 
                        sub_model=PhisicalModel(), 
                        extractors=[TrianglesSortBlock(),
                                    # AddArgsFromModelExtractor([image_model]),
                                    #TableExtractor()
                                    ], 
                        converters={
                                "ws": WordsAndStylesToGLAMBlocks(conf_glam)
                        })

pdf2json = PageModel(page_units=[
    PageModelUnit("pdf", precision_pdf, extractors=[], converters={}),
    words_unit,
    ws_unit,
    phis_unit
    
])

img2json = PageModel(page_units=[
    PageModelUnit("image", image_model, extractors=[], converters={}),
    PageModelUnit("pdf", precision_pdf, extractors=[], converters={"image":Image2PrecisionPDF()}),
    words_unit,
    ws_unit,
    phis_unit
])


@app.post("/")
async def read_pdf(file: UploadFile = File(...),
                   process:str = Form(...)):
    logger.info("start")
    path_dir = os.path.join(os.getcwd(), "tmp_dir", uuid.uuid4().hex)
    os.mkdir(path_dir)
    typefile = file.filename.split(".")[-1].lower() 

    if typefile in ('pdf', ):
        path_file =  os.path.join(path_dir, "file.pdf")
        process = processPDF   
    elif typefile in ('png', 'jpeg', 'jpg'):  
        path_image_dir = os.path.join(path_dir, NAME_DIR_IMAGES)
        os.mkdir(path_image_dir)
        path_file = os.path.join(path_image_dir, f"page_0.{typefile}")
        process = processImg
    else:
        return {"error": "Неизвестный тип файла"}

    with open(path_file, "wb") as f:
        f.write(file.file.read())
    rez = process(path_file)
    # shutil.rmtree(path_dir)
    return rez

def processPDF(path_file) -> dict:
    pdf2json.read_from_file(path_file)
    
    name_dir = os.path.dirname(path_file)
    name_imgs_dir = os.path.join(name_dir, NAME_DIR_IMAGES)
    os.mkdir(name_imgs_dir)
    precision_pdf.save_pdf_as_imgs(name_imgs_dir)

    precision_pdf.num_page = 0
    image_model.read_from_file(os.path.join(name_imgs_dir, f"page_{precision_pdf.num_page}.png"))
    pdf2json.extract()
    rez = pdf2json.to_dict()

    return rez

def processImg(path_file) -> dict:
    img2json.read_from_file(path_file)
    precision_pdf.num_page = 0
    img2json.extract()
    rez = img2json.to_dict()

    return rez

if __name__ == '__main__': 
    uvicorn.run(app=app, port=8000)