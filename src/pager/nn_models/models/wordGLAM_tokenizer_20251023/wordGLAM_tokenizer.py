from pager.page_model.sub_models.phisical_model.segment_clusterizer import KMeanClusterizer
from pager.page_model.sub_models.dtype import ImageSegment
import numpy as np
import torch
import re

class WordGLAMTokenizer:
    def __init__(self):
        self.clusterizer = KMeanClusterizer()
        
    def __call__(self, words_json):
        A = self.get_A(words_json)
        node_features = self.get_node_features(words_json)
        edge_features = self.get_edge_features(A, words_json)
        json_info =  {
            'A': A,
            'node_features': node_features,
            'edge_features': edge_features
        }
        return self.get_tensor_from_graph(json_info)

    def get_A(self, words_json):
        
        neigbors = self.clusterizer.get_index_neighbors_segment([ImageSegment(dict_2p=word_json['segment']) for word_json in words_json])
        A = []
        for i, nodes in enumerate(neigbors):
            for j in nodes:
                if i == j:
                    continue
                A.append((min([i, j]), max([i, j])))
        A1, A2 = [],[]
        
        for a1, a2 in set(A):
            A1.append(a1)
            A2.append(a2)
        index = np.argsort(A1)
        A1_ = [A1[i] for i in index]
        A2_ = [A2[i] for i in index]
    
        return [A1_, A2_]
    
    def get_node_features(self, words_json):
        if len(words_json) == 0:
            return [[]]
        word_texts = [w['text'] for w in words_json]
        dot_vec = np.array([[1.0 if dot in r else 0.0 for dot in (".", ",", ";", ":")] for r in word_texts])
        
        list_ind_vec = np.array([self.get_vec_list(w) for w in word_texts])
        super_vec = np.array([self.get_vec_supper(w) for w in word_texts])
        coord_vec = np.array([self.get_vec_coord(w_json) for w_json in words_json])
        heuristics_vec = np.array([self.get_vec_heuristics(w_json) for w_json in words_json])
        nodes_feature = np.concat([coord_vec,  dot_vec, super_vec, list_ind_vec, heuristics_vec], axis=1)
        return nodes_feature.tolist()

    def get_edge_features(self, A, words_json):
        edges_featch = []
        for i, j in zip(A[0], A[1]):
            r1 = ImageSegment(dict_2p= words_json[i]['segment'])
            r2 = ImageSegment(dict_2p= words_json[j]['segment'])
            x1, y1 = r1.get_center()
            x2, y2 = r2.get_center()

            edges_featch.append([r1.get_angle_center(r2), r1.get_min_dist(r2), abs(x1-x2), abs(y1-y2)])
        # print(edges_featch)
        return edges_featch
    
    def get_tensor_from_graph(self, graph):
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