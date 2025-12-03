from pager import PageModelUnit, PageModel, ImageModel, PDFModel, PDF2Img

pdf2img = PageModel([
    PageModelUnit(id ='pdf', 
                  sub_model=PDFModel(), 
                  extractors=[], 
                  converters={}),
    PageModelUnit(id ='img', 
                  sub_model=ImageModel(), 
                  extractors=[], 
                  converters={"pdf": PDF2Img()})
])