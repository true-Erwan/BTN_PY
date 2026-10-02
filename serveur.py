import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import webbrowser
import threading
import time

from moteur_jeu import (
    nouvelle_partie, flasher_case, scan_radar,
    acheter_scan_radar, tirer_bombe_croix, tirer_bombe_ligne_colonne,
    PRIX_BOUTIQUE, charger_records, sauvegarder_record
)

app = FastAPI(title="Traque Urbaine API")

DOSSIER_RACINE = os.path.dirname(os.path.abspath(__file__))
DOSSIER_WEB = os.path.join(DOSSIER_RACINE, "web")
DOSSIER_SONS = os.path.join(DOSSIER_RACINE, "sons")

partie_courante = None


class RequeteMode(BaseModel):
    mode: str


class RequeteCoordonnees(BaseModel):
    x: int
    y: int


class RequeteBoutique(BaseModel):
    action: str
    x: int
    y: int


@app.get("/api/records")
def api_records():
    return charger_records()


@app.post("/api/partie")
def api_nouvelle_partie(req: RequeteMode):
    global partie_courante
    p = nouvelle_partie(req.mode)
    if not p:
        raise HTTPException(status_code=500, detail="Impossible d'initialiser le parking")
    partie_courante = p
    return formater_etat_partie()


@app.post("/api/flash")
def api_flash(req: RequeteCoordonnees):
    global partie_courante
    if not partie_courante or partie_courante["fini"]:
        raise HTTPException(status_code=400, detail="Aucune partie active")
    
    resultat = flasher_case(partie_courante, req.x, req.y)
    
    nouveau_record = False
    if partie_courante["fini"]:
        nouveau_record = sauvegarder_record(partie_courante["mode"], partie_courante["nb_scans"])
        
    return {
        "resultat": resultat,
        "partie": formater_etat_partie(),
        "nouveau_record": nouveau_record
    }


@app.post("/api/radar")
def api_radar(req: RequeteCoordonnees):
    global partie_courante
    if not partie_courante or partie_courante["fini"]:
        raise HTTPException(status_code=400, detail="Aucune partie active")
    
    resultat = scan_radar(partie_courante, req.x, req.y)
    if resultat is None:
        raise HTTPException(status_code=400, detail="Radar deja utilise")
        
    if resultat.get("type") == "contact":
        resultat["cases_occupees"] = [
            [c[0], c[1]] for c in resultat.get("cases_occupees", [])
        ]
        resultat["adjacents"] = {
            f"{c[0]},{c[1]}": occ for c, occ in resultat["adjacents"].items()
        }
        
    return {
        "radar": resultat,
        "partie": formater_etat_partie()
    }


@app.post("/api/shop/action")
def api_shop_action(req: RequeteBoutique):
    global partie_courante
    if not partie_courante or partie_courante["fini"]:
        raise HTTPException(status_code=400, detail="Aucune partie active")

    if req.action == "scan":
        resultat = acheter_scan_radar(partie_courante, req.x, req.y)
    elif req.action == "bombe_croix":
        resultat = tirer_bombe_croix(partie_courante, req.x, req.y)
    elif req.action == "bombe_ligne_colonne":
        resultat = tirer_bombe_ligne_colonne(partie_courante, req.x, req.y)
    else:
        raise HTTPException(status_code=400, detail="Action boutique inconnue")

    if isinstance(resultat, dict) and "erreur" in resultat:
        raise HTTPException(status_code=400, detail=resultat["erreur"])

    if req.action == "scan" and resultat.get("type") == "contact":
        resultat["cases_occupees"] = [
            [c[0], c[1]] for c in resultat.get("cases_occupees", [])
        ]
        resultat["adjacents"] = {
            f"{c[0]},{c[1]}": occ for c, occ in resultat["adjacents"].items()
        }

    nouveau_record = False
    if partie_courante["fini"]:
        nouveau_record = sauvegarder_record(partie_courante["mode"], partie_courante["nb_scans"])

    return {
        "action": req.action,
        "resultat": resultat,
        "partie": formater_etat_partie(),
        "nouveau_record": nouveau_record
    }


def formater_etat_partie():
    if not partie_courante:
        return None
    
    cases_flashees_str = {
        f"{x},{y}": etat
        for (x, y), etat in partie_courante["cases_flashees"].items()
    }
    
    vehicules_info = {}
    for vid, v in partie_courante["vehicules"].items():
        epave = len(v["touches"]) >= v["taille"]
        vehicules_info[vid] = {
            "nom": v["nom"],
            "taille": v["taille"],
            "touches": len(v["touches"]),
            "epave": epave,
            "cases": v["cases"] if epave else []
        }
        
    return {
        "taille": partie_courante["taille"],
        "mode": partie_courante["mode"],
        "nb_scans": partie_courante["nb_scans"],
        "radar_utilise": partie_courante["radar_utilise"],
        "tour": partie_courante.get("tour", 1),
        "or": partie_courante.get("or", 0),
        "prix_boutique": PRIX_BOUTIQUE,
        "fini": partie_courante["fini"],
        "cases_flashees": cases_flashees_str,
        "vehicules": vehicules_info,
        "records": charger_records()
    }


if os.path.exists(DOSSIER_SONS):
    app.mount("/sons", StaticFiles(directory=DOSSIER_SONS), name="sons")

if os.path.exists(DOSSIER_WEB):
    app.mount("/static", StaticFiles(directory=DOSSIER_WEB), name="static")

@app.get("/")
def index():
    return FileResponse(
        os.path.join(DOSSIER_WEB, "index.html"),
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )


def ouvrir_navigateur():
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:8000")


if __name__ == "__main__":
    print("Demarrage du serveur Traque Urbaine sur http://127.0.0.1:8000 ...")
    threading.Thread(target=ouvrir_navigateur, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
