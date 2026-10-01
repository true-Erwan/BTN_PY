    import random
    import json
    import os

    FICHIER_RECORDS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "records.json")


    class Vehicule(dict):
        def __init__(self, nom, taille, id):
            super().__init__(nom=nom, taille=taille, id=id, touches=set(), cases=[])

        def positions(self, n, p):
            t = self["taille"]
            pos = []
            for y in range(n):
                for x in range(n):
                    if x + t <= n and all(p[y][x + i] == 0 for i in range(t)):
                        pos.append([(x + i, y) for i in range(t)])
                    if t > 1 and y + t <= n and all(p[y + i][x] == 0 for i in range(t)):
                        pos.append([(x, y + i) for i in range(t)])
            return pos


    class Blinde(Vehicule):
        def __init__(self, id):
            super().__init__("Blinde", 4, id)

        def positions(self, n, p):
            return [
                [(x + dx, y + dy) for dy in (0, 1) for dx in (0, 1)]
                for y in range(n - 1) for x in range(n - 1)
                if all(p[y + dy][x + dx] == 0 for dy in (0, 1) for dx in (0, 1))
            ]


    def creer_parking(taille):
        return [[0] * taille for _ in range(taille)]


    def vehicules_rallye():
        return [
            Vehicule("Kei Car", 1, 1),
            Vehicule("GT-R R34", 2, 2),
        ]


    def vehicules_grand_prix():
        return [
            Vehicule("Limousine VIP", 5, 1),
            Blinde(2),
            Vehicule("Formule 1", 3, 3),
            Vehicule("GT-R R34", 2, 4),
            Vehicule("Kei Car", 1, 5),
        ]


    def placer_tous_vehicules(parking, flotte):
        places = {}
        n = len(parking)
        for v in flotte:
            choix = v.positions(n, parking)
            if not choix:
                return None
            v["cases"] = random.choice(choix)
            for cx, cy in v["cases"]:
                parking[cy][cx] = v["id"]
            places[v["id"]] = v
        return places


    def nouvelle_partie(mode):
        taille = 5 if mode == "rallye" else 8
        flotte = vehicules_rallye() if mode == "rallye" else vehicules_grand_prix()

        for _ in range(200):
            parking = creer_parking(taille)
            vehicules = placer_tous_vehicules(parking, flotte)
            if vehicules is not None:
                return {
                    "parking": parking,
                    "taille": taille,
                    "mode": mode,
                    "vehicules": vehicules,
                    "cases_flashees": {},
                    "nb_scans": 0,
                    "radar_utilise": False,
                    "fini": False,
                    "tour": 1,
                    "or": 0,
                }
        return None


    PRIX_BOUTIQUE = {
        "scan": 20,
        "bombe_croix": 40,
        "bombe_ligne_colonne": 80,
    }


    def terminer_tour(partie):
        partie["tour"] += 1
        if partie["mode"] == "grand_prix":
            partie["or"] += 10


    def est_epave(vehicule):
        return len(vehicule["touches"]) >= vehicule["taille"]


    def tous_epaves(vehicules):
        return all(est_epave(v) for v in vehicules.values())


    def tirer_sur_case(partie, x, y):
        if (x, y) in partie["cases_flashees"]:
            return {"x": x, "y": y, "resultat": "deja_scanne"}

        id_v = partie["parking"][y][x]

        if id_v == 0:
            partie["cases_flashees"][(x, y)] = "vide"
            return {"x": x, "y": y, "resultat": "vide"}

        v = partie["vehicules"][id_v]
        v["touches"].add((x, y))
        partie["cases_flashees"][(x, y)] = "touche"

        if est_epave(v):
            for cx, cy in v["cases"]:
                partie["cases_flashees"][(cx, cy)] = "epave"
            partie["fini"] = tous_epaves(partie["vehicules"])
            return {"x": x, "y": y, "resultat": "epave", "vehicule": v["nom"], "cases": v["cases"]}

        return {"x": x, "y": y, "resultat": "touche", "vehicule": v["nom"]}


    def flasher_case(partie, x, y):
        if (x, y) in partie["cases_flashees"]:
            return {"resultat": "deja_scanne"}
        partie["nb_scans"] += 1
        res = tirer_sur_case(partie, x, y)
        terminer_tour(partie)
        return res


    def scanner_zone(partie, x, y):
        t, p = partie["taille"], partie["parking"]
        zone = [(x + dx, y + dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if 0 <= x + dx < t and 0 <= y + dy < t]
        if p[y][x] != 0:
            adjacents = {c: p[c[1]][c[0]] != 0 for c in zone if c != (x, y)}
            return {"type": "contact", "centre": (x, y), "adjacents": adjacents, "zone": zone}
        compteur = sum(1 for cx, cy in zone if p[cy][cx] != 0)
        return {"type": "balayage", "centre": (x, y), "compteur": compteur, "zone": zone}


    def scan_radar(partie, x, y):
        if partie["radar_utilise"]:
            return None
        partie["radar_utilise"] = True
        partie["nb_scans"] += 1
        terminer_tour(partie)
        return scanner_zone(partie, x, y)


    def acheter_scan_radar(partie, x, y):
        if partie["or"] < PRIX_BOUTIQUE["scan"]:
            return {"erreur": "or_insuffisant"}
        partie["or"] -= PRIX_BOUTIQUE["scan"]
        partie["nb_scans"] += 1
        terminer_tour(partie)
        return scanner_zone(partie, x, y)


    def tirer_bombe_croix(partie, x, y):
        prix = PRIX_BOUTIQUE["bombe_croix"]
        if partie["or"] < prix:
            return {"erreur": "or_insuffisant"}
        partie["or"] -= prix
        partie["nb_scans"] += 1
        t = partie["taille"]

        candidats = [(x, y), (x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]
        cases = [(cx, cy) for cx, cy in candidats if 0 <= cx < t and 0 <= cy < t]
        impacts = [tirer_sur_case(partie, cx, cy) for cx, cy in cases]
        terminer_tour(partie)
        return {"type": "bombe_croix", "centre": (x, y), "impacts": impacts}


    def tirer_bombe_ligne_colonne(partie, x, y):
        prix = PRIX_BOUTIQUE["bombe_ligne_colonne"]
        if partie["or"] < prix:
            return {"erreur": "or_insuffisant"}
        partie["or"] -= prix
        partie["nb_scans"] += 1
        t = partie["taille"]

        cases = {(i, y) for i in range(t)} | {(x, i) for i in range(t)}
        impacts = [tirer_sur_case(partie, cx, cy) for cx, cy in sorted(cases)]
        terminer_tour(partie)
        return {"type": "bombe_ligne_colonne", "centre": (x, y), "impacts": impacts}


    def charger_records():
        try:
            with open(FICHIER_RECORDS, "r") as f:
                return json.load(f)
        except Exception:
            return {"rallye": None, "grand_prix": None}


    def sauvegarder_record(mode, score):
        records = charger_records()
        if records.get(mode) is None or score < records[mode]:
            records[mode] = score
            with open(FICHIER_RECORDS, "w") as f:
                json.dump(records, f)
            return True
        return False
