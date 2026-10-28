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
from pagerlib.extractors.page_extractor import Rows2Regions , Words2Rows, MergeRegion, PDFIMGExtractor, Images2RegionsExtractor
from pagerlib.file_input import FileInput
from pathlib import Path

from PIL import Image
from io import BytesIO
import base64
import numpy as np
from urllib.parse import quote
from pager.pager_pipe_line.json2docx import PDF2MSWord

file_inpit = FileInput()
words2rows = Words2Rows()
img2region = Images2RegionsExtractor()
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

            if reg['label'] in  ('figure', 'image', 'table'):
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
    pdf2img.extract(pagerdf)
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
    pagerdf.data['path'] = path
    is_image = path.suffix.lower() in ('.png', '.jpg', '.jpeg')
    if "only_text" in params and params["only_text"]:
        return pagerdf2json(pagerdf)

    if is_image:
        # pagerlib reads images differently from PDFs: the first (and only)
        # child of a page is the page raster itself. Save a reference to it
        # before OCR replaces the children with regions, then restore the
        # raster at the front so rows2regions/pagerdf2json see the same layout
        # as for PDFs (page raster at children[0], regions after it).
        page = pagerdf.data['pages'][0]
        page_img = page.children[0]
        img2region.extract(pagerdf)   # OCR page raster -> text regions
        words2rows.extract(pagerdf)   # cluster words into rows
        page.children = [page_img] + page.children
    elif "glam_words" in params and params["glam_words"]:
        words2rows.extract(pagerdf)

    if not is_image:
        pdf2img.extract(pagerdf)
    
    if not "glam_rows" in params or params["glam_rows"]:
        rows2regions.extract(pagerdf)
        if is_image:
            page.children = [page_img] + page.children
        else:
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

class JsonTask(BaseModel):
    precisionPDF_json: str
    name_save: str


def _prepare_json2docx(json_task: dict) -> None:
    """Доводит JSON (вывод / или /precision-pdf/) до формата, который ожидает
    конвертер MinerPDFToMSWord: у каждого region должен быть 'label' из
    известного набора и непустой 'text'."""
    known_labels = {"text", "header", "list", "table", "other", "figure"}
    for page in json_task.get("pages", []):
        regions = page.get("regions", [])
        for region in regions:
            label = region.get("label", "text")
            if label in ("figure", "image"):
                region["label"] = "figure"
            else:
                region["label"] = label if label in known_labels else "text"

            text = region.get("text")
            if text is not None and str(text).strip():
                continue
            parts = []
            for row in region.get("rows", []):
                row_text = row.get("text")
                if row_text is not None and str(row_text).strip():
                    parts.append(str(row_text).strip())
                    continue
                words = [w.get("text", "") for w in row.get("words", [])]
                parts.append(" ".join(str(w) for w in words if str(w).strip()))
            region["text"] = " ".join(p for p in parts if p).strip()
        page["regions"] = [r for r in regions if str(r["text"]).strip() or r.get("base64")]


@app.post("/json2word")
async def convert_json_to_docx(task: JsonTask):
    logger.info("start")

    json_task = json.loads(task.precisionPDF_json)
    _prepare_json2docx(json_task)

    json2docx = PDF2MSWord()
    json2docx.from_dict(json_task)
    json2docx.extract()

    path_dir = os.path.join(os.getcwd(), "tmp_dir", uuid.uuid4().hex)
    os.mkdir(path_dir)
    path = os.path.join(path_dir, "file.docx")
    json2docx.save_doc(path)

    with open(path, "rb") as f:
        file = f.read()

    shutil.rmtree(path_dir)

    filename = task.name_save.replace('"', "").strip() or "file.docx"
    ascii_filename = filename.encode("ascii", "ignore").decode("ascii").strip()
    ascii_stem = ascii_filename.rsplit(".", 1)[0] if "." in ascii_filename else ascii_filename
    if not any(c.isalnum() for c in ascii_stem):
        ascii_filename = "file.docx"
    content_disposition = (
        f'attachment; filename="{ascii_filename}"; '
        f"filename*=UTF-8''{quote(filename)}"
    )
    return Response(
        content=file,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": content_disposition},
    )

    

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