from ..base_sub_model import BaseSubModel
from typing import Dict, List
from ..dtype import Region


class RegionModel(BaseSubModel):
    def __init__(self) -> None:
        super().__init__()
        self.regions: List[Region] = []
    
    def from_dict(self, input_model_dict: Dict):
        self.regions = [Region(region) for region in input_model_dict["regions"]]

    def to_dict(self) -> Dict:
        return {"regions": [region.to_dict() for region in self.regions]}

    def read_from_file(self, path_file: str) -> None:
        phis_json = self._read_json(path_file)
        self.from_dict(phis_json)

    def clean_model(self):
        self.regions = []
    
    def show(self, with_label=True):
        # TODO: Регионы имеют разные метки (зависит от датасета)
        print(f"count regions: {len(self.regions)}")
        # colors = {
        #     "list": "g",
        #     "text": "b",
        #     "header": "orange",
        #     "figure": "r",
        #     "table": "y",
        # }
        # for block in self.blocks:
        #     block.segment.plot(color=colors[block.label] if with_label else "r", text=block.label if with_label else "")
