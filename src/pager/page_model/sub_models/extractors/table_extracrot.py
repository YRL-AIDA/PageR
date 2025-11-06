from ..base_sub_model import BaseExtractor
from ..region_model import RegionModel
from ..dtype.block import TableBlock, Block
import numpy as np
import cv2
from typing import List, Tuple, Dict, Any

class TableExtractor(BaseExtractor):
    def extract(self, model:RegionModel):
        # TODO: block -> region
        if not "img" in model.__dict__:
            raise Exception("Can't find img in model")
        
        new_blocks = []
        for block in model.blocks:
            if block.label != "table":
                new_blocks.append(block)
            tbl = block.segment.get_segment_from_img(model.img)
            try:
                tbl_json = self.extract_table_to_json(model.img, block)
                print(tbl_json)
                tbl_block = TableBlock(block.to_dict(), tbl, tbl_json['grid'], tbl_json['cells'])
                new_blocks.append(tbl_block)
            except TableExaption:
                pass
        model.blocks = new_blocks

    def extract_table_to_json(self,
        image: np.ndarray,
        block: Block
    ) -> Dict[str, Any]:
        """
        Преобразует таблицу на изображении в JSON-структуру.

        Args:
            image: Входное изображение (numpy.ndarray).
            word_boxes: Координаты слов в формате [(x1, y1, x2, y2), ...].
            word_elements: Список слов с атрибутами [{"text": "...", "italic": bool, ...}].

        Returns:
            JSON-структура таблицы.
        """
        # Шаг 1: Находим сетку таблицы (гарантируем числовые типы)
        list_seg = [w.segment for w in block.words]
        x0 = block.segment.x_top_left
        y0 = block.segment.y_top_left
        word_bboxes = [(seg.x_top_left-x0, seg.y_top_left-y0, seg.x_bottom_right-x0, seg.y_bottom_right-y0) for seg in list_seg]
        word_dicts = [w.to_dict() for w in block.words]

        tbl_img = block.segment.get_segment_from_img(image)
        grid_lines = self.detect_table_grid(tbl_img, word_bboxes)
        if not grid_lines["rows"] or not grid_lines["columns"]:
            raise TableExaption("No table grid found")

        rows = [int(y) for y in sorted(grid_lines["rows"])]
        cols = [int(x) for x in sorted(grid_lines["columns"])]

        # Шаг 2: Находим объединённые ячейки (гарантируем числовые типы)
        merged_cells = self.find_merged_cells({"rows": rows, "columns": cols}, word_bboxes)
        merged_bboxes = [[int(i) for i in dict_merge_cell['bbox'] ]  for dict_merge_cell in merged_cells]

        # Шаг 3: Сопоставляем слова с ячейками
        cell_data = [[[] for _ in range(len(cols) - 1)] for _ in range(len(rows) - 1)]
        merge_data = [[] for _ in merged_bboxes]
        for (x1, y1, x2, y2), word in zip(word_bboxes, word_dicts):
            center_x = (int(x1) + int(x2)) // 2
            center_y = (int(y1) + int(y2)) // 2
            
            row_idx = max(0, np.searchsorted(rows, center_y) - 1)
            col_idx = max(0, np.searchsorted(cols, center_x) - 1)
            
            if row_idx < len(rows) - 1 and col_idx < len(cols) - 1:
                cell_data[row_idx][col_idx].append(word)

        for (x1, y1, x2, y2), word in zip(word_bboxes, word_dicts):
            center_x = (int(x1) + int(x2)) // 2
            center_y = (int(y1) + int(y2)) // 2

            for k, (x_1, y_1, x_2, y_2) in enumerate(merged_bboxes):
                if (x_1 <= center_x <= x_2) and (y_1 <= center_y <= y_2):
                    merge_data[k].append(word)
                    break

        # Шаг 4: Формируем итоговый JSON
        table_json = {
            "grid": {
                "rows": rows,
                "columns": cols
            },
            "cells": []
        }
        
        count_in_merged = [0 for _ in merged_bboxes]
       
        for i in range(len(rows) - 1):
            for j in range(len(cols) - 1):
                
                # Проверяем, не входит ли ячейка в объединённуя, которое было засчитано
                count_in_k_merge = 0
                for k, (x1, y1, x2, y2) in enumerate(merged_bboxes):
                    if (x1 <= cols[j] <= x2) and (y1 <= rows[i] <= y2):
                        index_k = k
                        count_in_merged[k] += 1
                        count_in_k_merge = count_in_merged[k]
                        break

                if count_in_k_merge > 1:
                    continue
            
                # Определяем объединение для текущей ячейки
                rowspan = colspan = 1
                for merge_cell in merged_cells:
                    (x1, y1, x2, y2) = merge_cell['bbox']
                    (rs, cs) = merge_cell['span']
                    if (x1 <= cols[j] <= x2) and (y1 <= rows[i] <= y2):
                        rowspan, colspan = int(rs), int(cs)
                        break

                # Собираем текст и стили
                words_ = merge_data[index_k] if count_in_k_merge == 1 else cell_data[i][j]
                cell_text = " ".join([w["text"] for w in words_] ) 
                # styles = {}
                # if cell_data[i][j]:
                #     styles = {k: v for k, v in cell_data[i][j][0].items() if k != "text"}

                cell_dict = {
                    "row": i,
                    "col": j,
                    "text": cell_text,
                    # "styles": styles,
                    # "bbox": [cols[j], rows[i], cols[j + colspan], rows[i + rowspan]]
                }

                if count_in_k_merge == 1:
                    cell_dict["rowspan"] = rowspan
                    cell_dict["colspan"] = colspan

                table_json["cells"].append(cell_dict)

        return table_json

    def detect_table_grid(self, tbl_img, word_boxes):
        # Preprocess image
        gray = cv2.cvtColor(tbl_img, cv2.COLOR_BGR2GRAY) if len(tbl_img.shape) == 3 else tbl_img
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Удаляем текст (закрашиваем word_boxes белым)
        mask = np.zeros_like(gray)
        for (x1, y1, x2, y2) in word_boxes:
            cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
        cleaned = cv2.bitwise_and(thresh, cv2.bitwise_not(mask))

        # Детекция линий (разные ядра для горизонтальных и вертикальных)
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 30))  # Уменьшили высоту ядра

        # Улучшаем детекцию вертикальных линий
        vertical_lines = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        horizontal_lines = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

        # Находим линии через HoughLinesP (более точный метод)
        def get_lines_v2(mask, axis='horizontal', min_len=50):
            lines = []
            if axis == 'horizontal':
                edges = cv2.Canny(mask, 50, 150)
                lines_p = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=min_len, maxLineGap=10)
                if lines_p is not None:
                    for line in lines_p:
                        x1, y1, x2, y2 = line[0]
                        lines.append((y1 + y2) // 2)  # Средняя координата линии
            else:
                edges = cv2.Canny(mask, 50, 150)
                lines_p = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=min_len, maxLineGap=10)
                if lines_p is not None:
                    for line in lines_p:
                        x1, y1, x2, y2 = line[0]
                        lines.append((x1 + x2) // 2)
            return sorted(list(set(lines)))  # Убираем дубликаты

        # Получаем линии (старый метод для горизонтальных, новый для вертикальных)
        horizontal = get_lines_v2(horizontal_lines, 'horizontal')
        vertical = get_lines_v2(vertical_lines, 'vertical', min_len=20)  # Более короткие линии для столбцов

        # Объединяем близкие линии (разные допуски для строк и столбцов)
        def merge_lines(lines, tol=5):
            if not lines:
                return []
            merged = [lines[0]]
            for line in lines[1:]:
                if abs(line - merged[-1]) > tol:
                    merged.append(line)
            return merged

        horizontal = merge_lines(horizontal, tol=5)
        vertical = merge_lines(vertical, tol=10)  # Больший допуск для столбцов

        # Фильтруем линии, которые режут слова (ослабляем условие для столбцов)
        def filter_cutting_lines(lines, word_boxes, axis='horizontal', max_cut_ratio=0.15):
            filtered = []
            for line in lines:
                cutting_words = 0
                for (x1, y1, x2, y2) in word_boxes:
                    if axis == 'horizontal':
                        if y1 < line < y2 and (min(line - y1, y2 - line) / (y2 - y1) > max_cut_ratio):
                            cutting_words += 1
                    else:
                        if x1 < line < x2 and (min(line - x1, x2 - line) / (x2 - x1) > max_cut_ratio):
                            cutting_words += 1
                if cutting_words <= 1:  # Допускаем 1 слово, пересекаемое линией
                    filtered.append(line)
            return filtered

        horizontal = filter_cutting_lines(horizontal, word_boxes, 'horizontal')
        vertical = filter_cutting_lines(vertical, word_boxes, 'vertical', max_cut_ratio=0.2)  # Более мягкий фильтр

        return {'rows': horizontal, 'columns': vertical}
    
    def find_merged_cells(self, grid_lines: Dict[str, List[int]],
                          word_boxes: List[Tuple[int, int, int, int]],
                          ) -> List[Dict[str, Tuple[int, int, int, int, Tuple[int, int]]]]:
        """
        Находит объединённые ячейки в таблице.

        Args:
            grid_lines: {'rows': List[y1, y2, ...], 'columns': List[x1, x2, ...]}
            word_boxes: [(x1, y1, x2, y2), ...] (координаты слов)

        Returns:
            Список объединённых ячеек в формате:
            [{
                'bbox': (x1, y1, x2, y2),  # Координаты ячейки
                'span': (rowspan, colspan)  # Число объединённых строк/столбцов
            }, ...]
        """
        if not grid_lines or not word_boxes:
            return []

        rows = sorted(grid_lines['rows'])
        cols = sorted(grid_lines['columns'])

        # Если нет линий или всего одна линия — таблица не существует
        if len(rows) < 2 or len(cols) < 2:
            return []

        # Инициализация сетки ячеек (все ячейки изначально не объединены)
        cell_grid = [[{'span': (1, 1)} for _ in range(len(cols) - 1)] for _ in range(len(rows) - 1)]

        for (x1, y1, x2, y2) in word_boxes:
            # Находим индексы строк и столбцов, которые пересекает слово
            row_start = np.searchsorted(rows, y1, side='right') - 1
            row_end = np.searchsorted(rows, y2, side='right')
            col_start = np.searchsorted(cols, x1, side='right') - 1
            col_end = np.searchsorted(cols, x2, side='right')

            # Корректируем индексы, чтобы не выйти за границы
            row_start = max(0, min(row_start, len(rows) - 2))
            row_end = max(1, min(row_end, len(rows) - 1))
            col_start = max(0, min(col_start, len(cols) - 2))
            col_end = max(1, min(col_end, len(cols) - 1))

            rowspan = row_end - row_start
            colspan = col_end - col_start

            if rowspan > 1 or colspan > 1:
                for i in range(row_start, row_end):
                    for j in range(col_start, col_end):
                        cell_grid[i][j]['span'] = (rowspan, colspan)

        # Собираем объединённые ячейки, избегая дубликатов
        merged_cells = []
        visited = set()

        for i in range(len(rows) - 1):
            for j in range(len(cols) - 1):
                if (i, j) in visited:
                    continue

                rowspan, colspan = cell_grid[i][j]['span']
                if rowspan > 1 or colspan > 1:
                    # Проверяем, что не выходим за границы
                    if i + rowspan > len(rows) - 1 or j + colspan > len(cols) - 1:
                        continue  # Пропускаем некорректные span

                    x1, x2 = cols[j], cols[j + colspan]
                    y1, y2 = rows[i], rows[i + rowspan]

                    # Помечаем все ячейки внутри объединённой как посещённые
                    for di in range(rowspan):
                        for dj in range(colspan):
                            visited.add((i + di, j + dj))

                    merged_cells.append({
                        'bbox': (x1, y1, x2, y2),
                        'span': (rowspan, colspan)
                    })

        return merged_cells
    

class TableExaption(Exception):
    def __init__(self, message):
        self.message = message

