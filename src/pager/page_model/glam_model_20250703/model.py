"""
обязательно нужно реализовать 
img2words_and_styles
words_and_styles2graph
get_img2phis
"""

from ...page_model import PageModel, PageModelUnit
from ...page_model.sub_models import ImageModel, PDFModel, WordsAndStylesModel, SpGraph4NModel, JsonWithFeatchs, BaseExtractor, BaseConverter
from ...page_model.sub_models.converters import Image2WordsAndStyles, PDF2WordsAndStyles
from ...page_model.sub_models import PhisicalModel, WordsAndStylesToGLAMBlocks,WordsAndStylesToSpGraph4N
from ..sub_models import WordsAndStylesModel, SpGraph4NModel, WordsAndStylesToSpGraph4N, WordsAndStylesToSpDelaunayGraph
from ..sub_models.dtype import ImageSegment, Word
from ..sub_models.phisical_model import TrianglesSortBlock

from ..sub_models.base_sub_model import AddArgsFromModelExtractor
from ..sub_models.extractors import TableExtractor

# from ..sub_models.converters import PDF2Img, PDF2OnlyFigBlocks
import numpy as np
import os
from typing import List
import torch
import re
from .torch_model import TorchModel
from dotenv import load_dotenv
load_dotenv(override=True)

PATH_STYLE_MODEL = os.environ["PATH_STYLE_MODEL"]

WITH_TEXT = True
TYPE_GRAPH = "4N"
EXPERIMENT_PARAMS = {
    "node_featch": 47,
    "edge_featch": 2,
    "epochs": 30,
    "batch_size": 80,
    "learning_rate": 0.005,
    "Tag": [{'in': -1, 'size': 64, 'out': 64, 'k': 3},
             {'in': 64, 'size': 16, 'out': 16, 'k': 3}],
    "NodeLinear": [-1, 16, 8],
    "EdgeLinear": [8],
    "NodeClasses": 5,
    "batchNormNode": True,
    "batchNormEdge": True,
    "seg_k": 0.5,
}

def featch_words_and_styles(words, styles):
    return [
        styles,
        words
    ]
    
def featch_A(styles,words):
    words_and_styles2graph.from_dict({
        "words": words,
        "styles": styles
    })
    words_and_styles2graph.extract()
    graph_json = words_and_styles2graph.to_dict()
    return [
        graph_json['A']
    ]

def nodes_feature(styles, words):
    if len(words) == 0:
        return [[]]
    fonts = dict()
    for st in styles:
        fonts[st['id']] = st['font2vec']
    style_vec = np.array([fonts[w['style_id']] for w in words])
    word_texts = [w['text'] for w in words]
    text_vec = ws2g_converter.word2vec(word_texts)
    dot_vec = np.array([[1.0 if dot in w else 0.0 for dot in (".", ",", ";", ":")] for w in word_texts])
    key_vec = np.array([get_vec_key(w) for w in word_texts])
    list_ind_vec = np.array([get_vec_list(w) for w in word_texts])
    coord_vec = np.array([get_vec_coord(w) for w in words])
    nodes_feature = np.concat([coord_vec, style_vec, dot_vec, key_vec, list_ind_vec, text_vec], axis=1)
    return [nodes_feature.tolist()]

