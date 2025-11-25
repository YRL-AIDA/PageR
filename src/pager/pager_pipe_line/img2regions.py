from pager import RegionModel, WordsModel, Words2Rows, Image2Rows, RowsModel, ImageModel, Image2Words, Rows2Regions
from pager import Words2OneRegion
from pager import PrecisionPDFModel, Image2PrecisionPDF, PrecisionPDFRegionsFromPhisExtractor
from pager import PageModel, PageModelUnit

img_unit = PageModelUnit(id = "img",
                        sub_model=ImageModel(),
                        extractors=[],
                        converters={})
word_unit = PageModelUnit(id = "words",
                        sub_model=WordsModel(),
                        extractors=[],
                        converters={"img": Image2Words()})

# Либо из слов, либо из изображения ==============================
row_unit_w = PageModelUnit(id = "rows", 
                         sub_model=RowsModel(),
                        extractors=[],
                        converters={"words": Words2Rows()})
row_unit_i = PageModelUnit(id = "rows",
                        sub_model=RowsModel(),
                        extractors=[],
                        converters={"img": Image2Rows()})
# ================================================================

regions_unit = PageModelUnit(id = "regions",
                        sub_model=RegionModel(),
                        extractors=[],
                        converters={"rows": Rows2Regions()})

one_region_unit = PageModelUnit(id = "regions",
                                sub_model=RegionModel(),
                                extractors=[],
                                converters={"words": Words2OneRegion()})


img2region_word = PageModel([img_unit, 
                            word_unit,
                            row_unit_w,
                            regions_unit])

img2region_row = PageModel([img_unit, 
                            row_unit_i,
                            regions_unit])

img2one_region = PageModel([img_unit,
                            word_unit,
                            one_region_unit])



# JSON --------------------------------------------------------------------------
precision_pdf = PrecisionPDFModel()
precision_pdf.num_page = 0

img2json_word = PageModel([img_unit, PageModelUnit("pdf", precision_pdf, extractors=[], converters={"img":Image2PrecisionPDF()}),
                        word_unit,
                        row_unit_w,
                        regions_unit,
                        PageModelUnit("json", precision_pdf, extractors=[PrecisionPDFRegionsFromPhisExtractor(regions_unit.sub_model)], converters={})])

img2json_row = PageModel([img_unit, PageModelUnit("pdf", precision_pdf, extractors=[], converters={"img":Image2PrecisionPDF()}), 
                        row_unit_i,
                        regions_unit,
                        PageModelUnit("json", precision_pdf, extractors=[PrecisionPDFRegionsFromPhisExtractor(regions_unit.sub_model)], converters={})])

img2json_one = PageModel([img_unit, PageModelUnit("pdf", precision_pdf, extractors=[], converters={"img":Image2PrecisionPDF()}),
                        word_unit,
                        one_region_unit,
                        PageModelUnit("json", precision_pdf, extractors=[PrecisionPDFRegionsFromPhisExtractor(one_region_unit.sub_model)], converters={})])

