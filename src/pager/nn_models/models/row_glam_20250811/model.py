
# from ... import PageModel, PageModelUnit, RowToSpGraph4N
# from ..sub_models import RowsModel, PDFModel, SpGraph4NModel, JsonWithFeatchs, BaseExtractor, PhisicalModel
# from ..sub_models.converters import PDF2Rows
# from ..sub_models.dtype import ImageSegment, Word, Row, Graph, Block 
# from ..sub_models.base_sub_model import BaseConverter
# from ..sub_models.utils import merge_segment

# import numpy as np
# from typing import List
# import torch
# import re
# from .torch_model import TorchModel
# from dotenv import load_dotenv



# load_dotenv(override=True)

# # TYPE_GRAPH = "4N"
# EXPERIMENT_PARAMS = {
#     "node_featch": 15,
#     "edge_featch": 4,
#     "epochs": 80,
#     "batch_size": 20,
#     "learning_rate": 0.01,
#     "Tag":[ {'in': -1, 'size': 128, 'out': 128, 'k': 3},
#             {'in': 128, 'size': 64, 'out': 64, 'k': 3},
#             {'in': 64, 'size': 32, 'out': 32, 'k': 3}],
#     "NodeLinear": [-1, 64, 32],
#     "NodeLinearClassifier": [16, 8],
#     "EdgeLinear": [64],
#     "NodeClasses": 5,
#     "batchNormNode": True,
#     "batchNormEdge": True,
#     "seg_k": 0.5,
# }


# unit_pdf = PageModelUnit(id="pdf", 
#                         sub_model=PDFModel({"method": "rows"}), 
#                         converters={}, 
#                         extractors=[])

# unit_rows_end = PageModelUnit(id="rows",
#                           sub_model=RowsModel(),
#                           converters={"pdf":PDF2Rows()},
#                           extractors=[])


# pdf2rows = PageModel(page_units=[ #img2words_and_styles
#     unit_pdf, 
#     unit_rows_end
# ]) 

# unit_rows_start = PageModelUnit(id="rows",
#                           sub_model=RowsModel(),
#                           converters={},
#                           extractors=[])
                           


# r2g_converter=RowToSpGraph4N()
# unit_graph = PageModelUnit(id="graph", 
#                             sub_model=SpGraph4NModel(), 
#                             extractors=[],  
#                             converters={"rows":  r2g_converter})


# rows2graph  = PageModel(page_units=[
#     unit_rows_start,
#     unit_graph
# ])


# def featch_rows(rows):
#     return [
#         rows
#     ]

# def featch_A(rows):
#     rows2graph.from_dict({
#         "rows": rows,
#     })
#     rows2graph.extract()
#     graph_json = rows2graph.to_dict()
#     return [
#         graph_json['A']
#     ]

# def nodes_feature(rows):
#     if len(rows) == 0:
#         return [[]]
#     row_texts = [r['text'] for r in rows]
#     dot_vec = np.array([[1.0 if dot in r else 0.0 for dot in (".", ",", ";", ":")] for r in row_texts])
    
#     list_ind_vec = np.array([get_vec_list(r) for r in row_texts])
#     super_vec = np.array([get_vec_supper(r) for r in row_texts])
#     coord_vec = np.array([get_vec_coord(r) for r in rows])
#     heuristics_vec = np.array([get_vec_heuristics(r) for r in rows])
#     nodes_feature = np.concat([coord_vec,  dot_vec, super_vec, list_ind_vec, heuristics_vec], axis=1)
#     return [nodes_feature.tolist()]

# def get_vec_heuristics(row):
#     text = row['text']
#     text_size = len(text)
#     if text_size == 0:
#         return [0, 0]
#     seg = ImageSegment(dict_2p=row['segment'])
#     m = seg.width/seg.height
#     digit_count = sum(char.isdigit() for char in text)
#     return [text_size/m, digit_count/text_size]

# def get_vec_supper(row_text):
#     if row_text.isupper():
#         return [1, 0]
#     elif row_text and row_text[0].isupper():
#         return [0, 1]
#     else:
#         return [0, 0]
    
