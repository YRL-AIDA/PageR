import os 
import shutil
import sys


def get_path(default_path, desc):
    print(desc)
    while True:
        ans = input(" <- :")
        if ans == '':
            return default_path
        else:
            if os.path.exists(ans):
                return ans
            else:
                print('Error path')

def check_dependencies():
    required_binaries = ['java', 'tesseract']
    for binary in required_binaries:
        if shutil.which(binary) is None:
            raise RuntimeError(
                f"Требуется установить {binary}. "
            )
        else:
            print(f"{binary} установлен")

pager_dir = os.path.dirname(__file__)
print(pager_dir)
model_dir = os.path.join(pager_dir, 'models')
print(model_dir)

path = os.path.join(model_dir, 'PDF2Block', 'precisionPDF.jar')
JAR_PDF_PARSER = get_path(path, f'path JAR_PDF_PARSER (default: {path})')

# path = os.path.join(model_dir,  'seg_gnn')
# PATH_TORCH_SEG_GNN_MODEL = get_path(path, f'path PATH_TORCH_SEG_GNN_MODEL (default: {path})')

# path = os.path.join(model_dir,  'seg_linear')
# PATH_TORCH_SEG_LINEAR_MODEL = get_path(path, f'path PATH_TORCH_SEG_LINEAR_MODEL (default: {path})')

path = os.path.join(model_dir,  'Words2Rows','style_classmodel_20250121')
PATH_STYLE_MODEL = get_path(path, f'path PATH_STYLE_MODEL (default: {path})')

path = os.path.join(model_dir,  'glam_node_model_20250221')
PATH_TORCH_GLAM_NODE_MODEL = get_path(path, f'path PATH_TORCH_GLAM_NODE_MODEL (default: {path})')

path = os.path.join(model_dir,  'glam_edge_model_20250221')
PATH_TORCH_GLAM_EDGE_MODEL = get_path(path, f'path PATH_TORCH_GLAM_EDGE_MODEL (default: {path})')

path = os.path.join(model_dir,  'glam_model_20250415')
PATH_TORCH_GLAM_MODEL = get_path(path, f'path PATH_TORCH_GLAM_MODEL (default: {path})')

path = os.path.join(model_dir,  'row_glam_20250811')
PATH_TORCH_ROW_GLAM = get_path(path, f'path PATH_TORCH_ROW_GLAM (default: {path})')

path = os.path.join(model_dir, 'Words2Rows', 'words2rows_glam_20251023')
PATH_TORCH_WORDS2ROWS_GLAM = get_path(path, f'path PATH_TORCH_WORDS2ROWS_GLAM (default: {path})')

path = os.path.join(model_dir,  'glam_config_model_20250221.json')
PATH_TORCH_GLAM_CONF_MODEL = get_path(path, f'path PATH_TORCH_GLAM_CONF_MODEL (default: {path})')


# словарь Python
config = {'JAR_PDF_PARSER': JAR_PDF_PARSER,
        # 'PATH_TORCH_SEG_GNN_MODEL':PATH_TORCH_SEG_GNN_MODEL, 
        # 'PATH_TORCH_SEG_LINEAR_MODEL': PATH_TORCH_SEG_LINEAR_MODEL,
        'PATH_STYLE_MODEL': PATH_STYLE_MODEL,
        'PATH_TORCH_GLAM_NODE_MODEL': PATH_TORCH_GLAM_NODE_MODEL,
        'PATH_TORCH_GLAM_EDGE_MODEL': PATH_TORCH_GLAM_EDGE_MODEL,
        'PATH_TORCH_GLAM_MODEL': PATH_TORCH_GLAM_MODEL,
        'PATH_TORCH_GLAM_CONF_MODEL': PATH_TORCH_GLAM_CONF_MODEL,
        'PATH_TORCH_ROW_GLAM': PATH_TORCH_ROW_GLAM,
        'PATH_TORCH_WORDS2ROWS_GLAM':PATH_TORCH_WORDS2ROWS_GLAM,
        'DEVICE': 'cpu'
}

        
# открываем файл на запись
with open(os.path.join(pager_dir, '.env'), 'w') as f:
    for key, val in config.items():
        f.write(f'{key}={val}\n')



check_dependencies()