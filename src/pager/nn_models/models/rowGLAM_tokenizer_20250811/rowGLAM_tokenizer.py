from pager.page_model.sub_models.dtype import ImageSegment 
import re
from pager.page_model.sub_models.utils.segment_clusterizer import KMeanClusterizer
from pager.page_model.sub_models.base_sub_model import BaseSubModel, BaseConverter
from typing import List, Dict
import matplotlib.pyplot as plt
from pager.page_model.sub_models.dtype import ImageSegment

import numpy as np
class SpGraph4NModel(BaseSubModel):
    def __init__(self) -> None:
        super().__init__()
        self.A = None
        self.nodes_feature  = None
        self.edges_feature = None
        self.true_edges = None
        self.true_nodes = None

    def from_dict(self, input_model_dict: Dict):
        pass

    def to_dict(self) -> Dict:
        return {"A": self.A.tolist(), "nodes_feature":self.nodes_feature.tolist(), "edges_feature": self.edges_feature.tolist()}

    def read_from_file(self, path_file: str) -> None:
        pass

    def clean_model(self):
        self.A = None
        self.nodes_feature  = None
        self.edges_feature = None

    def show(self):
        def get_color(i):
            if i == -1:
                return "black"
            elif i == 0:
                return "aqua"
            elif i == 1:
                return "gold"
            elif i == 2:
                return "lime"
            elif i == 3:
                return "violet"
            elif i == 4:
                return "teal"
            
        def plot_index(indexs, colors=["b", "b", "r"]):
            i, j = indexs
            #TODO: автоматически подтянуть длину вектора
            xi = self.nodes_feature[i][32]
            yi = self.nodes_feature[i][33]
            xj = self.nodes_feature[j][32]
            yj = self.nodes_feature[j][33]
            plt.scatter(xi, yi, c=colors[0])
            plt.scatter(xj, yj, c=colors[1])
            plt.plot([xi, xj], [yi, yj], colors[2])
        if self.true_edges is None:
            for indexs in zip(self.A[0], self.A[1]):
                plot_index(indexs)
        else:
            for k, indexs in enumerate(zip(self.A[0], self.A[1] )):
                i, j = indexs
                plot_index(indexs, [get_color(self.true_nodes[i]), 
                                    get_color(self.true_nodes[j]), "g" if self.true_edges[k] == 1 else "r"])

class RowToSpGraph4N(BaseConverter):
    def __init__(self, conf=None, add_text=True) -> None:
        super().__init__()
        self.kmean_clusterizer = KMeanClusterizer()
        self.with_text = False
        self.add_text = add_text
        if conf is not None:
            self.with_text = conf["with_text"] if "with_text" in conf.keys() else False
        
    def convert(self, input_model: BaseSubModel, output_model: BaseSubModel)-> None:
        rows = input_model.rows
        segments: List[ImageSegment]  = [r.segment for r in rows]
        graph4n = self.kmean_clusterizer.get_index_neighbors_segment(segments)
        distans = self.kmean_clusterizer.get_distans(graph4n, segments)
        edges_set = set()
        edges = [[], []]
        edges_feature = []
        for i, nodes in enumerate(graph4n):
            for k, j in enumerate(nodes):
                edge = (min(i, j), max(i, j))
                if edge in edges_set:
                    continue
                edges_set.add(edge)
                
                edges[0].append(i)
                edges[1].append(j)
                edges_feature.append([
                    distans[i][k],
                    segments[i].get_angle_center(segments[j]),
                    ])
        output_model.A = np.array(edges)
        #TODO: TEST !!!!

        # if self.add_text:
        #     output_model.nodes_feature = np.array(self.get_vec_words(words, styles, self.with_text))
        #     output_model.edges_feature = np.array(edges_feature)
        # else:
        output_model.nodes_feature = np.array([]) #np.array(self.get_vec_words(words, styles, self.with_text))
        output_model.edges_feature = np.array([]) #np.array(edges_feature)
    
class RowGLAMTokenizer:
    def __call__(self, rows_json):
        A = self.get_A(rows_json)
        node_features = self.get_node_features(rows_json)
        edge_features = self.get_edge_features(A, rows_json)
        json_info =  {
            'A': A,
            'node_features': node_features,
            'edge_features': edge_features
        }
        return self.get_tensor_from_graph(json_info)

    def get_A(self, rows_json):
        from pager import PageModel, PageModelUnit, RowsModel
        r2g_converter=RowToSpGraph4N()
        unit_rows_start = PageModelUnit(id="rows",
                          sub_model=RowsModel(),
                          converters={},
                          extractors=[])
        unit_graph = PageModelUnit(id="graph", 
                            sub_model=SpGraph4NModel(), 
                            extractors=[],  
                            converters={"rows":  r2g_converter})
        rows2graph  = PageModel(page_units=[
            unit_rows_start,
            unit_graph
        ])
        rows2graph.from_dict({
            "rows": rows_json,
        })
        rows2graph.extract()
        graph_json = rows2graph.to_dict()
        return graph_json['A']
    
    def get_node_features(self, rows):
        import numpy as np
        if len(rows) == 0:
            return [[]]
        row_texts = [r['text'] for r in rows]
        dot_vec = np.array([[1.0 if dot in r else 0.0 for dot in (".", ",", ";", ":")] for r in row_texts])
        
        list_ind_vec = np.array([self.get_vec_list(r) for r in row_texts])
        super_vec = np.array([self.get_vec_supper(r) for r in row_texts])
        coord_vec = np.array([self.get_vec_coord(r) for r in rows])
        heuristics_vec = np.array([self.get_vec_heuristics(r) for r in rows])
        nodes_feature = np.concat([coord_vec,  dot_vec, super_vec, list_ind_vec, heuristics_vec], axis=1)
        return nodes_feature.tolist()

    def get_edge_features(self, A, rows):
        edges_featch = []
        for i, j in zip(A[0], A[1]):
            r1 = ImageSegment(dict_2p= rows[i]['segment'])
            r2 = ImageSegment(dict_2p= rows[j]['segment'])
            x1, y1 = r1.get_center()
            x2, y2 = r2.get_center()

            edges_featch.append([r1.get_angle_center(r2), r1.get_min_dist(r2), abs(x1-x2), abs(y1-y2)])
        # print(edges_featch)
        return edges_featch
    
    def get_tensor_from_graph(self, graph):
        import torch
        i = graph["A"]
        v_in = [1 for e in graph["edge_features"]]
        y = graph["edge_features"]
        # for yi in y:
        #     yi[0] = 1.0 if yi[0] > 0.86 else 0.0
        x = graph["node_features"]
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
    
    def get_vec_heuristics(self, row):
        text = row['text']
        text_size = len(text)
        if text_size == 0:
            return [0, 0]
        seg = ImageSegment(dict_2p=row['segment'])
        m = seg.width/seg.height
        digit_count = sum(char.isdigit() for char in text)
        return [text_size/m, digit_count/text_size]

    def get_vec_supper(self, row_text):
        if row_text.isupper():
            return [1, 0]
        elif row_text and row_text[0].isupper():
            return [0, 1]
        else:
            return [0, 0]
        
    def get_vec_list(self, word_text):
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

    def get_vec_coord(self, word):
        seg = ImageSegment(dict_2p=word['segment'])
        return [seg.x_top_left, seg.x_bottom_right, seg.width, seg.y_top_left, seg.y_bottom_right, seg.height]