def is_cell_empty(ws, row, column):
    value = ws.cell(row, column).value
    return value is None or str(value).strip() == ""