def get_vec_key(word_text):
    keywords = {
            # Класс 0: Текст / Text
            "text": 0, "основнойтекст": 0, "paragraph": 0, "content": 0,
            "body": 0, "описание": 0, "описательныйблок": 0, "описательныйтекст": 0,
            "описательнаячасть": 0, "description": 0, "простойтекст": 0,
            "текстовыйблок": 0, "контент": 0, "абзац": 0, "narrative": 0,
            "txt": 0, "оснтекст": 0, "para": 0, "par": 0, "cont": 0,
            "опис": 0, "desc": 0, "prose": 0, "nar": 0, "narr": 0,

            # Класс 1: Заголовок / Heading
            "title": 1, "header": 1, "заголовок": 1, "heading": 1,
            "subtitle": 1, "подзаголовок": 1, "section": 1, "раздел": 1,
            "chapter": 1, "глава": 1, "subheader": 1, "название": 1,
            "заголовок раздела": 1, "topic": 1, "h1": 1, "h2": 1,
            "h3": 1, "h4": 1, "h5": 1, "h6": 1, "hdr": 1, "head": 1,
            "titl": 1, "загл": 1, "подзагл": 1, "subhdr": 1, "sect": 1,
            "гл": 1, "разд": 1, "subttl": 1, "hdg": 1, "ttl": 1, "subhd": 1,

            # Класс 2: Список / List
            "list": 2, "список": 2, "bullet points": 2, "маркированныйсписок": 2,
            "numberedlist": 2, "нумерованныйсписок": 2, "items": 2,
            "элементысписка": 2, "перечисление": 2, "enumeration": 2,
            "checklist": 2, "check boxes": 2, "unorderedlist": 2,
            "orderedlist": 2, "перечень": 2, "пункты": 2, "lst": 2, "ul": 2,
            "ol": 2, "bul": 2, "numlst": 2, "марксписок": 2, "enum": 2,
            "chklst": 2, "пункт": 2, "item": 2, "elements": 2, "точки": 2,
            "bull": 2, "спис": 2, "lis": 2, "chkbox": 2,

            # Класс 3: Таблица / Table
            "table": 3, "таблица": 3, "spreadsheet": 3, "datatable": 3,
            "grid": 3, "матрица": 3, "сетка": 3, "tabular data": 3,
            "excel-like": 3, "pivot table": 3, "columns": 3, "столбцы": 3,
            "rows": 3, "строки": 3, "ячейки": 3, "cells": 3, "tbl": 3,
            "табл": 3, "col": 3, "row": 3, "cell": 3, "datatbl": 3,
            "pivot": 3, "столб": 3, "строка": 3, "colrow": 3, "excel": 3,
            "matrix": 3, "таблданные": 3, "colhd": 3, "tblstruct": 3,

            # Класс 4: Изображение / Figure
            "figure": 4, "fig": 4, "image": 4, "изображение": 4,
            "picture": 4, "рисунок": 4, "photo": 4, "фото": 4,
            "illustration": 4, "иллюстрация": 4, "графика": 4,
            "graphic": 4, "diagram": 4, "диаграмма": 4, "chart": 4,
            "график": 4, "screenshot": 4, "скриншот": 4, "visual": 4,
            "drawing": 4, "чертеж": 4, "schema": 4, "схема": 4,
            "img": 4, "pic": 4, "рис": 4, "илл": 4, "fgr": 4,
            "diagr": 4, "graph": 4, "скрин": 4, "scrnsht": 4,
            "схм": 4, "draw": 4, "figs": 4, "imgs": 4,
            "photos": 4, "граф": 4, "vis": 4, "thumb": 4, "preview": 4
        }
    content = word_text.strip().lower().rstrip('.,;!?')
    key_word_mark = keywords[content] if content in keywords else -1
    return [key_word_mark]

def get_vec_list(word_text):
    patterns = [
            r'\b(\d+[.)])\s+',  # 1) 2. 15)
            r'\b([a-zA-Z][.)])\s+',  # a) B.
            r'\b([IVXLCDM]+[.)])\s+',  # XIX. VII)
            r'\[\d+\]',  # [5]
            r'\(\d+\)',  # (3)
            r'(?:^|\s)([•▪▫○◆▶➢✓-])\s+',  # Спецсимволы: • Item, ▪ Subitem
            r'\*{1,}\s+',  # Звездочки: **
            r'\b\d+\.\d+\b',  # Многоуровневые: 1.1, 2.3.4
            r'\b\d+-\w+\)',  # Комбинированные: 1-a), 5-b.
            r'\b(?:Item|Пункт)\s+\d+:\s+',  # Явные указатели: Item 5:
            r'(?:^|\s)\u2022\s+',  # Юникод-символы: •
            r'\[[A-Z]\]',  # Буквы в скобках: [A]
            r'\b\d{2,}\.\s+',  # Номера с ведущими нулями: 01.
            r'#\d+\b',  # Хештег-нумерация: #5
            r'\b\d+\s*[-–—]\s+',  # Тире-разделители: 5 -
            r'\b\d+/\w+\b',  # Слэш-нумерация: 1/a
            r'<\d+>',  # Угловые скобки: <3>
            r'\b[A-Z]\d+\)',  # Буква+число: A1)
            r'\b(?:Step|Шаг)\s+\d+\b',  # Шаги: Step 3
            r'\d+[.)]\s*-\s+',  # Комбинированные с тире: 1). -
            r'\b[А-Яа-я]\s*[).]\s+',  # а) б. кириллица
            r'\b\d+[.:]\d+\)',  # 1:2) вложенность
            r'\d+\s*→\s+',  # 1 → со стрелкой
            r'\b\d+\.?[a-z]\b',  # Буквенные подуровни: 1a
            r'\b[A-Z]+-\d+\b'  # Код-номера: ABC-123
        ]
    flag = False
    for pattern in patterns:
        if bool(re.search(pattern, word_text, flags=re.IGNORECASE)):
            flag = True
            break
    list_mark = 1 if flag else 0
    return [list_mark]

