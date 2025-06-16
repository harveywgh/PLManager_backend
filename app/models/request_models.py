from pydantic import BaseModel

class UploadFileRequest(BaseModel):
    fournisseur: str
    file_path: str
    output_dir: str

class CSVSettings(BaseModel):
    country_of_origin: str
    forwarder: str
    importer: str