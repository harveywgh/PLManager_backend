import os

UPLOAD_DIR = "Archives/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_temp_file(uploaded_file):
    """
    Sauvegarde un fichier temporaire dans le dossier 'Archives'.
    """
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(uploaded_file.file.read())
    return file_path