def get_vec_coord(word):
    seg = ImageSegment(dict_2p=word['segment'])
    return [seg.x_top_left, seg.x_bottom_right, seg.width, seg.y_top_left, seg.y_bottom_right, seg.height]


def nodes_feature_new_styles(styles, words, nodes_feature):
    # fonts = dict()
    # for st in styles:
    #     fonts[st['id']] = st['font2vec']
    # style_vec = np.array([fonts[w['style_id']] for w in words])
    word_texts = [w['text'] for w in words]
    dot_vec = np.array([[1.0 if dot in w else 0.0 for dot in (".", ",", ";", ":")] for w in word_texts])
    key_vec = np.array([get_vec_key(w) for w in word_texts])
    list_ind_vec = np.array([get_vec_list(w) for w in word_texts])
    # print(words[0])
    coord_vec = np.array([get_vec_coord(w) for w in words])
    rez = np.array(nodes_feature)
    # ------------------------------------v style_vec
    nodes_feature = np.concat([coord_vec, rez[:, :-32], dot_vec, key_vec, list_ind_vec, rez[:, -32:]], axis=1)
    return [nodes_feature.tolist()]

def edges_feature(A, words):
    edges_featch = []
    for i, j in zip(A[0], A[1]):
        w1 = ImageSegment(dict_2p= words[i]['segment'])
        w2 = ImageSegment(dict_2p= words[j]['segment'])
        edges_featch.append([w1.get_angle_center(w2), w1.get_min_dist(w2)])
    # print(edges_featch)
    return [edges_featch]
      



# unit_pdf = PageModelUnit(id="pdf", 
#                                sub_model=PDFModel(), 
#                                converters={}, 
#                                extractors=[])                            

unit_words_and_styles_start = PageModelUnit(id="words_and_styles", 
                            sub_model=WordsAndStylesModel(), 
                            converters={}, 
                            extractors=[])
conf_graph = {"with_text": True} if WITH_TEXT else None
ws2g_converter=WordsAndStylesToSpDelaunayGraph(conf_graph, add_text=False) if TYPE_GRAPH == "Delaunay" else WordsAndStylesToSpGraph4N(conf_graph, add_text=False)
unit_graph = PageModelUnit(id="graph", 
                            sub_model=SpGraph4NModel(), 
                            extractors=[],  
                            converters={"words_and_styles":  ws2g_converter})

words_and_styles2graph = PageModel(page_units=[
    unit_words_and_styles_start,
    unit_graph
])

json_with_featchs = JsonWithFeatchs()

class JsonWithFeatchsExtractor(BaseExtractor):
    def extract(self, json_with_featchs: JsonWithFeatchs):
        json_with_featchs.add_featchs(lambda: featch_words_and_styles(json_with_featchs.words, json_with_featchs.styles), names=['styles', 'words'], 
                            is_reupdate=False, rewrite=False)
        
        json_with_featchs.add_featchs(lambda: featch_A(json_with_featchs.json['styles'], json_with_featchs.json['words']), names=['A'], 
                            is_reupdate=False, rewrite=False)
        
        json_with_featchs.add_featchs(lambda: nodes_feature(json_with_featchs.json['styles'], json_with_featchs.json['words']), names=['nodes_feature'], 
                            is_reupdate=False, rewrite=False) 
        
        json_with_featchs.add_featchs(lambda: edges_feature(json_with_featchs.json['A'], json_with_featchs.json['words']), names=['edges_feature'], 
                            is_reupdate=False, rewrite=False) 

