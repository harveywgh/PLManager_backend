from fastapi import APIRouter, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import uuid
import shutil
import pandas as pd
from fastapi import File, Form
from ..services.southern_fruit_alliance.southern_fruit_alliance_service import SFAService
from ..services.sunny.sunny_service import SunnyService
from ..services.safpro.safpro_service import SafproService
from ..services.alg.alg_service import AlgService
from ..services.langplaas.langplaas_service import LangplaasService
from ..services.athos.athos_service import AthosService
from ..services.asica.asica_service import AsicaService
from ..services.angon.angon_service import AngonService
from ..services.gh.gh_service import GHService
from ..services.cpf.cpf_service import CpfService
from ..services.unifruitti.unifruitti_service import UnifruittiService
from ..services.jaguacy.jaguacy_service import JaguacyService


router = APIRouter()
OUTPUT_DIR = "/outputs" 
BASE_EXPORT_DIR = os.getenv("EXPORT_DIR", "outputs")  # configurable depuis .env

extraction_records = {}

FOURNISSEURS_SUPPORTES = {
    "Komati": SFAService,
    "Grosa": SFAService,
    "ZestFruit": SFAService,
    "Mahela": SFAService,
    "Sunny": SunnyService,
    "Safpro": SafproService,
    "ALG": AlgService,
    "Langplaas": LangplaasService,
    "Exportadora Fruticola Athos": AthosService,
    "Asica": AsicaService,
    "Laran": AsicaService,
    "Jaguacy": JaguacyService,
    "Angon": AngonService,
    "Agualima": AsicaService,
    "Camposol": AsicaService,
    "CPF": CpfService,
    "Mosqueta": UnifruittiService,
    "Pirona": UnifruittiService,
    "Hefei": UnifruittiService,
}

# Dictionnaire pour stocker temporairement les paramètres CSV
csv_settings_store = {}

class CSVSettings(BaseModel):
    country_of_origin: str
    forwarder: str
    importer: str
    archive: str

@router.post("/csv-settings/")
async def save_csv_settings(settings: CSVSettings):
    """
    Enregistre les paramètres CSV envoyés par le front.
    """
    csv_settings_store["settings"] = settings.dict()
    print("📌 Paramètres CSV enregistrés après correction :", csv_settings_store["settings"]) 
    return {"message": "Paramètres enregistrés avec succès"}


@router.get("/csv-settings/")
async def get_csv_settings():
    """
    Récupère les paramètres CSV enregistrés.
    """
    if "settings" not in csv_settings_store:
        raise HTTPException(status_code=404, detail="Aucun paramètre trouvé")
    return csv_settings_store["settings"]

@router.post("/archives-file/{fournisseur}/")
async def process_file(fournisseur: str, file: UploadFile):
    """Traite un fichier et génère un identifiant d’extraction unique."""
    print(f"📂 Requête reçue pour extraction - Fournisseur : {fournisseur}")

    if fournisseur not in FOURNISSEURS_SUPPORTES:
        raise HTTPException(status_code=400, detail=f"Fournisseur '{fournisseur}' non pris en charge.")

    try:
        os.makedirs("archives", exist_ok=True)

        file_location = f"archives/{file.filename}"
        with open(file_location, "wb") as buffer:
            buffer.write(file.file.read())
        print(f"📥 Fichier enregistré à {file_location}")

        output_dir = "outputs/"
        os.makedirs(output_dir, exist_ok=True)

        service_class = FOURNISSEURS_SUPPORTES[fournisseur]()
        
        if "settings" in csv_settings_store:
            service_class.apply_csv_settings(csv_settings_store["settings"])
            service_class.csv_settings["Fournisseur"] = fournisseur

        
        # ✅ Générer un identifiant unique pour l’extraction
        extraction_id = str(uuid.uuid4())

        # ✅ Traitement du fichier et récupération des fichiers générés
        generated_files = service_class.process_file(file_location, output_dir)

        # ✅ Vérifie que `generated_files` est bien une liste
        if not isinstance(generated_files, list):
            print("❌ ERREUR: `generated_files` n'est pas une liste valide !")
            raise HTTPException(status_code=500, detail="Erreur interne: format des fichiers invalides.")

        # ✅ Stocker les fichiers avec leur extraction_id
        extraction_records[extraction_id] = generated_files

        print(f"✅ Extraction ID enregistré : {extraction_id}")
        print(f"✅ Fichiers associés : {extraction_records[extraction_id]}")

        return {
            "extraction_id": extraction_id,
            "message": f"Extraction terminée pour {fournisseur}.",
            "generated_files": extraction_records[extraction_id]
        }

    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement du fichier : {str(e)}")
 
    
