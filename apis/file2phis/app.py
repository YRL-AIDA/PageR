import os
import shutil
import logging
import uuid
import json 

import uvicorn
from fastapi import FastAPI, UploadFile, Form, File, Response
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from pagerlib.dtypes import PageRDF
from pagerlib.extractors.page_extractor import Rows2Regions , Words2Rows, MergeRegion, PDFIMGExtractor
from pagerlib.file_input import FileInput
from pathlib import Path

from PIL import Image
from io import BytesIO
import base64
import numpy as np

file_inpit = FileInput()
words2rows = Words2Rows()
rows2regions = Rows2Regions()
merge_region = MergeRegion()
pdf2img = PDFIMGExtractor()
path = Path(os.getcwd(), "tmp_dir")
path.mkdir(exist_ok=True)

def np_array_to_base64(image: np.ndarray) -> str:
    image = Image.fromarray(image)
    image_bytes = BytesIO()
    image.save(image_bytes, format='PNG')
    base64_image = base64.b64encode(image_bytes.getvalue()).decode('utf-8')

    return base64_image

def pagerdf2json(pagerdf:PageRDF):
    pages = []
    for i, prdf_page in enumerate(pagerdf.data['pages']):
        img_page = prdf_page.children[0].data['array']
        prdf_page.children = prdf_page.children[1:]
        page = prdf_page.to_dict()
        page['number'] = i
        seg = page.pop('segment')
        page['height'] = seg['height']
        page['width'] = seg['width']
        data = page.pop('data')
        for reg, prdf_reg in zip(page['regions'], prdf_page.children) :
            reg['text'] = ''
            data = reg.pop('data')
            reg['label'] = data['label'] if 'label' in data else 'text'

            if reg['label'] in  ('figure', 'image'):
                reg['base64'] = np_array_to_base64(prdf_reg.segment.get_segment_from_img(img_page))

            if not 'rows' in reg:
                continue
            for row in reg['rows']:
                row.pop('data')
                row['text'] = ''
                for word in row['words']:
                    data = word.pop('data')
                    word['text'] = data['text']
                    row['text'] += word['text'] + ' '
                reg['text'] += row['text'] + ' '
        pages.append(page)    
                    
    return {
        "pages": pages 
    }

def pdf2region4precission(path):
    path = Path(path)
    pagerdf = file_inpit(path)
    rows2regions.extract(pagerdf)
    merge_region.extract(pagerdf)
    pages = [page.to_dict() for page in pagerdf.data['pages']] 
    for i, page in enumerate(pages):
        page['number'] = i
        new_regions = [{"segment": reg['segment'], 
                        "label":  reg['data']['label'] if 'label' in reg['data'] else 'text'} for reg in page['regions']]
        page['regions'] = new_regions
    return {
        "pages": pages
    }

            

def file2json(path, params):
    path = Path(path)
    pagerdf = file_inpit(path)
    is_image = path.suffix.lower() in ('.png', '.jpg', '.jpeg')
    if "only_text" in params and params["only_text"]:
        return pagerdf2json(pagerdf)
    
    if "glam_words" in params and params["glam_words"]:
        words2rows.extract(pagerdf)
    elif not "glam_words" in params and is_image:
        words2rows.extract(pagerdf)
    
    if not "glam_rows" in params or params["glam_rows"]:
        rows2regions.extract(pagerdf)
    if not is_image:
        pdf2img.extract(pagerdf)
    merge_region.extract(pagerdf)
    return pagerdf2json(pagerdf)
        
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
    if not typefile in ('pdf', 'png', 'jpeg', 'jpg'):
        shutil.rmtree(path_dir)
        return {"error": "Неизвестный тип файла"} 
    path_file =  os.path.join(path_dir, "file."+typefile)   
    with open(path_file, "wb") as f:
        f.write(file.file.read())
    rez = file2json(path_file, process)
    shutil.rmtree(path_dir)
    return rez

@app.post("/precision-pdf/")
async def read_pdf(file: UploadFile = File(...)):
    logger.info("start")
    path_dir = os.path.join(os.getcwd(), "tmp_dir", uuid.uuid4().hex)
    os.mkdir(path_dir)
    typefile = file.filename.split(".")[-1].lower() 
    if not typefile in ('pdf'):
        shutil.rmtree(path_dir)
        return {"error": "Неизвестный тип файла"} 
    path_file =  os.path.join(path_dir, "file.pdf")   
    with open(path_file, "wb") as f:
        f.write(file.file.read())
    rez = pdf2region4precission(path_file)
    shutil.rmtree(path_dir)
    return rez

# class JsonTask(BaseModel):
#     precisionPDF_json: str
#     name_save: str
# @app.post("/json2word")
# async def convert_json_to_docx(task: JsonTask):
#     logger.info("start")

#     json_task = json.loads(task.precisionPDF_json)
#     json2docx.from_dict(json_task)
#     json2docx.extract()
#     path_dir = os.path.join(os.getcwd(), "tmp_dir", uuid.uuid4().hex)
#     os.mkdir(path_dir)
#     name = "file.docx"
#     path = os.path.join(path_dir, name)
#     json2docx.save_doc(path) 
#     # отправка файла без удаления
#     # return FileResponse(path=path, 
#     #                     filename=task.name_save, media_type='multipart/form-data') 
#     with open(path, "rb") as f:
#         file = f.read()

#     shutil.rmtree(path_dir)
#     return Response(file)

    

# def processPDF(path_file, process) -> dict:
#     IS_GLAM_ROW = "glam_rows" in process and process["glam_rows"]
#     IS_ONLY_TEXT = "only_text" in process and process["only_text"]
#     IS_AS_IMAGES = "is_images" in process and process["is_images"]
    

#     if IS_GLAM_ROW:
#         filejson:PrecisionPDFModel = pdf2json_row
#     elif IS_ONLY_TEXT:
#         filejson:PrecisionPDFModel = pdf2json_one
#     else:
#         filejson:PrecisionPDFModel = pdf2json_word

#     filejson.read_from_file(path_file)
#     if IS_AS_IMAGES:
#         name_imgs_dir = save_images_from_pdf(filejson, path_file)
#         rez = {"pages": []}
#         for i in range(filejson.count_page):
#             page = processImg(os.path.join(name_imgs_dir, f"page_{i}.png"), process)['pages'][0]
#             page['number'] = i
#             rez['pages'].append(page.copy())
#     else:
#         print("START")
#         filejson.extract()
#         rez = filejson.to_dict()
#     return rez

# def save_images_from_pdf(pdf_parser: PrecisionPDFModel, path_file):
#     name_dir = os.path.dirname(path_file)
#     name_imgs_dir = os.path.join(name_dir, NAME_DIR_IMAGES)
#     os.mkdir(name_imgs_dir)
#     pdf_parser.save_pdf_as_imgs(name_imgs_dir)
#     return name_imgs_dir

# def processPdfImgs(path_file, process) -> dict:
#     images = os.listdir(path_file)
#     images.sort()
#     for i, image in enumerate(images):
#         page = processImg(os.path.join(path_file, image), process)
#     page['pages']


# def processImg(path_file, process) -> dict:
#     filejson = img2json_one if "only_text" in process and process["only_text"] else img2json_word
#     filejson.read_from_file(path_file)
#     filejson.extract()
#     return filejson.to_dict()

if __name__ == '__main__': 
    uvicorn.run(app=app, port=8000)