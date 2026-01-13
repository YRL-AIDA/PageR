from typing import Dict, List
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextLine, LTChar, LAParams
from pdfminer.layout import LTImage,  LTFigure
import math


class PDFStructureExtractor:
    def __init__(self, laparams: LAParams = None):
        """Инициализация парсера PDF"""
        self.laparams = laparams or LAParams(
            line_margin=0.5,
            word_margin=0.1,
            char_margin=2.0,
            boxes_flow=0.5,
            detect_vertical=True
        )
    
    def extract_from_path(self, pdf_path: str) -> Dict:
        """Извлечение структуры из PDF файла"""
        result = {
            "document": pdf_path,
            "pages": []
        }
        
        for page_num, page_layout in enumerate(extract_pages(pdf_path, laparams=self.laparams)):
            page_info = self._process_page(page_layout, page_num)
            result["pages"].append(page_info)
        
        return result
    
    def _process_page(self, page_layout, page_number: int) -> Dict:
        """Обработка одной страницы"""
        page_info = {
            "number": page_number,
            "width": math.ceil(page_layout.width),
            "height": math.ceil(page_layout.height),
            "rows": [],
            "images": []  # Добавляем список для изображений
        }
        
        # Собираем все элементы страницы
        elements = []
        self._collect_elements(page_layout, elements)
        
        # Разделяем элементы по типам
        text_lines = []
        images = []
        
        for element in elements:
            if isinstance(element, LTTextLine):
                text_lines.append(element)
            elif isinstance(element, LTImage):
                images.append(element)
            elif isinstance(element, LTFigure):
                # LTFigure может содержать изображения или графику
                figure_images = self._extract_images_from_figure(element)
                images.extend(figure_images)
        
        # Обрабатываем текстовые строки
        for text_line in text_lines:
            row_info = self._process_text_line(text_line, page_info["height"])
            if row_info:
                page_info["rows"].append(row_info)
        
        # Обрабатываем изображения
        for image in images:
            image_info = self._process_image(image, page_info["height"])
            if image_info:
                page_info["images"].append(image_info)
        
        # Сортируем строки по Y координате (сверху вниз)
        page_info["rows"].sort(key=lambda x: x["segment"]["y_top_left"], reverse=True)
        
        # Сортируем изображения по Y координате (сверху вниз)
        page_info["images"].sort(key=lambda x: x["segment"]["y_top_left"], reverse=True)
        
        return page_info
    
    def _collect_elements(self, element, elements_list: List):
        """Рекурсивный сбор всех элементов макета"""
        elements_list.append(element)
        
        if hasattr(element, '_objs'):
            for child in element._objs:
                self._collect_elements(child, elements_list)
    
    def _extract_images_from_figure(self, figure: LTFigure) -> List[LTImage]:
        """Извлечение изображений из LTFigure объекта"""
        images = []
        elements = []
        self._collect_elements(figure, elements)
        
        for element in elements:
            if isinstance(element, LTImage):
                images.append(element)
        
        return images
    
    def _process_text_line(self, text_line: LTTextLine, page_height: float) -> Dict:
        """Обработка текстовой строки"""
        if not text_line.get_text().strip():
            return None
        
        x0, y0, x1, y1 = text_line.bbox
        
        # Фильтруем слишком высокие элементы (вероятно, блоки)
        line_height = y1 - y0
        if line_height > 50:
            return None
        
        y_top_left = page_height - y1
        height = y1 - y0
        width = x1 - x0
        
        # Извлекаем слова
        words = self._extract_words_from_line(text_line, page_height)
        
        return {
            "segment": {
                "x_top_left": math.ceil(x0),
                "y_top_left": math.ceil(y_top_left),
                "width": math.ceil(width),
                "height": math.ceil(height)
            },
            "text": text_line.get_text().strip(),
            "words": words
        }
    
    def _extract_words_from_line(self, text_line: LTTextLine, page_height: float) -> List[Dict]:
        """Извлечение слов из строки"""
        words = []
        current_word_chars = []
        current_word_bbox = None
        
        for child in text_line:
            if isinstance(child, LTChar):
                char_text = child.get_text()
                char_bbox = child.bbox
                
                if char_text.strip() and not char_text.isspace():
                    if not current_word_chars:
                        current_word_bbox = list(char_bbox)
                    else:
                        current_word_bbox[0] = min(current_word_bbox[0], char_bbox[0])
                        current_word_bbox[1] = min(current_word_bbox[1], char_bbox[1])
                        current_word_bbox[2] = max(current_word_bbox[2], char_bbox[2])
                        current_word_bbox[3] = max(current_word_bbox[3], char_bbox[3])
                    
                    current_word_chars.append(char_text)
                else:
                    if current_word_chars:
                        word_info = self._create_word_info(
                            current_word_chars, current_word_bbox, page_height
                        )
                        words.append(word_info)
                        current_word_chars = []
                        current_word_bbox = None
        
        if current_word_chars:
            word_info = self._create_word_info(
                current_word_chars, current_word_bbox, page_height
            )
            words.append(word_info)
        
        return words
    
    def _process_image(self, image: LTImage, page_height: float) -> Dict:
        """Обработка изображения"""
        try:
            # Получаем координаты изображения
            x0, y0, x1, y1 = image.bbox
            
            # Преобразуем координаты
            y_top_left = page_height - y1
            height = y1 - y0
            width = x1 - x0
            
            # Проверяем, что это действительно изображение (имеет ненулевые размеры)
            if width <= 0 or height <= 0:
                return None
            
            # Также проверяем, что изображение не слишком маленькое (может быть шумом)
            if width < 5 or height < 5:
                return None
            
            image_info = {
                "segment": {
                    "x_top_left": math.ceil(x0),
                    "y_top_left": math.ceil(y_top_left),
                    "width": math.ceil(width),
                    "height": math.ceil(height),
                },
                "text": " "  # Пробел вместо текста для изображений
            }
            
            # Дополнительная информация об изображении (опционально)
            if hasattr(image, 'name'):
                image_info['image_name'] = getattr(image, 'name', '')
            
            return image_info
            
        except Exception as e:
            print(f"Ошибка при обработке изображения: {e}")
            return None
    
    def _create_word_info(self, chars: List[str], bbox: List[float], page_height: float) -> Dict:
        """Создание информации о слове"""
        word_text = ''.join(chars)
        x0, y0, x1, y1 = bbox
        
        word_segment = {
            "x_top_left": math.ceil(x0),
            "y_top_left": math.ceil(page_height - y1),
            "width": math.ceil(x1 - x0),
            "height": math.ceil(y1 - y0)
        }
        
        return {
            "segment": word_segment,
            "text": word_text
        }



