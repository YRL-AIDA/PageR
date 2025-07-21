Спецификация формата JSON-документа
===================================

.. code-block:: json

    {
        "document": "string",
        "pages": [
            {
                "number": "integer",
                "width": "float",
                "height": "float",
                "blocks": [
                    {
                        "order": "integer",
                        "x_top_left": "float",
                        "y_top_left": "float",
                        "width": "float",
                        "height": "float",
                        "text": "string",
                        "start": "integer",
                        "end": "integer",
                        "metadata": "string",
                        "indent": "float",
                        "spacing": "float",
                        "annotations": [
                            {
                                "metadata": "string",
                                "url": "string",
                                "text": "string",
                                "is_bold": "boolean",
                                "is_italic": "boolean",
                                "is_normal": "boolean",
                                "font_name": "string",
                                "font_size": "float",
                                "x_top_left": "float",
                                "y_top_left": "float",
                                "width": "float",
                                "height": "float",
                                "start": "integer",
                                "end": "integer"
                            }
                        ]
                    }
                ],
                "tables": [],
                "images": [
                    {
                        "original_name": "string",
                        "tmp_file_path": "string",
                        "uuid": "string",
                        "x_top_left": "float",
                        "y_top_left": "float",
                        "width": "float",
                        "height": "float",
                        "page_num": "integer"
                    }
                ]
            }
        ]
    }

Описание полей
--------------

Корневой объект
~~~~~~~~~~~~~~~
- ``document`` (string): Имя файла документа
- ``pages`` (array[object]): Массив объектов страниц

Объект страницы (Page)
~~~~~~~~~~~~~~~~~~~~~~
- ``number`` (integer): Номер страницы
- ``width`` (float): Ширина страницы
- ``height`` (float): Высота страницы
- ``blocks`` (array[object]): Массив текстовых блоков
- ``tables`` (array): Пустой массив таблиц (заглушка)
- ``images`` (array[object]): Массив объектов изображений

Объект текстового блока (TextBlock)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``order`` (integer): Порядковый номер блока
- ``x_top_left`` (float): X-координата верхнего левого угла
- ``y_top_left`` (float): Y-координата верхнего левого угла
- ``width`` (float): Ширина блока
- ``height`` (float): Высота блока
- ``text`` (string): Текст содержимого блока
- ``start`` (integer): Начальная позиция текста
- ``end`` (integer): Конечная позиция текста
- ``metadata`` (string): Метаданные блока
- ``indent`` (float): Величина отступа
- ``spacing`` (float): Межстрочный интервал
- ``annotations`` (array[object]): Массив аннотаций

Объект аннотации (Annotation)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``metadata`` (string): Метаданные аннотации
- ``url`` (string): URL-адрес аннотации
- ``text`` (string): Текст аннотации
- ``is_bold`` (boolean): Жирное начертание
- ``is_italic`` (boolean): Курсивное начертание
- ``is_normal`` (boolean): Обычное начертание
- ``font_name`` (string): Наименование шрифта
- ``font_size`` (float): Размер шрифта
- ``x_top_left`` (float): X-координата аннотации
- ``y_top_left`` (float): Y-координата аннотации
- ``width`` (float): Ширина области аннотации
- ``height`` (float): Высота области аннотации
- ``start`` (integer): Начальная позиция в тексте
- ``end`` (integer): Конечная позиция в тексте

Объект изображения (Image)
~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``original_name`` (string): Исходное имя файла
- ``tmp_file_path`` (string): Временный путь к файлу
- ``uuid`` (string): Уникальный идентификатор
- ``x_top_left`` (float): X-координата верхнего левого угла
- ``y_top_left`` (float): Y-координата верхнего левого угла
- ``width`` (float): Ширина изображения
- ``height`` (float): Высота изображения
- ``page_num`` (integer): Номер страницы с изображением