from ..base_sub_model import BaseConverter
from ..region_model import RegionModel
from ..rows_model import RowsModel
from ..dtype import ImageSegment
from pager.nn_models.manager_models import ManagerModels
from ..dtype import Graph
from ..extractors import RegionSorterCutXYExtractor


class Rows2Regions(BaseConverter):
    def __init__(self):
        manager_model = ManagerModels()
        self.rows2regionsGLAM_tokenizer = manager_model.get_model("rowGLAM-tokenizer")
        self.rows2regionsGLAM = manager_model.get_model("rowGLAM-model")

    def convert(self, input_model: RowsModel, output_model: RegionModel):
        page_json = input_model.to_dict()
        region_list = self.get_region(page_json['rows'])
        output_model.from_dict({"regions": region_list})

        # сортировка после создания региона
        sorter = RegionSorterCutXYExtractor()
        sorter.extract(output_model)

    def get_region(self, rows_json):
        graph_dict_torch = self.rows2regionsGLAM_tokenizer(rows_json)
        result = self.rows2regionsGLAM(graph_dict_torch)
        result['deleted_edges'] = result['E_pred'] > 0.5
        
        graph = graph_dict_torch['inds']
        deleted_edges = result['deleted_edges']
        
        regions = self.regions_from_graph(rows_json, graph, deleted_edges)
        return regions
    

    def regions_from_graph(self, rows_json, graph, deleted_edges):
        graph_ = Graph()
        regions = []
        
        for row_json in rows_json:
            segment = ImageSegment(dict_2p=row_json['segment'])
            xc, yc = segment.get_center()
            graph_.add_node(xc, yc)

        for node_i, node_j, ind in zip(graph[0], graph[1], deleted_edges):
            if not ind:
                graph_.add_edge(node_i+1, node_j+1)

        for reg in graph_.get_related_graphs():
            indexes = [node.index-1 for node in reg.get_nodes()]
            regions.append({'rows': [rows_json[i] for i in indexes]})
        return regions



# class Rows2Regions(BaseConverter):
#     def __init__(self, conf={}):
#         manager_model = ManagerModels()
#         self.rowGLAM_tokenizer = manager_model.get_model("rowGLAM-tokenizer")
#         self.rowGLAM = manager_model.get_model("rowGLAM-model")

#     def convert(self, input_model: RowsModel, output_model: RegionModel):
#         page_json = input_model.to_dict()
#         region_list = self.get_region(page_json['rows'])
#         output_model.from_dict({"regions": region_list})

#         # сортировка после создания региона
#         sorter = RegionSorterCutXYExtractor()
#         sorter.extract(output_model)

#     def get_region(self, rows_json):
#         graph_dict_torch = self.rowGLAM_tokenizer(rows_json)
#         result = self.rowGLAM(graph_dict_torch)
#         result['deleted_edges'] = result['E_pred'] > 0.5
#         result['labels'] = result['node_classes'].argmax(1)
        
#         graph = graph_dict_torch['inds']
    
#         labels = result['labels']
#         deleted_edges = result['deleted_edges']
        
#         regions = self.regions_from_graph(rows_json, graph, labels, deleted_edges)
#         return regions
    

#     def regions_from_graph(self, rows_json, A, labels, deleted_edges):
#         graph_ = Graph()
#         regions = []

#         for row_json in rows_json:
#             segment = ImageSegment(dict_2p=row_json['segment'])
#             xc, yc = segment.get_center()
#             graph_.add_node(xc, yc)

#         for node_i, node_j, ind in zip(A[0], A[1], deleted_edges):
#             if ind != 0:
#                 graph_.add_edge(node_i+1, node_j+1)

#         for reg in graph_.get_related_graphs():
#             indexes = [node.index-1 for node in reg.get_nodes()]
#             label = [labels[i] for i in indexes]
#             count_label = Counter(label)
#             label = max(count_label, key=count_label.get)
#             regions.append({'rows': [rows_json[i] for i in indexes], 'label': label})
#         return regions