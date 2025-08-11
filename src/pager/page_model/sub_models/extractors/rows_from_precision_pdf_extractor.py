from ..base_sub_model import BaseExtractor
from ..pdf_model import PrecisionPDFModel
from ..rows_model import RowsModel
from ..exceptions import ConteinNumPage
from ..dtype.block import Row


class RowsFromPrecisionPDFExtractor(BaseExtractor):
    def __init__(self, precision_pdf:PrecisionPDFModel):
        self.precision_pdf = precision_pdf
        if not "num_page" in self.precision_pdf.__dict__:
            raise ConteinNumPage()

    def extract(self, model:RowsModel):
        json_pdf = self.precision_pdf.to_dict()
        json_rows = json_pdf["pages"][self.precision_pdf.num_page]['blocks']
        rows_list = self.get_rows(json_rows)
        model.rows = rows_list

    def get_rows(self, rows_json:list[dict]):
        rows = []
        for row in rows_json:
            row_dict = row.copy()
            if row_dict["height"] < 1 or row_dict["width"] < 1 or row_dict["height"] > 25:
                continue
            row_dict["segment"] = row_dict 
            rows.append(Row(row_dict))
        return rows