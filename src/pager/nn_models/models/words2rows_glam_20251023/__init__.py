# from .model import get_final_model

from .torch_model import TorchModel
import torch
def get_load_model(path, device='cpu'):
    model = TorchModel({
        "sigmoidEdge": True,
        "node_featch": 15,
        "edge_featch": 4,
        "learning_rate": 0.05,
        "Tag":[ {'in': -1, 'size': 64, 'out': 64, 'k': 3},
                {'in': 64, 'size': 32, 'out': 32, 'k': 2},
                {'in': 32, 'size': 16, 'out': 16, 'k': 1},
                ],
        "NodeLinear": [-1, 32, 16],
        # "NodeLinearClassifier": [8],
        "EdgeLinear": [32, 16, 8],
        # "NodeClasses": 5,
        "batchNormNode": True,
        "batchNormEdge": True,
        "seg_k": 0.5,
    })
    model.load_state_dict(torch.load(path, weights_only=True, map_location=torch.device(device)))
    return model