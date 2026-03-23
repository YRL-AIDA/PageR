from .base_converter import BaseConverter
from ..pdf_as_json_model import BasePDFasJsonModel
from ..logic_tree_model import LogicTreeModel
class PDF2LogicTree(BaseConverter):
    def convert(self, input_model:BasePDFasJsonModel, output_model:LogicTreeModel):
        document = input_model.document
        regions = [reg for page in document.pages for reg in page.regions]
        tree = self.get_tree_from_doc(regions)
        self.set_level(regions, tree['parent'])
        
        output_model.document = document
        output_model.regions = regions
        output_model.edges = tree

    def get_parent_edges(self, regions):
        parent_edges = []
        tmp_parent_list_id = [-1] # -1 is id Document
        

        # region_embs = {i:get_embedding(reg) for i, reg in enumerate(regions)}
        def is_include_by_id(parent_id, child_id):
            if parent_id == -1:
                return True
            return regions[parent_id].font > regions[child_id].font

        for id_reg, reg  in enumerate(regions):
            test_parent_id = tmp_parent_list_id[-1]

            # Поместить контент
            if reg.is_content:
                parent_edges.append((test_parent_id, id_reg))
                continue
            
            # Работа с заголовками
            while not is_include_by_id(test_parent_id, id_reg):
                tmp_parent_list_id.pop(-1)
                test_parent_id = tmp_parent_list_id[-1]

            parent_edges.append((test_parent_id, id_reg))
            tmp_parent_list_id.append(id_reg)
        return parent_edges
        

    def get_tree_from_doc(self, regions):
        N = len(regions)
        order_edges = [(-1, 0)] + [(i, i+1) for i in range(N-1)]
        parent_edges = self.get_parent_edges(regions)
        return {
            'parent': parent_edges,
            'order': order_edges
        }
        


    def set_level(self, regions, edges):
        levels = []
        for e in edges:
            level = 1
            ref = e[0]
            while ref != -1:
                ref = edges[ref][0]
                level+=1
            levels.append(level)
        for r, l in zip(regions, levels):
            r.set_header_level(l)