@router.get("/get-extraction-files/{extraction_id}/")
async def get_extraction_files(extraction_id: str):
    """
    Retourne la liste des fichiers générés pour une extraction spécifique.
    """
    if extraction_id not in extraction_records:
        print(f"❌ Aucun fichier trouvé pour extraction_id={extraction_id}")
        raise HTTPException(status_code=404, detail="Aucun fichier trouvé pour cet extraction_id.")

    # 🔹 Supprime un éventuel double préfixe "/outputs/" en normalisant les chemins
    normalized_files = [os.path.relpath(f, start="outputs") for f in extraction_records[extraction_id]]

    print(f"📡 Fichiers trouvés pour extraction_id={extraction_id}: {normalized_files}")
    return {"extraction_id": extraction_id, "files": normalized_files}



@router.get("/get-csv/{extraction_id}/")
async def get_csv(extraction_id: str):
    print(f"📌 DEBUG API: Requête reçue pour extraction_id={extraction_id}")

    # ✅ Vérifie que l'extraction_id existe
    if extraction_id not in extraction_records:
        print(f"❌ Aucun fichier trouvé pour extraction_id={extraction_id}")
        raise HTTPException(status_code=404, detail="Aucun fichier trouvé.")

    # ✅ Vérifie que `extraction_records[extraction_id]` est une liste non vide
    csv_files = extraction_records[extraction_id]
    if not csv_files or not isinstance(csv_files, list):
        print(f"❌ ERREUR: `extraction_records[{extraction_id}]` est vide ou mal formaté.")
        raise HTTPException(status_code=500, detail="Erreur interne: aucune liste de fichiers disponible.")

    print(f"✅ DEBUG: Fichiers retournés pour extraction_id={extraction_id}: {csv_files}")

    return {"extraction_id": extraction_id, "files": csv_files}



@router.get("/download-csv/")
async def download_csv(file_path: str):
    """
    📥 Télécharge un fichier CSV depuis le serveur via HTTP.
    Le file_path est relatif au dossier d'export configuré.
    """
    # 🔹 Nettoyage du chemin reçu
    file_path = file_path.replace("\\", "/").strip()

    # 🔒 Protection contre les chemins dangereux
    if ".." in file_path or file_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Chemin de fichier non autorisé.")

    # 🔧 Corriger si on reçoit un chemin déjà préfixé (protection double outputs/)
    if file_path.startswith(BASE_EXPORT_DIR + "/"):
        file_path = file_path[len(BASE_EXPORT_DIR) + 1:]

    # 📁 Construction du chemin absolu
    full_path = os.path.abspath(os.path.join(BASE_EXPORT_DIR, file_path))
    filename = os.path.basename(file_path)

    # 📥 Vérification et réponse
    if os.path.exists(full_path):
        print(f"📌 Téléchargement du fichier : {full_path}")
        return FileResponse(full_path, filename=filename)

    print(f"❌ Erreur: Le fichier {full_path} est introuvable.")
    raise HTTPException(status_code=404, detail="Fichier introuvable")


@router.put("/update-csv/")
async def update_csv(file: UploadFile = File(...), csv_path: str = Form(...)):
    print(f"📌 DEBUG: Chemin reçu pour mise à jour : {csv_path}")

    try:
        csv_path = csv_path.replace("\\", "/").strip()

        if not csv_path.startswith("outputs/"):
            print(f"❌ ERREUR: Chemin invalide reçu, mise à jour interdite -> {csv_path}")
            raise HTTPException(status_code=400, detail="Mise à jour interdite en dehors de outputs/")

        if not os.path.exists(csv_path):
            print(f"❌ ERREUR: Fichier introuvable - {csv_path}")
            raise HTTPException(status_code=404, detail=f"Fichier introuvable : {csv_path}")

        # 📥 Lecture du CSV envoyé
        df = pd.read_csv(file.file, sep=";", encoding="utf-8")
        print(f"📊 Fichier reçu - lignes : {len(df)}")

        for idx, row in df.iterrows():
            if row.isnull().all() or all(str(c).strip() == '' for c in row):
                print(f"⚠️ Ligne {idx} vide")
            else:
                print(f"➡️ [{idx}] {row.values}")

        if df.empty:
            raise HTTPException(status_code=400, detail="Le fichier CSV envoyé est vide.")

        os.chmod(csv_path, 0o777)

        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            df.to_csv(f, sep=";", index=False, lineterminator="\n")
            f.flush()
            os.fsync(f.fileno())

        # 📄 Vérification post-écriture
        df_check = pd.read_csv(csv_path, sep=";", encoding="utf-8")
        print(f"📄 Après écriture : {len(df_check)} lignes")
        for i, row in df_check.iterrows():
            print(f"✔️ ligne {i} : {row.values}")

        return {"message": "Fichier CSV mis à jour avec succès"}

    except Exception as e:
        print(f"❌ ERREUR lors de la mise à jour : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour : {str(e)}")
