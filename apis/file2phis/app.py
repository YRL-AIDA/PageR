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

from pager.page_model.sub_models.extractors  import WordsFromPrecisionPDFExtractor,PrecisionPDFRegionsFromPhisExtractor
from pager import AddArgsFromModelExtractor

from pager import PhisicalModel, TrianglesSortBlock, WordsAndStylesToGLAMBlocks
from pager.page_model.glam_model_20250703 import get_final_model

NAME_DIR_IMAGES = "image_pages"
PATH_STYLE_MODEL = os.getenv("PATH_STYLE_MODEL")

logger = logging.getLogger(__name__)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все домены (для разработки)
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)

word_glam_model = get_final_model( {"GLAM_MODEL":os.environ["PATH_TORCH_GLAM_MODEL"]})
glam_json_unit = word_glam_model.page_units[word_glam_model.keys["json_model"]]
phis_unit = word_glam_model.page_units[word_glam_model.keys["phisical_model"]]
phis_model = phis_unit.sub_model


image_model = ImageModel()
precision_pdf = PrecisionPDFModel()
precision_pdf.num_page = 0
words_model = WordsModel()
# phis_model = PhisicalModel()

wimg2ws = ImageAndWords2WordsAndStyles({
    "path_model": os.environ["PATH_STYLE_MODEL"]
})

words_unit = PageModelUnit("words", words_model, extractors=[
        WordsFromPrecisionPDFExtractor(precision_pdf),
        AddArgsFromModelExtractor([image_model])
        ], converters={})
ws_unit = PageModelUnit("words_and_styles", WordsAndStylesModel(), extractors=[], converters={"words":wimg2ws})


json_unit = PageModelUnit("json", precision_pdf, extractors=[PrecisionPDFRegionsFromPhisExtractor(phis_model)], converters={})

pdf2json = PageModel(page_units=[
    PageModelUnit("pdf", precision_pdf, extractors=[], converters={}),
    words_unit,
    ws_unit,
    glam_json_unit,
    phis_unit,
    json_unit
])

img2json = PageModel(page_units=[
    PageModelUnit("image", image_model, extractors=[], converters={}),
    PageModelUnit("pdf", precision_pdf, extractors=[], converters={"image":Image2PrecisionPDF()}),
    words_unit,
    ws_unit,
    glam_json_unit,
    phis_unit,
    json_unit
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
    shutil.rmtree(path_dir)
    return rez

def processPDF(path_file) -> dict:
    pdf2json.read_from_file(path_file)
    
    name_dir = os.path.dirname(path_file)
    name_imgs_dir = os.path.join(name_dir, NAME_DIR_IMAGES)
    os.mkdir(name_imgs_dir)
    precision_pdf.save_pdf_as_imgs(name_imgs_dir)
    for i in range(precision_pdf.count_page): 
        precision_pdf.num_page = i
        image_model.read_from_file(os.path.join(name_imgs_dir, f"page_{precision_pdf.num_page}.png"))
        pdf2json.extract()
    return pdf2json.to_dict()

def processImg(path_file) -> dict:
    img2json.read_from_file(path_file)
    precision_pdf.num_page = 0
    img2json.extract()
    return img2json.to_dict()

if __name__ == '__main__': 
    uvicorn.run(app=app, port=8000)