class JsonWithFeatchsWithRead(JsonWithFeatchs):
    def read_from_file(self, path_file):
        self.name_file = path_file
        return super().from_dict({})
    

class WS2JsonConverter(BaseConverter):
    def convert(self, input_model:WordsAndStylesModel, output_model:JsonWithFeatchs):
        dict_ws = input_model.to_dict(is_vec=True)
        output_model.words = dict_ws["words"]
        output_model.styles = dict_ws["styles"]

def get_tensor_from_graph(graph):
    i = graph["A"]
    v_in = [1 for e in graph["edges_feature"]]
    y = graph["edges_feature"]
    x = graph["nodes_feature"]
    N = len(x)
    
    X = torch.tensor(data=x, dtype=torch.float32)
    Y = torch.tensor(data=y, dtype=torch.float32)
    sp_A = torch.sparse_coo_tensor(indices=i, values=v_in, size=(N, N), dtype=torch.float32)
    return {
        "N": N,
        "X": X,
        "Y": Y,
        "sp_A": sp_A,
        "inds": i
    }
class Json2Blocks(WordsAndStylesToGLAMBlocks):
    def __init__(self, conf):
        self.seg_k = conf['seg_k'] if "seg_k" in conf.keys() else 0.5
        self.spgraph = SpGraph4NModel()
        self.graph_converter = WordsAndStylesToSpGraph4N({"with_text": True})
        
        self.name_class = ["figure", "text", "header", "list", "table"]
        self.model = TorchModel(conf)
        self.model.load_state_dict(torch.load(conf['path_model'], weights_only=True, map_location=torch.device('cpu')))
    
    def segmenter(self, graph) -> List[int]:
        data_graph_dict = get_tensor_from_graph(graph)
        N = data_graph_dict["N"]
        i = data_graph_dict["inds"]

        if len(i[0]) == 0:
            self.tmp = np.array([[0.0, 1.0, 0.0, 0.0, 0.0] for _ in range(N)])
            return np.array([])
        if N == 1:
            self.tmp = np.array([[0.0, 1.0, 0.0, 0.0, 0.0]])
            return np.array([0 for _ in i[0]])
        pred_graph_dict = self.model(data_graph_dict)
        self.tmp_edge = pred_graph_dict["E_pred"].detach().numpy()
        rez = np.zeros_like(self.tmp_edge)
        self.tmp = pred_graph_dict["node_classes"].detach().numpy()
        rez[self.tmp_edge>0.5] = 1
        return rez

    def convert(self, input_model: JsonWithFeatchs, output_model: PhisicalModel):
        graph = {
            "A": input_model.json["A"], 
            "nodes_feature": input_model.json["nodes_feature"], 
            "edges_feature": input_model.json["edges_feature"]
        } 
        words = [Word(w) for w in input_model.json["words"]]
        self.set_output_block(output_model, words, graph)

def get_img2phis(conf):
    conf['sigmoidEdge'] = True
    img_model = ImageModel()
    conf_words_and_styles = {"path_model": PATH_STYLE_MODEL,"lang": "eng+rus", "psm": 4, "oem": 3,"onetone_delete": True, "k": 4 }
    
    unit_image = PageModelUnit(id="image", 
                               sub_model=img_model, 
                               converters={}, 
                               extractors=[])
    unit_ws = PageModelUnit(id="words_and_styles", 
                            sub_model=WordsAndStylesModel(), 
                            converters={"image": Image2WordsAndStyles(conf_words_and_styles)}, 
                            extractors=[])

    json_model = PageModelUnit(id="json_model", 
                        sub_model=JsonWithFeatchs(), 
                        extractors=[JsonWithFeatchsExtractor()],
                        converters={"words_and_styles": WS2JsonConverter()})


    unit_phis = PageModelUnit(id="phisical_model", 
                        sub_model=PhisicalModel(), 
                        extractors=[TrianglesSortBlock(),], 
                        converters={"json_model": Json2Blocks(conf=conf)})
    return PageModel(page_units=[
        unit_image,
        unit_ws,
        json_model,
        unit_phis
    ])

def get_final_model(conf):
    EXPERIMENT_PARAMS["path_model"] = conf["GLAM_MODEL"]
    return get_img2phis(EXPERIMENT_PARAMS)
