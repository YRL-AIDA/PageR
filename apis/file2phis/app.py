import os
import shutil
import logging
import uuid
import json 

import uvicorn
from fastapi import FastAPI, UploadFile, Form, File, Response
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from pager import PageModel
from pager.page_model.sub_models import PDFModel, ImageModel

from pager import PrecisionPDFModel

from pager.pager_pipe_line import (
    pdf2json_word, pdf2json_row, pdf2json_one,
    img2json_word, img2json_row, img2json_one,
    json2docx
)
image_model = ImageModel()
NAME_DIR_IMAGES = "image_pages"
# PATH_STYLE_MODEL = os.getenv("PATH_STYLE_MODEL")

logger = logging.getLogger(__name__)
app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все домены (для разработки)
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)

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
        read_file = lambda file: pdf2json_row.read_from_file(file)
        filejson: PageModel = pdf2json_row
    elif IS_ONLY_TEXT:
        read_file = lambda file: pdf2json_one.read_from_file(file)
        filejson: PageModel = pdf2json_one
    else:
        read_file = lambda file: pdf2json_word.read_from_file(file)
        filejson: PageModel = pdf2json_word

    read_file(path_file)
    pdf_model: PDFModel = filejson.page_units[0].sub_model
    if IS_NEED_IMAGES:
        name_imgs_dir = save_images_from_pdf(pdf_model.pdf_parser, path_file)
    if IS_AS_IMAGES:
        rez = pdf_model.pdf_parser.pdf_json
    print(pdf_model.pdf_parser.count_page)
    for i in range(pdf_model.pdf_parser.count_page):
        if IS_AS_IMAGES:
            page = processImg(os.path.join(name_imgs_dir, f"page_{i}.png"), process)['pages'][0]
            rez['pages'][i] = page 
        else:
            pdf_model.pdf_parser.num_page = i
            if IS_NEED_IMAGES:
                image_model.read_from_file(os.path.join(name_imgs_dir, f"page_{i}.png"))
            filejson.extract()
    if not IS_AS_IMAGES:
        rez = filejson.to_dict()
    return rez

def save_images_from_pdf(pdf_parser: PrecisionPDFModel, path_file):
    name_dir = os.path.dirname(path_file)
    name_imgs_dir = os.path.join(name_dir, NAME_DIR_IMAGES)
    os.mkdir(name_imgs_dir)
    pdf_parser.save_pdf_as_imgs(name_imgs_dir)
    return name_imgs_dir

def processPdfImgs(path_file, process) -> dict:
    images = os.listdir(path_file)
    images.sort()
    for i, image in enumerate(images):
        page = processImg(os.path.join(path_file, image), process)
    page['pages']


def processImg(path_file, process) -> dict:
    filejson = img2json_one if "only_text" in process and process["only_text"] else img2json_word
    filejson.read_from_file(path_file)
    filejson.page_units[1].sub_model.num_page = 0
    filejson.extract()
    return filejson.to_dict()

if __name__ == '__main__': 
    uvicorn.run(app=app, port=8000)