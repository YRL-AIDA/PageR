import os
import shutil
import logging
import uuid
import json 

import uvicorn
from fastapi import FastAPI, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware

from pager import PageModel, PageModelUnit
from pager import ImageModel, PrecisionPDFModel
from pager import Image2PrecisionPDF


logger = logging.getLogger(__name__)
app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все домены (для разработки)
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)

img2json = PageModel(page_units=[
    PageModelUnit("image", ImageModel(), extractors=[], converters={}),
    PageModelUnit("pdf", PrecisionPDFModel(), extractors=[], converters={"image":Image2PrecisionPDF()}),
])

@app.post("/")
async def read_img(file: UploadFile = File(...),
                   process:str = Form(...)):
    logger.info("start")
    path_dir = os.path.join(os.getcwd(), "tmp_dir", uuid.uuid4().hex)
    os.mkdir(path_dir)
    path_file =  os.path.join(path_dir, "file.png")   

    with open(path_file, "wb") as f:
        f.write(file.file.read())
    img2json.read_from_file(path_file)
    img2json.extract()
    rez = img2json.to_dict()
    logger.info(rez)
    shutil.rmtree(path_dir)
    return rez

if __name__ == '__main__': 
    
    uvicorn.run(app=app, port=8002)