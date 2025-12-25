from ..base_sub_model import BaseConverter
from ..pdf_model import PDFModel
from ..rows_model import RowsModel
from ..dtype import Row

class PDF2Rows(BaseConverter):
    def convert(self, input_model: PDFModel, output_model: RowsModel):
        page_json = input_model.to_dict()
        rows_list = self.get_rows(page_json['rows'])
        output_model.rows = rows_list

    def get_rows(self, rows_json):
        rows = []
        for row in rows_json:
            if not self.is_correct_row(row):
                continue
            rows.append(Row(row))
        return rows
    
    def is_correct_row(self, row_json):
        if row_json["segment"]["height"] < 1 or row_json["segment"]["width"] < 1:
            return False
        return True