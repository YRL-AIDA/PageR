import os
import shutil
import logging
import uuid
import json 

import uvicorn
from fastapi import FastAPI, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware

from pager import PageModel, PageModelUnit
from pager.page_model.sub_models import PrecisionPDFModel


logger = logging.getLogger(__name__)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все домены (для разработки)
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)

pdf2json = PageModel(page_units=[
    PageModelUnit("pdf", PrecisionPDFModel(), extractors=[], converters={}),
])

@app.post("/")
async def read_pdf(file: UploadFile = File(...),
                   process:str = Form(...)):
    logger.info("start")
    path_dir = os.path.join(os.getcwd(), "tmp_dir", uuid.uuid4().hex)
    os.mkdir(path_dir)
    path_file =  os.path.join(path_dir, "file.pdf")   

    with open(path_file, "wb") as f:
        f.write(file.file.read())
    pdf2json.read_from_file(path_file)
    pdf2json.extract()
    rez = pdf2json.to_dict()
    shutil.rmtree(path_dir)
    return rez

if __name__ == '__main__': 
    
    uvicorn.run(app=app, port=8001)