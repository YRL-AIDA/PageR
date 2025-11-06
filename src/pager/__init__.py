import os
import torch
device = torch.device('cpu')
if 'DEVICE' in os.environ:
    device = torch.device('cuda:0' if torch.cuda.device_count() != 0 else 'cpu') if os.environ['DEVICE'] == 'gpu' else torch.device('cpu')


from .page_model import PageModel, PageModelUnit
from .page_model.sub_models import *
from .page_model.sub_models.dtype import *
from .nn_models.manager_models import ManagerModels



