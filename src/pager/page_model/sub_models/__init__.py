from .base_sub_model import BaseSubModel, BaseConverter, BaseExtractor, BaseLoger, BasePrinter, AddArgsFromModelExtractor
from .converters import *

from .image_model import *
from .pdf_model import *
from .words_model import *
from .rows_model import *
from .region_model import *
from .words_and_styles_model import *
from .phisical_model import *
from .ms_word_model import *
from .json_with_featchs_model import *

from .converters import *

import warnings
class PhisicalModel(RegionModel):
   def __init__(self):
       warnings.warn("use WoRegionModelrd (PhisicalModel deleting)")
       super().__init__()
