from pager import RegionModel, WordsModel, Words2Rows, RowsModel, PDFModel, PDF2Words, PDF2Rows, ImageFromPDF, Rows2Regions
from pager import Words2OneRegion
from pager import PageModel, PageModelUnit
from pager import ImageFromPDF
from pager.doc_model import PrecisionPDFModel

# Либо извлекать строки, либо извлекать сразу слова
unit_pdf_w = PageModelUnit(id = "pdf",
                        sub_model=PDFModel({"method": "w"}),
                        extractors=[],
                        converters={})
unit_pdf_r = PageModelUnit(id = "pdf",
                        sub_model=PDFModel({"method": "r"}),
                        extractors=[],
                        converters={})
unit_words = PageModelUnit(
        id = "words",
        sub_model=WordsModel(),
        extractors=[],
        converters={"pdf": PDF2Words()}
    )

unit_rows_p = PageModelUnit(id = "rows",
                            sub_model=RowsModel(),
                            extractors=[ImageFromPDF(unit_pdf_r.sub_model)],
                            converters={"pdf": PDF2Rows()}
)
unit_rows_w = PageModelUnit(id = "rows",
                            sub_model=RowsModel(),
                            extractors=[ImageFromPDF(unit_pdf_w.sub_model)],
                            converters={"words": Words2Rows()}
)

unit_regions = PageModelUnit(id = "regions",
                             sub_model=RegionModel(),
                             extractors=[],
                             converters={"rows": Rows2Regions()})

one_region_unit = PageModelUnit(id = "regions",
                                sub_model=RegionModel(),
                                extractors=[],
                                converters={"words": Words2OneRegion()})



# -------------------------------------------------------------------------------

pdf2region_word = PageModel([
    unit_pdf_w,
    unit_words,
    unit_rows_w,
    unit_regions
])

pdf2region_row = PageModel([
    unit_pdf_r,
    unit_rows_p,
    unit_regions
])

pdf2one_region = PageModel([unit_pdf_w,
                            unit_words,
                            one_region_unit])


# JSON --------------------------------------------------------------------------

pdf2json_word = PrecisionPDFModel({"page_model": pdf2region_word}) 
pdf2json_row = PrecisionPDFModel({ "page_model": pdf2region_row}) 
pdf2json_one = PrecisionPDFModel({ "page_model": pdf2one_region}) 