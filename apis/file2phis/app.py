import os
import shutil
import logging
import uuid
import json 

from io import BytesIO

import uvicorn
from fastapi import FastAPI, UploadFile, Form, File, Response
from fastapi.responses import FileResponse,StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from pager import PageModel, PageModelUnit
from pager.page_model.sub_models import PrecisionPDFModel, ImageModel, Image2PrecisionPDF
from pager import WordsModel, WordsAndStylesModel, ImageAndWords2WordsAndStyles
from pager import RowsModel

from pager.page_model.sub_models.extractors  import WordsFromPrecisionPDFExtractor, RowsFromPrecisionPDFExtractor, PrecisionPDFRegionsFromPhisExtractor
from pager import AddArgsFromModelExtractor

from pager import PhisicalModel, TrianglesSortBlock, WordsAndStylesToGLAMBlocks, MSWordModel, PrecisionPDFToMSWord
from pager import Words2OneBlock
from pager.page_model.glam_model_20250703 import get_final_model
from pager.page_model.row_glam_20250811 import get_final_model as get_final_model_row


NAME_DIR_IMAGES = "image_pages"
PATH_STYLE_MODEL = os.getenv("PATH_STYLE_MODEL")

logger = logging.getLogger(__name__)
app = FastAPI(debug=True)

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


row_glam_model = get_final_model_row({"ROW_GLAM": os.environ["PATH_TORCH_ROW_GLAM"]})
row_glam_json_unit = row_glam_model.page_units[row_glam_model.keys["json_model"]]
row_phis_unit = row_glam_model.page_units[row_glam_model.keys["phisical_model"]]
row_phis_model = row_phis_unit.sub_model

image_model = ImageModel()
precision_pdf = PrecisionPDFModel()
precision_pdf.num_page = 0
words_model = WordsModel()
rows_model = RowsModel()
# phis_model = PhisicalModel()

wimg2ws = ImageAndWords2WordsAndStyles({
    "path_model": os.environ["PATH_STYLE_MODEL"]
})

words_unit = PageModelUnit("words", words_model, extractors=[
        WordsFromPrecisionPDFExtractor(precision_pdf),
        AddArgsFromModelExtractor([image_model])
        ], converters={})

rows_unit = PageModelUnit("rows", rows_model, extractors=[
        RowsFromPrecisionPDFExtractor(precision_pdf)
        ], converters={})

ws_unit = PageModelUnit("words_and_styles", WordsAndStylesModel(), extractors=[], converters={"words":wimg2ws})


json_unit = PageModelUnit("json", precision_pdf, extractors=[PrecisionPDFRegionsFromPhisExtractor(phis_model)], converters={})
row_json_unit = PageModelUnit("json", precision_pdf, extractors=[PrecisionPDFRegionsFromPhisExtractor(row_phis_model)], converters={})

