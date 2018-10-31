from io import BytesIO

import openpyxl


def autofit_databook(db):
    """Autofit databook columns."""
    wb_in = openpyxl.load_workbook(BytesIO(db.xlsx))
    wb_out = openpyxl.Workbook()
    for idx, sheet_name in enumerate(wb_in.sheetnames):

        ws_in = wb_in.get_sheet_by_name(sheet_name)
        ws_out = wb_out.create_sheet(sheet_name, idx)
        ws_out.freeze_panes = 'A2'

        for row in ws_in.rows:
            new_row = []
            for value in row:
                new_row.append(value.value)
            ws_out.append(new_row)

        for column_cells in ws_out.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            ws_out.column_dimensions[column_cells[0].column].width = length

    return wb_out
