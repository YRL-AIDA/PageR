from pager import PageModel, PageModelUnit, PrecisionPDFModel, MSWordModel, PrecisionPDFToMSWord


unit_json_precision_pdf = PageModelUnit("json_precision_pdf", PrecisionPDFModel(), extractors=[], converters={})
unit_ms_word = PageModelUnit("ms_word", MSWordModel(), extractors=[], converters={"json_precision_pdf": PrecisionPDFToMSWord()})

json2docx = PageModel(page_units=[
    unit_json_precision_pdf,
    unit_ms_word
])