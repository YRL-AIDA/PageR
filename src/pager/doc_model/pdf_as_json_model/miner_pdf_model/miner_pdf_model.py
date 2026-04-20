from typing import Dict, List
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextLine, LTTextLineHorizontal
from pdfminer.layout import  LTChar, LAParams
from pdfminer.layout import LTImage,  LTFigure, LTPage
import math
import os
from pdf2image import convert_from_path
from ..base_pdf_as_json_model import BasePDFasJsonModel


DPI = 72
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
    
    def _pdf_to_pixel_coords(self, x, y, page_height_points, dpi=DPI):
        """
        x, y — координаты в points из PDFMiner (относительно cropbox)
        page_height_points — высота страницы в points (cropbox.y1 - cropbox.y0)
        dpi — разрешение для рендеринга
        возвращает (x_px, y_px) — пиксельные координаты с началом в верхнем левом углу
        """
        # Масштабируем в пиксели
        x_px = x * dpi / 72.0
        y_px = (page_height_points - y) * dpi / 72.0  # переворот вертикали
        return int(x_px), int(y_px)


    def _get_coords(self, bbox, page_height):
        x_pdf_bottom_left, y_pdf_bottom_left, x_pdf_top_right, y_pdf_top_right = bbox

        x0_px, y0_px = self._pdf_to_pixel_coords(x_pdf_bottom_left, y_pdf_top_right, page_height)
        x1_px, y1_px = self._pdf_to_pixel_coords(x_pdf_top_right, y_pdf_bottom_left, page_height)

        # Нормализуем координаты
        x_top_left = min(x0_px, x1_px)
        x_bottom_right = max(x0_px, x1_px)
        y_top_left = min(y0_px, y1_px)
        y_bottom_right = max(y0_px, y1_px)
        # Преобразуем координаты
        
        height = y_bottom_right - y_top_left
        width = x_bottom_right - x_top_left
        return x_top_left, x_bottom_right, width, y_top_left, y_bottom_right, height

    def extract_from_path(self, pdf_path: str) -> Dict:
        """Извлечение структуры из PDF файла"""
        result = {
            "document": pdf_path,
            "pages": [],
        }
        
        for page_num, page_layout in enumerate(extract_pages(pdf_path, laparams=self.laparams)):
            page_info = self._process_page(page_layout, page_num)
            result["pages"].append(page_info)
        
        return result
    
    def _process_page(self, page_layout:LTPage, page_number: int) -> Dict:
        """Обработка одной страницы"""
        page_info = {
            "number": page_number,
            "width": math.ceil(page_layout.width*DPI/72),
            "height": math.ceil(page_layout.height*DPI/72),
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
            elif isinstance(element, LTTextLineHorizontal):
                text_lines.append(element)
            elif isinstance(element, LTImage):
                images.append(element)
            elif isinstance(element, LTFigure):
                # LTFigure может содержать изображения или графику
                figure_images = self._extract_images_from_figure(element)
                images.extend(figure_images)
        
        # Обрабатываем текстовые строки
        for text_line in text_lines:
            row_info = self._process_text_line(text_line, page_layout.height)
            if row_info and self.__is_correct_segment(row_info['segment']):
                page_info["rows"].append(row_info)
        
        # Обрабатываем изображения
        for image in images:
            image_info = self._process_image(image, page_layout.height)
            if image_info and self.__is_correct_segment(image_info['segment']):
                page_info["images"].append(image_info)
        
        # Сортируем строки по Y координате (сверху вниз)
        page_info["rows"].sort(key=lambda x: x["segment"]["y_top_left"], reverse=False)
        
        # Сортируем изображения по Y координате (сверху вниз)
        page_info["images"].sort(key=lambda x: x["segment"]["y_top_left"], reverse=False)
        
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
        x0, y0, x1, y1 = text_line.x0, text_line.y0, text_line.x1, text_line.y1
        x_top_left, x_bottom_right, width, y_top_left, y_bottom_right, height=self._get_coords([x0, y0, x1, y1], page_height)
        if height > 50:
            return None
        # Извлекаем слова
        words = self._extract_words_from_line(text_line, page_height)
        
        return {
            "segment": {
                "x_top_left": math.ceil(x_top_left),
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
        font_info = {}
        
        for child in text_line:
            if isinstance(child, LTChar):
                char_text = child.get_text()
                char_bbox = child.bbox
                # TODO: Сейчас по первой букве По первой букве!!!!
                fontname = child.fontname
                fontsize = child.size
                is_normal = child.upright
                
                if char_text.strip() and not char_text.isspace():
                    if not current_word_chars:
                        current_word_bbox = list(char_bbox)
                        font_info = {
                            "fontname": fontname, "fontsize": fontsize, "is_normal": is_normal
                        }
                    else:
                        current_word_bbox[0] = min(current_word_bbox[0], char_bbox[0])
                        current_word_bbox[1] = min(current_word_bbox[1], char_bbox[1])
                        current_word_bbox[2] = max(current_word_bbox[2], char_bbox[2])
                        current_word_bbox[3] = max(current_word_bbox[3], char_bbox[3])
                    
                    current_word_chars.append(char_text)
                else:
                    if current_word_chars:
                        word_info = self._create_word_info(
                            current_word_chars, current_word_bbox, page_height, font_info
                        )
                        words.append(word_info)
                        current_word_chars = []
                        font_info = {}
                        current_word_bbox = None
        
        if current_word_chars:
            word_info = self._create_word_info(
                current_word_chars, current_word_bbox, page_height, font_info
            )
            words.append(word_info)
        
        words = [word for word in words if self.__is_correct_segment(word['segment'])]
        return words
    
    def __is_correct_segment(self, segment):
        return segment['width'] > 0 and segment['height'] > 0

    def _process_image(self, image: LTImage, page_height: float) -> Dict:
        """Обработка изображения"""
        try:
            # Получаем координаты изображения
            x_top_left, x_bottom_right, width, y_top_left, y_bottom_right, height=self._get_coords(image.bbox, page_height)
            
            
            # Проверяем, что это действительно изображение (имеет ненулевые размеры)
            if width <= 0 or height <= 0:
                return None
            
            # Также проверяем, что изображение не слишком маленькое (может быть шумом)
            if width < 5 or height < 5:
                return None
            
            image_info = {
                "segment": {
                    "x_top_left": math.ceil(x_top_left),
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
    
    def _create_word_info(self, chars: List[str], bbox: List[float], page_height: float, font_info: Dict) -> Dict:
        """Создание информации о слове"""
        word_text = ''.join(chars)
        x_top_left, x_bottom_right, width, y_top_left, y_bottom_right, height=self._get_coords(bbox, page_height)
        
        word_segment = {
            "x_top_left": math.ceil(x_top_left),
            "y_top_left": math.ceil(y_top_left),
            "width": math.ceil(width),
            "height": math.ceil(height)
        }
        
        return {
            "segment": word_segment,
            "text": word_text,
            "font": font_info
        }



class MinerPDFModel(BasePDFasJsonModel):
    """Класс-аналог вашего PrecisionPDFModel, но использующий pdfminer"""
    def __init__(self, conf=None) -> None:
        if conf is None:
            conf = {}
        # Инициализируем парсер
        laparams = LAParams(
            line_margin=0.5,
            word_margin=0.1,
            char_margin=2.0,
            boxes_flow=0.5
        )
        conf['extractor'] = PDFStructureExtractor(laparams)
        super().__init__(conf)
