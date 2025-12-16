import os
from .sys_model_manager import get_model_path

class ManagerModels:
    def __init__(self):
        pass

    def get_model(self, name):
        if name == "rowGLAM-tokenizer":
            # from .models.rowGLAM_tokenizer_20250811 import RowGLAMTokenizer
            # return RowGLAMTokenizer()
            from .models.rowsGLAM_tokenizer_20251106 import RowGLAMTokenizer
            return RowGLAMTokenizer()
        elif name == "rowGLAM-model":
            # from .models.row_glam_20250811 import get_load_model
            # model = get_load_model(os.getenv("PATH_TORCH_ROW_GLAM"))
            from .models.rows2region_glam_20251203 import get_load_model
            model = get_load_model(get_model_path('rows2regions-GLAM'))
            return model
        elif name == "wordGLAM-tokenizer":
            from .models.wordGLAM_tokenizer_20251023 import WordGLAMTokenizer
            return WordGLAMTokenizer()
        elif name == "words2rowsGLAM-model":
            from .models.words2rows_glam_20251023 import get_load_model
            model = get_load_model(get_model_path('words2rows-GLAM'))
            return model
        
        elif name == 'style-model-20250121': 
            from .models.imgfont_tokenizer_20250121 import classifier_image_word, get_model
            model = get_model(get_model_path('style_classmodel'))
            fun = lambda word_img:classifier_image_word(model, word_img).detach().numpy().tolist()
            return model, fun
        # elif name == 'style-model-20250424':
        #     from .models.imgfont_tokenizer_20250424 import classifier_image_word, get_model
        #     model = get_model(get_model_path('style_classmodel2'))
        #     fun = lambda word_img:classifier_image_word(model, word_img).detach().numpy().tolist()
        #     return model, fun
        else:
            raise NotModel(name)

class NotModel(Exception):
    def __init__(self, name_model):
        self.name_model = name_model

    def __str__(self):
        return f"Not Model with name {self.name_model}"



