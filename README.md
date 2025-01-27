# Page Reader (PageR)

## Содержание
- [Установка](#установка)
- [Информация для разработчиков](#информация-для-разработчиков)


## Установка
Предварительно установить
- [OCR-Tesseract](https://tesseract-ocr.github.io/tessdoc/Installation.html)
- [Java-PDF-Parser](https://github.com/YRL-AIDA/Java-PDF-Parser/tree/main)

Создать переменную 
```
export JAR_PDF_PARSER="Java-PDF-Parser.jar"
export PATH_SEG_MODEL="PageR/models/segmodel"
export PATH_CLASS_MODEL="PageR/models/classmodel"
export PATH_TORCH_SEG_GNN_MODEL="PageR/models/seg_gnn"
export PATH_TORCH_SEG_LINEAR_MODEL="PageR/models/seg_linear"
export PATH_STYLE_MODEL="PageR/models/style_classmodel_20250121"
```

```
python -m pip install .
```


## Информация для разработчиков
<!--описание коммитов-->
### Описание коммитов
| Название | Описание                                                        |
|----------|-----------------------------------------------------------------|
| build	   | Сборка проекта или изменения внешних зависимостей               |
| sec      | Безопасность, уязвимости                                        |
| ci       | Настройка CI и работа со скриптами                              |
| docs	   | Обновление документации                                         |
| comment  | Добавление комментариев в коде и readme                         |
| feat	   | Добавление нового функционала                                   |
| fix	   | Исправление ошибок                                              |
| perf	   | Изменения направленные на улучшение производительности          |
| refactor | Правки кода без исправления ошибок или добавления новых функций |
| revert   | Откат на предыдущие коммиты                                     |
| style	   | Правки по кодстайлу (табы, отступы, точки, запятые и т.д.)      |
| test	   | Добавление тестов                                               |

<!--структура проекта -->
### Структура проекта
```
.
├── pager - папка проекта
|   └── page_model - папка модели страницы
|   |   ├── image2phis.py - модель от изображения к структурее
|   |   ├── page_model.py - базовая модель страницы (собираемой из блоков)
|   |   └── sub_models - блоки модели
|   |   |   ├── base_sub_model.py  - базовая модель блока
|   |   |   ├── dtype - типы данных
|   |   |   ├── image_model - блок изображения
|   |   |   ├── pdf_model - блок pdf
|   |   |   ├── words_model - блок работы со словами
|   |   |   ├── words_and_styles_model - блок работы со словами их стилями
|   |   |   └── phisical_model -блок работы с физическими сегментами
```