class MinerPDFModel:
    """Класс-аналог вашего PrecisionPDFModel, но использующий pdfminer"""
    
    def __init__(self, conf=None) -> None:
        self.pdf_json: Dict = {}
        self.count_page: int = 0
        self.page_model = None
        if conf and "page_model" in conf:
            self.page_model = conf["page_model"]
        
        # Инициализируем парсер
        laparams = LAParams(
            line_margin=0.5,
            word_margin=0.1,
            char_margin=2.0,
            boxes_flow=0.5
        )
        self.extractor = PDFStructureExtractor(laparams)
    
    def from_dict(self, input_model_dict: Dict):
        self.pdf_json = input_model_dict.copy()
        self.count_page = len(self.pdf_json['pages']) if "pages" in self.pdf_json.keys() else 0
    
    def to_dict(self) -> Dict:
        return self.pdf_json
    
    def extract(self) -> None:
        if not self.page_model:
            return
        
        for i in range(self.count_page):
            page_json = self.pdf_json["pages"][i]
            self.page_model.from_dict(page_json)
            self.page_model.extract()
            dict_page = self.page_model.to_dict()
            # TODO: удалить исходные строки и слова
            for key in dict_page.keys():
                self.pdf_json["pages"][i][key] = dict_page[key]
    
    def read_from_file(self, path_file: str) -> None:
        """Чтение структуры из PDF файла с использованием pdfminer"""
        self.path = path_file
        self.pdf_json = self.extractor.extract_from_path(path_file)
        self.count_page = len(self.pdf_json['pages']) if "pages" in self.pdf_json.keys() else 0
    
    def clean_model(self) -> None:
        self.pdf_json = {}
        self.count_page = 0