# def get_vec_list(word_text):
#     patterns = [
#             r'\b(\d+[.)])\s+',  # 1) 2. 15)
#             r'\b([a-zA-Z][.)])\s+',  # a) B.
#             r'\b([IVXLCDM]+[.)])\s+',  # XIX. VII)
#             r'\[\d+\]',  # [5]
#             r'\(\d+\)',  # (3)
#             r'(?:^|\s)([•▪▫○◆▶➢✓-])\s+',  # Спецсимволы: • Item, ▪ Subitem
#             r'\*{1,}\s+',  # Звездочки: **
#             r'\b\d+\.\d+\b',  # Многоуровневые: 1.1, 2.3.4
#             r'\b\d+-\w+\)',  # Комбинированные: 1-a), 5-b.
#             r'\b(?:Item|Пункт)\s+\d+:\s+',  # Явные указатели: Item 5:
#             r'(?:^|\s)\u2022\s+',  # Юникод-символы: •
#             r'\[[A-Z]\]',  # Буквы в скобках: [A]
#             r'\b\d{2,}\.\s+',  # Номера с ведущими нулями: 01.
#             r'#\d+\b',  # Хештег-нумерация: #5
#             r'\b\d+\s*[-–—]\s+',  # Тире-разделители: 5 -
#             r'\b\d+/\w+\b',  # Слэш-нумерация: 1/a
#             r'<\d+>',  # Угловые скобки: <3>
#             r'\b[A-Z]\d+\)',  # Буква+число: A1)
#             r'\b(?:Step|Шаг)\s+\d+\b',  # Шаги: Step 3
#             r'\d+[.)]\s*-\s+',  # Комбинированные с тире: 1). -
#             r'\b[А-Яа-я]\s*[).]\s+',  # а) б. кириллица
#             r'\b\d+[.:]\d+\)',  # 1:2) вложенность
#             r'\d+\s*→\s+',  # 1 → со стрелкой
#             r'\b\d+\.?[a-z]\b',  # Буквенные подуровни: 1a
#             r'\b[A-Z]+-\d+\b'  # Код-номера: ABC-123
#         ]
#     flag = False
#     for pattern in patterns:
#         if bool(re.search(pattern, word_text, flags=re.IGNORECASE)):
#             flag = True
#             break
#     list_mark = 1 if flag else 0
#     return [list_mark]

# def get_vec_coord(word):
#     seg = ImageSegment(dict_2p=word['segment'])
#     return [seg.x_top_left, seg.x_bottom_right, seg.width, seg.y_top_left, seg.y_bottom_right, seg.height]


# def nodes_feature_new_styles(nodes_feature):
#     new_feature = np.copy(nodes_feature)[:, :-512]
#     return [new_feature.tolist(), nodes_feature]

# def edges_feature(A, rows):
#     edges_featch = []
#     for i, j in zip(A[0], A[1]):
#         r1 = ImageSegment(dict_2p= rows[i]['segment'])
#         r2 = ImageSegment(dict_2p= rows[j]['segment'])
#         x1, y1 = r1.get_center()
#         x2, y2 = r2.get_center()

#         edges_featch.append([r1.get_angle_center(r2), r1.get_min_dist(r2), abs(x1-x2), abs(y1-y2)])
#     # print(edges_featch)
#     return [edges_featch]
   

# class JsonWithFeatchsExtractor(BaseExtractor):
#     def extract(self, json_with_featchs: JsonWithFeatchs):
#         json_with_featchs.add_featchs(lambda: featch_rows(json_with_featchs.rows), names=['rows'], 
#                                 is_reupdate=False, rewrite=False)
#         json_with_featchs.add_featchs(lambda: featch_A(json_with_featchs.json['rows']), names=['A'], 
#                             is_reupdate=False, rewrite=False)
        
#         json_with_featchs.add_featchs(lambda: nodes_feature(json_with_featchs.json['rows']), names=['nodes_feature'], 
#                             is_reupdate=False, rewrite=False) 
        
#         json_with_featchs.add_featchs(lambda: edges_feature(json_with_featchs.json['A'], json_with_featchs.json['rows']), names=['edges_feature'], 
#                             is_reupdate=False, rewrite=False) 
        
        

# class JsonWithFeatchsWithRead(JsonWithFeatchs):
#     def read_from_file(self, path_file):
#         self.name_file = path_file
#         return super().from_dict({})


# class Rows2JsonConverter(BaseConverter):
#     def convert(self, input_model:RowsModel, output_model:JsonWithFeatchs):
#         dict_rows = input_model.to_dict()
#         output_model.rows = dict_rows["rows"]


# def get_tensor_from_graph(graph):
#     i = graph["A"]
#     v_in = [1 for e in graph["edges_feature"]]
#     y = graph["edges_feature"]
#     # for yi in y:
#     #     yi[0] = 1.0 if yi[0] > 0.86 else 0.0
#     x = graph["nodes_feature"]
#     N = len(x)
    
#     X = torch.tensor(data=x, dtype=torch.float32)
#     Y = torch.tensor(data=y, dtype=torch.float32)
#     sp_A = torch.sparse_coo_tensor(indices=i, values=v_in, size=(N, N), dtype=torch.float32)
    
#     return {
#         "N": N,
#         "X": X,
#         "Y": Y,
#         "sp_A": sp_A,
#         "inds": i
#     }





# class Json2Blocks(BaseConverter):
#     def __init__(self, conf):
#         self.seg_k = conf['seg_k'] if "seg_k" in conf.keys() else 0.5
#         self.spgraph = SpGraph4NModel()
#         self.graph_converter = RowToSpGraph4N()
        
#         self.name_class = ["figure", "text", "header", "list", "table"]
#         self.model = TorchModel(conf)
#         self.model.load_state_dict(torch.load(conf['path_model'], weights_only=True, map_location=torch.device('cpu')))
    
