import os
from dotenv import load_dotenv
load_dotenv(override=True)

class ManagerModels:
    def __init__(self):
        pass

    def get_model(self, name):
        if name == "rowGLAM-tokenizer":
            from .models.rowGLAM_tokenizer_20250811 import RowGLAMTokenizer
            return RowGLAMTokenizer()
        elif name == "rowGLAM-model":
            from .models.row_glam_20250811 import get_load_model
            model = get_load_model(os.getenv("PATH_TORCH_ROW_GLAM"))
            return model
        elif name == "wordGLAM-tokenizer":
            from .models.wordGLAM_tokenizer_20251023 import WordGLAMTokenizer
            return WordGLAMTokenizer()
        elif name == "words2rowsGLAM-model":
            from .models.words2rows_glam_20251023 import get_load_model
            model = get_load_model(os.getenv("PATH_TORCH_WORDS2ROWS_GLAM"))
            return model

        else:
            raise NotModel(name)

class NotModel(Exception):
    def __init__(self, name_model):
        self.name_model = name_model

    def __str__(self):
        return f"Not Model with name {self.name_model}"