pdf2json = PageModel(page_units=[
    PageModelUnit("pdf", precision_pdf, extractors=[], converters={}),
    words_unit,
    ws_unit,
    glam_json_unit,
    phis_unit,
    json_unit
])
pdf_row2json = PageModel(page_units=[
    PageModelUnit("pdf", precision_pdf, extractors=[], converters={}),
    rows_unit,
    row_glam_json_unit,
    row_phis_unit,
    row_json_unit
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

simple_phis_unit = PageModelUnit("simple_phis", phis_model, extractors=[], converters={"words": Words2OneBlock()})
pdf2simplejson = PageModel(page_units=[
    PageModelUnit("pdf", precision_pdf, extractors=[], converters={}),
    words_unit,
    simple_phis_unit,
    json_unit
])
img2simplejson = PageModel(page_units=[
    PageModelUnit("image", image_model, extractors=[], converters={}),
    PageModelUnit("pdf", precision_pdf, extractors=[], converters={"image":Image2PrecisionPDF()}),
    words_unit,
    simple_phis_unit,
    json_unit
])


unit_json_precision_pdf = PageModelUnit("json_precision_pdf", PrecisionPDFModel(), extractors=[], converters={})
unit_ms_word = PageModelUnit("ms_word", MSWordModel(), extractors=[], converters={"json_precision_pdf": PrecisionPDFToMSWord()})

json2docx = PageModel(page_units=[
    unit_json_precision_pdf,
    unit_ms_word
])

@app.get("/health")
async def health():
    if False:
        return {"status": "error"}
    return {"status": "ok"}


@app.post("/")
async def read_pdf(file: UploadFile = File(...),
                   process:str = Form(...)):
    logger.info("start")
    process = json.loads(process)
    path_dir = os.path.join(os.getcwd(), "tmp_dir", uuid.uuid4().hex)
    os.mkdir(path_dir)
    typefile = file.filename.split(".")[-1].lower() 

    if typefile in ('pdf', ):
        path_file =  os.path.join(path_dir, "file.pdf")
        processFile = processPDF   
    elif typefile in ('png', 'jpeg', 'jpg'):  
        path_image_dir = os.path.join(path_dir, NAME_DIR_IMAGES)
        os.mkdir(path_image_dir)
        path_file = os.path.join(path_image_dir, f"page_0.{typefile}")
        processFile = processImg
    else:
        return {"error": "Неизвестный тип файла"}

    with open(path_file, "wb") as f:
        f.write(file.file.read())
    rez = processFile(path_file, process)
    shutil.rmtree(path_dir)
    return rez

from pydantic import BaseModel
class JsonTask(BaseModel):
    precisionPDF_json: str
    name_save: str
@app.post("/json2word")
async def convert_json_to_docx(task: JsonTask):
    logger.info("start")

    json_task = json.loads(task.precisionPDF_json)
    json2docx.from_dict(json_task)
    json2docx.extract()
    path_dir = os.path.join(os.getcwd(), "tmp_dir", uuid.uuid4().hex)
    os.mkdir(path_dir)
    name = "file.docx"
    path = os.path.join(path_dir, name)
    json2docx.page_units[-1].sub_model.save_doc(path) 
    # отправка файла без удаления
    # return FileResponse(path=path, 
    #                     filename=task.name_save, media_type='multipart/form-data') 
    with open(path, "rb") as f:
        file = f.read()

    shutil.rmtree(path_dir)
    return Response(file)

    

def processPDF(path_file, process) -> dict:
    IS_GLAM_ROW = "glam_rows" in process and process["glam_rows"]
    IS_ONLY_TEXT = "only_text" in process and process["only_text"]
    IS_AS_IMAGES = "is_images" in process and process["is_images"]
    IS_NEED_IMAGES = not IS_GLAM_ROW or not IS_ONLY_TEXT
    

    if IS_GLAM_ROW:
        read_file = lambda file: pdf_row2json.page_units[0].sub_model.read_from_file(file, method="r")
        filejson = pdf_row2json
    elif IS_ONLY_TEXT:
        read_file = lambda file: pdf2simplejson.page_units[0].sub_model.read_from_file(file, method="w")
        filejson = pdf2simplejson
    else:
        read_file = lambda file: pdf2json.page_units[0].sub_model.read_from_file(file, method="w")
        filejson = pdf2json

    read_file(path_file)
    if IS_NEED_IMAGES:
        name_imgs_dir = save_images_from_pdf(path_file)
    if IS_AS_IMAGES:
        rez = precision_pdf.pdf_json
    
    for i in range(precision_pdf.count_page):
        if IS_AS_IMAGES:
            page = processImg(os.path.join(name_imgs_dir, f"page_{i}.png"), process)['pages'][0]
            rez['pages'][i] = page 
        else:
            precision_pdf.num_page = i
            if IS_NEED_IMAGES:
                image_model.read_from_file(os.path.join(name_imgs_dir, f"page_{i}.png"))
            filejson.extract()

    if not IS_AS_IMAGES:
        rez = filejson.to_dict()
    return rez

def save_images_from_pdf(path_file):
    name_dir = os.path.dirname(path_file)
    name_imgs_dir = os.path.join(name_dir, NAME_DIR_IMAGES)
    os.mkdir(name_imgs_dir)
    precision_pdf.save_pdf_as_imgs(name_imgs_dir)
    return name_imgs_dir

def processPdfImgs(path_file, process) -> dict:
    images = os.listdir(path_file)
    images.sort()
    for i, image in enumerate(images):
        page = processImg(os.path.join(path_file, image), process)
    page['pages']


def processImg(path_file, process) -> dict:
    filejson = img2simplejson if "only_text" in process and process["only_text"] else img2json
    filejson.read_from_file(path_file)
    precision_pdf.num_page = 0
    filejson.extract()
    return filejson.to_dict()

if __name__ == '__main__': 
    uvicorn.run(app=app, port=8000)