#     def convert(self, input_model: JsonWithFeatchs, output_model: PhisicalModel):
#         graph = {
#             "A": input_model.json["A"], 
#             "nodes_feature": input_model.json["nodes_feature"], 
#             "edges_feature": input_model.json["edges_feature"]
#         } 
#         rows = [Row(r) for r in input_model.json["rows"]]
#         self.set_output_block(output_model, rows, graph)
#         for block in output_model.blocks:
#             block.words = [Word(row.to_dict()) for row in  block.rows]
    
    
#     def set_output_block(self, output_model, rows, graph):
#         # SEGMENTER ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#         edges_ind = self.segmenter(graph)
#         relating_graph = Graph()
#         for row in rows:
#             x, y = row.segment.get_center()
#             relating_graph.add_node(x, y)
        
#         for n1, n2, ind in zip(graph['A'][0], graph['A'][1], edges_ind):
#             if ind == 1:
#                 relating_graph.add_edge(n1+1, n2+1)

#         for r in relating_graph.get_related_graphs():
#             rows_r = [rows[n.index-1] for n in r.get_nodes()]
#             segment = ImageSegment(0, 0, 1, 1)
#             segment.set_segment_max_segments([row.segment for row in rows_r])
#             block = Block(segment.get_segment_2p())
            
#             #TODO: Решить проблему с типами в блоке
#             rows_ = [row.to_dict()['segment'] for row in rows_r]
#             for row_, row in zip(rows_, rows_r):
#                 row_["text"] = row.content
#             # #TODO: Нужно сделать, чтоб перебирались все варианты, пока ни разу не зайдет
#             # skip = False
#             # for old_block in output_model.blocks:
#             #     if old_block.segment.is_intersection(block.segment):
#             #         old_block.segment.set_segment_max_segments([old_block.segment, block.segment])
#             #         old_block.words += [Word(w) for w in words_]
#             #         old_block.sort_words()
#             #         skip = True
#             # if skip:
#             #     continue
#             block.set_rows_from_dict(rows_)
            
#             output_model.blocks.append(block)
#         if len(output_model.blocks) == 0:
#             return 
        
#         index_blocks = merge_segment([block.segment for block in output_model.blocks])
#         count_block = max(index_blocks)+1
#         new_blocks = []
#         for i in range(count_block):
#             segment = ImageSegment(0, 0, 1, 1)
#             blocks = [output_model.blocks[k] for k, j in enumerate(index_blocks) if i==j]
#             segment.set_segment_max_segments([b.segment for b in blocks])
#             block = Block(segment.get_segment_2p())
#             block.rows = [r for b in blocks for r in b.rows]
#             block.sort_words()
#             new_blocks.append(block)
#         output_model.blocks = new_blocks
#         self.set_label_output_block(output_model, rows, graph)
    
    
#     def segmenter(self, graph) -> List[int]:
#         data_graph_dict = get_tensor_from_graph(graph)
#         N = data_graph_dict["N"]
#         i = data_graph_dict["inds"]

#         if len(i[0]) == 0:
#             self.tmp = np.array([[0.0, 1.0, 0.0, 0.0, 0.0] for _ in range(N)])
#             return np.array([])
#         if N == 1:
#             self.tmp = np.array([[0.0, 1.0, 0.0, 0.0, 0.0]])
#             return np.array([0 for _ in i[0]])
#         pred_graph_dict = self.model(data_graph_dict)
#         self.tmp_edge = pred_graph_dict["E_pred"].detach().numpy()
#         rez = np.zeros_like(self.tmp_edge)
#         self.tmp = pred_graph_dict["node_classes"].detach().numpy()
#         rez[self.tmp_edge>0.5] = 1
#         return rez    

#     def set_label_output_block(self, output_model, rows, graph):
#         # CLASSIFIER +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#         for block in output_model.blocks:
#             block_nodes = []
#             for i, row in enumerate(rows):
#                 if block.segment.is_intersection(row.segment):
#                     block_nodes.append(self.tmp[i])
#             block.tmp = np.array(block_nodes)
#             class_ = int(np.argmax(np.array(block_nodes).mean(axis=0)))
#             label = self.name_class[class_]
#             block.set_label(label)

    

# def get_img2phis(conf):
#     conf['sigmoidEdge'] = True
#     json_model = PageModelUnit(id="json_model", 
#                         sub_model=JsonWithFeatchsWithRead(), 
#                         extractors=[JsonWithFeatchsExtractor()],
#                         converters={"rows": Rows2JsonConverter()})

#     unit_phis = PageModelUnit(id="phisical_model", 
#                         sub_model=PhisicalModel(), 
#                         extractors=[], 
#                         converters={"json_model": Json2Blocks(conf=conf), 
#                                     # "pdf": PDF2OnlyFigBlocks()
#                                     })
#     return PageModel(page_units=[
#         json_model,
#         # unit_pdf,
#         unit_phis
#     ])

# def get_final_model(conf):
#     EXPERIMENT_PARAMS["path_model"] = conf["ROW_GLAM"]
#     return get_img2phis(EXPERIMENT_PARAMS)