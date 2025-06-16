import openpyxl

def _load_sheet(file_path, sheet_name="Sheet1"):
    wb = openpyxl.load_workbook(file_path, data_only=True)
    return wb[sheet_name]

def extract_vessel(sheet):
    return _safe_cell(sheet, "O23")

def extract_pol(sheet):
    return _safe_cell(sheet, "AK23")

def extract_pod(sheet):
    return _safe_cell(sheet, "AK24")

def extract_container_number(sheet):
    return _safe_cell(sheet, "AK25")

def extract_eta(sheet):
    return _safe_cell(sheet, "BB23")

def extract_etd(sheet):
    return _safe_cell(sheet, "BB24")

def extract_seal_no(sheet):
    return _safe_cell(sheet, "BV23")

def _safe_cell(sheet, coord):
    value = sheet[coord].value
    return str(value).strip() if value else ""
