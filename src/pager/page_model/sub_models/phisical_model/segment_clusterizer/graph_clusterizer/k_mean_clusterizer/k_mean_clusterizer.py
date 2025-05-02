from ..base_graph_clusterizer import *

from pager.page_model.sub_models.dtype import ImageSegment
from pager.page_model.sub_models.dtype  import Graph
import numpy as np
from typing import Dict, List

class KMeanClusterizer(BaseSegmentClusterizer):
    def cluster(self, segments: List[ImageSegment], conf: Dict={}) -> List[ImageSegment]:
        if len(segments) == 0:
            return []
        elif len(segments) == 1:
            segment = ImageSegment(dict_2p=segments[0].get_segment_2p())
            return [segment]

        neighbors = self.get_index_neighbors_segment(segments)
        distans = self.get_distans(neighbors, segments)
        
        dist_word, dist_row = self.get_standart_distant(distans)
        if "dist_row" in conf.keys():
            if conf["dist_row"] != "auto":
                dist_row = conf["dist_row"]
        if "dist_word" in conf.keys(): 
            if conf["dist_word"] != "auto":
                dist_word = conf["dist_word"]

        
        graph = self.get_graph_segments(segments, neighbors, dist_word, dist_row, distans)

        parent_segments = []
        for r in graph.get_related_graphs():
            seg = ImageSegment(0, 0, 1, 1)
            segment_r = [segments[n.index-1] for n in r.get_nodes()]
            seg.set_segment_max_segments(segment_r)
            parent_segments.append(seg)

        join_intersect_parent_segments = self.join_intersect_segments(parent_segments)

        # if "join_blocks" in history.keys():
        #     history["join_blocks"] = join_intersect_block
        # if "neighbors" in history.keys():
        #     history["neighbors"] = neighbors
        # if "distans" in history.keys():
        #     history["distans"] = distans
        # if "dist_word" in history.keys():
        #     history["dist_word"] = dist_word
        # if "dist_row" in history.keys():
        #     history["dist_row"] = dist_row
        # if "graph" in history.keys():
        #     history["graph"] = graph
        # if "no_join_blocks" in history.keys():
        #     history["no_join_blocks"] = list_block
        return join_intersect_parent_segments

    def get_index_neighbors_segment(self, segments, max_level=8):
        if len(segments) == 1:
            return [[0,0,0,0]]
        if len(segments) == 0:
            return []
        hash_matrix, fun_hashkey = self.get_hash_matrix(segments)
        neighbors = []
        for k in range(len(segments)):
            top_right_bottom_left = [k, k, k, k]
            for i, vec in enumerate(["top", "right", "bottom", "left"]):
                top_right_bottom_left[i] = self.get_neighbor_fun(segments, k, hash_matrix,
                                                                 fun_hashkey, max_level, vec)

            neighbors.append(top_right_bottom_left)
        return neighbors

    def get_hash_matrix(self, segments):
        n = len(segments)

        big_segment = ImageSegment(0, 0, 1, 1)
        big_segment.set_segment_max_segments(segments)

        h = big_segment.get_height()
        w = big_segment.get_width()

        coef = w / h

        m_width = int(np.ceil(n ** 0.5 * coef))
        m_height = int(np.ceil(m_width / coef))

        dh =  (m_height-1) / h
        dw = (m_width-1) / w
        ch = big_segment.y_top_left
        cw = big_segment.x_top_left
        hashkey = lambda seg: self.get_index_hash(seg, dh, dw, ch, cw)

        hash_matrix = [[[] for i in range(m_width)] for j in range(m_height)]

        for i, seg in enumerate(segments):
            hash_i, hash_j = hashkey(seg)
            hash_matrix[hash_i][hash_j].append(i)

        return hash_matrix, hashkey

    def get_index_hash(self, seg, dh, dw, ch, cw):
        x_c, y_c = seg.get_center()
        hash_i = int((y_c - ch) * dh)
        hash_j = int((x_c - cw) * dw)
        return hash_i, hash_j

    def get_segment_hash_cell(self, hash_matrix, hash_i, hash_j):
        return hash_matrix[hash_i][hash_j]

    def get_segment_index_level(self, segments, k, hash_matrix, fun_hashkey, level, vec):
        index_h, index_w = fun_hashkey(segments[k])

        index_h_max = len(hash_matrix)
        index_w_max = len(hash_matrix[0])

        neighbors = []
        if vec in ("left", "right"):
            new_index_w = index_w - level if vec == "left" else index_w + level
            if new_index_w < 0 or new_index_w >= index_w_max:
                return k
            new_index_h = index_h
            new_index_h0 = max(0, index_h - 1) #max(0, index_h - level)
            new_index_h1 = min(index_h_max - 1 , index_h + 1)  #min(index_h_max - 1 , index_h + level) 
            for new_index_h in range(new_index_h0, new_index_h1+1):
                neighbors += self.get_segment_hash_cell(hash_matrix, new_index_h, new_index_w)
             
            
        elif vec in ("top", "bottom"):
            new_index_h = index_h - level if vec == "top" else index_h + level
            new_index_w = index_w
            if new_index_h < 0 or new_index_h >= index_h_max:
                return k
            new_index_w0 = max(0, index_w - 1) #max(0, index_w - level)
            new_index_w1 = min(index_w_max - 1, index_w + 1)#min(index_w_max - 1, index_w + level)
            for new_index_w in range(new_index_w0, new_index_w1+1):
                neighbors += self.get_segment_hash_cell(hash_matrix, new_index_h, new_index_w)
             

        # if new_index_w < 0 or new_index_w >= index_w_max or new_index_h < 0 or new_index_h >= index_h_max:
        #     return k
        # else:
        #     neighbors = []
        #     if vec in ("left", "right"):
        #         neighbors += self.get_segment_hash_cell(hash_matrix, new_index_h, new_index_w)
        #     else:
        #         neighbors += self.get_segment_hash_cell(hash_matrix, new_index_h, new_index_w)



        min_distance = np.inf
        min_index = k

        for neighbor_index_seg in neighbors:
            if vec == "left":
                neighbor_ = segments[neighbor_index_seg].x_bottom_right
                seg_ = segments[k].x_top_left
                nc_, nc = segments[neighbor_index_seg].get_center()
                wc_, wc = segments[k].get_center()
                delta = seg_-neighbor_
                distance = delta**2+(nc-wc)**2
            elif vec == "right":
                neighbor_ = segments[neighbor_index_seg].x_top_left
                seg_ = segments[k].x_bottom_right
                nc_, nc = segments[neighbor_index_seg].get_center()
                wc_, wc = segments[k].get_center()
                delta = neighbor_-seg_
                distance = delta**2+(nc-wc)**2
            elif vec == "top":
                neighbor_ = segments[neighbor_index_seg].y_bottom_right
                seg_ = segments[k].y_top_left
                nc, nc_ = segments[neighbor_index_seg].get_center()
                wc, wc_ = segments[k].get_center()
                delta = seg_ - neighbor_
                distance = delta ** 2 + (nc - wc) ** 2
            elif vec == "bottom":
                neighbor_ = segments[neighbor_index_seg].y_top_left
                seg_ = segments[k].y_bottom_right
                nc, nc_ = segments[neighbor_index_seg].get_center()
                wc, wc_ = segments[k].get_center()
                delta = neighbor_ - seg_
                distance = delta ** 2 + (nc - wc) ** 2
            if (delta > 0) and (distance < min_distance):
                min_distance = distance
                min_index = neighbor_index_seg
        return min_index

    def get_neighbor_fun(self, segments, k, hash_matrix, fun_hashkey, max_level, vec):
        for level in range(max_level):
            min_index_seg = self.get_segment_index_level(segments, k, hash_matrix, fun_hashkey, level, vec)
            if min_index_seg != k:
                return min_index_seg
        return k

    def get_distans(self, neighbors, segments):
        distans = []

        for i, ed_k in enumerate(neighbors):
            top_dist = segments[i].y_top_left - segments[ed_k[0]].y_bottom_right if i!=ed_k[0] else 0
            right_dist = segments[ed_k[1]].x_top_left - segments[i].x_bottom_right if i!=ed_k[1] else 0
            bottom_dist = segments[ed_k[2]].y_top_left - segments[i].y_bottom_right if i!=ed_k[2] else 0
            left_dist = segments[i].x_top_left - segments[ed_k[3]].x_bottom_right if i!=ed_k[3] else 0
            distans.append([top_dist, right_dist, bottom_dist, left_dist])

        return distans

    def get_standart_distant(self, distans):
        distribution_h = []
        distribution_w = []

        for dist in distans:
            if dist[0] > 0:
                distribution_h.append(dist[0])
            if dist[1] > 0:
                distribution_w.append(dist[1])
            if dist[2] > 0:
                distribution_h.append(dist[2])
            if dist[3] > 0:
                distribution_w.append(dist[3])
        dist_row = np.mean(distribution_h)
        dist_word = np.mean(distribution_w)
        return dist_word, dist_row

    def get_graph_segments(self, segments, neighbors, dist_word, dist_row, distans):
        graph = Graph()
        edges = []

        for n1, ed_k in enumerate(neighbors):
            for vec, n2 in enumerate(ed_k):
                set_n = {n1, n2}
                if n1 != n2 and not (set_n in edges):
                    if (vec in (0, 2)) and (distans[n1][vec] <= dist_row) and (distans[n1][vec] > 0):
                        edges.append(set_n)
                    elif (vec in (1, 3)) and (distans[n1][vec] <= dist_word) and (distans[n1][vec] > 0):
                        edges.append(set_n)
        for i, seg in enumerate(segments):
            c1x, c1y = seg.get_center()
            index = graph.add_node(c1x, c1y)  # index_word+1

        for edge in edges:
            n_list = list(edge)
            n1, n2 = n_list[0] + 1, n_list[1] + 1
            graph.add_edge(n1, n2)

        return graph
