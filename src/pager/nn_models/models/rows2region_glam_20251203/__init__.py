
from .torch_model import TorchModel
import torch
def get_load_model(path, device='cpu'):
    model = TorchModel({
        "sigmoidEdge": True,
        "node_featch": 15,
        "edge_featch": 4,
        "Tag":[  {'in': -1, 'size': 512, 'out': 256, 'k': 3},
            {'in': 256, 'size': 128, 'out': 64, 'k': 3},
            {'in': 64, 'size': 32, 'out': 16, 'k': 3},
            ],
        "NodeLinear": [-1, 32, 16],
        "NodeLinearClassifier": [8],
        "EdgeLinear": [64, 8],
        "NodeClasses": 5,
        "batchNormNode": True,
        "batchNormEdge": True,
        "seg_k": 0.5,
    })
    model.load_state_dict(torch.load(path, weights_only=True, map_location=torch.device(device)))
    return model