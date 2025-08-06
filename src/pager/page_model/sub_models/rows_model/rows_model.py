from ..base_sub_model import BaseSubModel
from typing import Dict, List
from ..dtype import Row



class RowsModel(BaseSubModel):
    def __init__(self) -> None:
        super().__init__()
        self.rows: List[Row] = []
        self.others = []
    
    def from_dict(self, input_model_dict: Dict):
        self.rows = [Row(row_dict) for row_dict in input_model_dict["rows"]]

    def to_dict(self) -> Dict:
        return {"rows": [row.to_dict() for row in self.rows]}

    def read_from_file(self, path_file: str) -> None:
        phis_json = self._read_json(path_file)      
        for block_dict in phis_json["rows"]:
            row = Row(block_dict)
            self.rows.append(row)
    
    def set_rows_from_dict(self, row_list_dict):
        self.rows = []
        for row_dict in row_list_dict:
            self.rows.append(Row(row_dict))
    
    def set_others_from_dict(self, other_list_dict):
        self.others = other_list_dict
    
    def clean_model(self):
        self.rows = []