import pygame
import sys
import math
import random
import os

from moteur_jeu import (
    nouvelle_partie, flasher_case, scan_radar, est_epave,
    acheter_scan_radar, tirer_bombe_croix, tirer_bombe_ligne_colonne,
    PRIX_BOUTIQUE, charger_records, sauvegarder_record
)

LARGEUR, HAUTEUR = 1200, 800
FPS = 60

NOIR            = (8, 8, 12)
ASPHALTE        = (30, 32, 38)
ASPHALTE_CLAIR  = (45, 47, 55)
MARQUAGE        = (130, 132, 140)
JAUNE           = (220, 190, 40)
CYAN            = (0, 220, 255)
CYAN_SOMBRE     = (0, 50, 70)
ROUGE           = (230, 50, 40)
ORANGE          = (240, 140, 30)
VERT            = (40, 220, 80)
VERT_RADAR      = (0, 255, 130)
BLANC           = (210, 212, 220)
GRIS            = (100, 102, 110)
GRIS_SOMBRE     = (60, 62, 68)
PANNEAU_BG      = (18, 20, 26)
PANNEAU_BORD    = (40, 42, 50)

COULEURS_V = {
    "Kei Car":       (255, 220, 50),
    "GT-R R34":      (160, 80, 245),
    "Formule 1":     (230, 40, 40),
    "Blinde":        (110, 145, 65),
    "Limousine VIP": (230, 195, 60),
}

MENU, JEU, VICTOIRE = "menu", "jeu", "victoire"
DOSSIER_SONS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sons")


def charger_sons():
    sons = {}
    if os.path.exists(DOSSIER_SONS):
        for f in os.listdir(DOSSIER_SONS):
            nom, ext = os.path.splitext(f)
            if ext.lower() in (".wav", ".mp3", ".ogg"):
                try:
                    sons[nom] = pygame.mixer.Sound(os.path.join(DOSSIER_SONS, f))
                except Exception:
                    pass
    return sons


class Particule:
    def __init__(self, x, y, couleur, vx=0, vy=0, taille=2, vie=30, gravite=0):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.couleur = couleur
        self.taille = taille
        self.vie = self.vie_max = vie
        self.gravite = gravite

    def maj(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravite
        self.vie -= 1
        return self.vie > 0

    def dessiner(self, ecran):
        r = max(1, int(self.taille * (self.vie / self.vie_max)))
        pygame.draw.circle(ecran, self.couleur, (int(self.x), int(self.y)), r)


def emettre_particules(parts, x, y, genre, nb=10):
    for _ in range(nb):
        if genre == "etincelles":
            a, v = random.uniform(0, 6.28), random.uniform(1.5, 4.0)
            parts.append(Particule(x, y, random.choice([ORANGE, ROUGE, JAUNE]),
                                   math.cos(a)*v, math.sin(a)*v, random.randint(1, 3), random.randint(15, 30)))
        elif genre == "fumee":
            g = random.randint(70, 120)
            parts.append(Particule(x + random.uniform(-4, 4), y, (g, g, g),
                                   random.uniform(-0.3, 0.3), random.uniform(-1.0, -0.3), random.randint(2, 4), 35))
        elif genre == "confetti":
            a, v = random.uniform(0, 6.28), random.uniform(2, 6)
            c = random.choice([CYAN, ORANGE, VERT, JAUNE, ROUGE, (255, 120, 255)])
            parts.append(Particule(x, y, c, math.cos(a)*v, math.sin(a)*v - 3, random.randint(2, 4), 60, 0.08))


def texte_centre(ecran, police, texte, y, couleur):
    surf = police.render(texte, True, couleur)
    ecran.blit(surf, (LARGEUR // 2 - surf.get_width() // 2, y))


def dessiner_bouton(ecran, police, texte, rect, c_fond, c_bord, survol=False, c_txt=BLANC):
    r = pygame.Rect(rect)
    fond = tuple(min(255, c + 20) for c in c_fond) if survol else c_fond
    bord = tuple(min(255, c + 40) for c in c_bord) if survol else c_bord
    pygame.draw.rect(ecran, fond, r, border_radius=8)
    pygame.draw.rect(ecran, bord, r, 2, border_radius=8)
    surf = police.render(texte, True, c_txt)
    ecran.blit(surf, (r.centerx - surf.get_width() // 2, r.centery - surf.get_height() // 2))
    return r


class TraqueUrbaine:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.audio_ok = True
        except Exception:
            self.audio_ok = False

        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("TRAQUE URBAINE — Détection Tactique")
        self.horloge = pygame.time.Clock()

        self.p_titre   = pygame.font.SysFont("consolas", 46, bold=True)
        self.p_grande  = pygame.font.SysFont("consolas", 28, bold=True)
        self.p_normale = pygame.font.SysFont("consolas", 18)
        self.p_petite  = pygame.font.SysFont("consolas", 14)

        self.sons = charger_sons()
        self.son_actif = True
        self.etat = MENU
        self.partie = None
        self.records = charger_records()

        self.mode_radar = False
        self.arme_active = None
        self.radar_info = None
        self.cellule_survol = None
        self.message_flash = None
        self.message_timer = 0
        self.flash_ecran = 0
        self.victoire_timer = 0
        self.nouveau_record = False
        self.anim_pings = []
        self.particules = []
        self.boutons = {}

        self.parts_menu = [
            {"x": random.randint(0, LARGEUR), "y": random.randint(0, HAUTEUR),
             "vx": random.uniform(-0.2, 0.2), "vy": random.uniform(-0.4, -0.05),
             "t": random.randint(1, 3), "a": random.randint(30, 80)}
            for _ in range(50)
        ]
        self.menu_timer = 0
        self.grille_x = self.grille_y = self.tc = 0

    def jouer_son(self, nom, duree_ms=None):
        if not (self.son_actif and self.audio_ok and nom in self.sons):
            return False
        try:
            if duree_ms:
                self.sons[nom].play(maxtime=int(duree_ms))
            else:
                self.sons[nom].play()
            return True
        except Exception:
            return False

    def demarrer_partie(self, mode):
        self.partie = nouvelle_partie(mode)
        self.etat = JEU
        self.mode_radar = False
        self.arme_active = None
        self.radar_info = None
        self.message_flash = None
        self.message_timer = self.flash_ecran = self.victoire_timer = 0
        self.anim_pings.clear()
        self.particules.clear()

        t = self.partie["taille"]
        self.tc = min(int(min(HAUTEUR - 150, LARGEUR * 0.48) / t), 100)
        self.grille_x = 80
        self.grille_y = (HAUTEUR - self.tc * t) // 2 + 15
        self.jouer_son("clic")

    def _clic_grille(self, pos):
        if not self.partie or self.partie["fini"]:
            return
        gx = (pos[0] - self.grille_x) // self.tc
        gy = (pos[1] - self.grille_y) // self.tc
        t = self.partie["taille"]
        if not (0 <= gx < t and 0 <= gy < t):
            return

        px = self.grille_x + gx * self.tc + self.tc // 2
        py = self.grille_y + gy * self.tc + self.tc // 2

        # Arme du shop
        if self.arme_active:
            arme = self.arme_active
            self.arme_active = None
            if arme == "scan":
                resultat = acheter_scan_radar(self.partie, gx, gy)
                if resultat and "erreur" not in resultat:
                    self.radar_info = resultat
                    self.jouer_son("radar")
                    self.anim_pings.append({"x": px, "y": py, "t": 0, "c": VERT_RADAR, "dur": 0.8})
                    self.message_flash, self.message_timer = "Scan radar (20G) effectué !", 2.0
                else:
                    self.message_flash, self.message_timer = "Or insuffisant (20 requis) !", 1.5
                return
            elif arme == "bombe_croix":
                resultat = tirer_bombe_croix(self.partie, gx, gy)
                if resultat and "erreur" not in resultat:
                    self.jouer_son("epave")
                    self.flash_ecran = 0.2
                    for imp in resultat.get("impacts", []):
                        if imp.get("resultat") in ("touche", "epave"):
                            cpx = self.grille_x + imp["x"] * self.tc + self.tc // 2
                            cpy = self.grille_y + imp["y"] * self.tc + self.tc // 2
                            emettre_particules(self.particules, cpx, cpy, "etincelles", 14)
                    self.message_flash, self.message_timer = "Bombe en croix déployée !", 2.0
                    if self.partie["fini"]:
                        self.etat = VICTOIRE
                        self.nouveau_record = sauvegarder_record(self.partie["mode"], self.partie["nb_scans"])
                        self.records = charger_records()
                        emettre_particules(self.particules, LARGEUR // 2, HAUTEUR // 2, "confetti", 60)
                        self.jouer_son("victoire")
                else:
                    self.message_flash, self.message_timer = "Or insuffisant (40 requis) !", 1.5
                return
            elif arme == "bombe_ligne_colonne":
                resultat = tirer_bombe_ligne_colonne(self.partie, gx, gy)
                if resultat and "erreur" not in resultat:
                    self.jouer_son("epave")
                    self.flash_ecran = 0.3
                    for imp in resultat.get("impacts", []):
                        if imp.get("resultat") in ("touche", "epave"):
                            cpx = self.grille_x + imp["x"] * self.tc + self.tc // 2
                            cpy = self.grille_y + imp["y"] * self.tc + self.tc // 2
                            emettre_particules(self.particules, cpx, cpy, "etincelles", 14)
                    self.message_flash, self.message_timer = "Frappe Ligne/Col déployée !", 2.5
                    if self.partie["fini"]:
                        self.etat = VICTOIRE
                        self.nouveau_record = sauvegarder_record(self.partie["mode"], self.partie["nb_scans"])
                        self.records = charger_records()
                        emettre_particules(self.particules, LARGEUR // 2, HAUTEUR // 2, "confetti", 60)
                        self.jouer_son("victoire")
                else:
                    self.message_flash, self.message_timer = "Or insuffisant (80 requis) !", 1.5
                return

        if self.mode_radar:
            self.mode_radar = False
            resultat = scan_radar(self.partie, gx, gy)
            if resultat:
                self.radar_info = resultat
                self.jouer_son("radar")
                self.anim_pings.append({"x": px, "y": py, "t": 0, "c": VERT_RADAR, "dur": 0.8})
                txt = f"Radar : {resultat['compteur']} case(s) détectée(s)" if resultat["type"] == "balayage" else "Radar : contact direct !"
                self.message_flash, self.message_timer = txt, 3.0
            return

        res = flasher_case(self.partie, gx, gy)
        type_res = res["resultat"]

        if type_res == "vide":
            self.jouer_son("rate")
            self.anim_pings.append({"x": px, "y": py, "t": 0, "c": GRIS, "dur": 0.4})
            self.message_flash, self.message_timer = "Place vide...", 1.2
        elif type_res == "touche":
            nom_v = res["vehicule"]
            if not self.jouer_son(nom_v):
                self.jouer_son("touche")
            emettre_particules(self.particules, px, py, "etincelles", 12)
            self.anim_pings.append({"x": px, "y": py, "t": 0, "c": ORANGE, "dur": 0.5})
            self.flash_ecran, self.message_flash, self.message_timer = 0.08, f"{nom_v} touché !", 1.8
        elif type_res == "epave":
            nom_v = res["vehicule"]
            self.jouer_son("epave")
            for cx, cy in res["cases"]:
                cpx = self.grille_x + cx * self.tc + self.tc // 2
                cpy = self.grille_y + cy * self.tc + self.tc // 2
                emettre_particules(self.particules, cpx, cpy, "etincelles", 8)
                emettre_particules(self.particules, cpx, cpy, "fumee", 5)
            self.anim_pings.append({"x": px, "y": py, "t": 0, "c": ROUGE, "dur": 0.6})
            self.flash_ecran, self.message_flash, self.message_timer = 0.15, f"{nom_v} — ÉPAVE !", 2.2

            if self.partie["fini"]:
                self.etat = VICTOIRE
                nb, mode = self.partie["nb_scans"], self.partie["mode"]
                self.nouveau_record = sauvegarder_record(mode, nb)
                self.records = charger_records()
                emettre_particules(self.particules, LARGEUR // 2, HAUTEUR // 2, "confetti", 60)
                self.jouer_son("victoire")

    def gerer_evenements(self):
        pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:

        for i in range(8):
            yy = (i * 120 + int(self.menu_timer * 30)) % (HAUTEUR + 100) - 50
            pygame.draw.rect(ecran, (25, 27, 32), (LARGEUR // 2 - 3, yy, 6, 40))

        texte_centre(ecran, self.p_titre, "TRAQUE URBAINE", 100, CYAN)
        texte_centre(ecran, self.p_normale, "Détection Tactique sur Grille de Parking", 160, GRIS)
        pygame.draw.line(ecran, CYAN_SOMBRE, (LARGEUR // 2 - 200, 195), (LARGEUR // 2 + 200, 195), 1)

        pos = pygame.mouse.get_pos()
        r1 = pygame.Rect(LARGEUR // 2 - 200, 240, 400, 60)
        self.boutons["rallye"] = dessiner_bouton(ecran, self.p_grande, "RALLYE URBAIN (5x5)", r1, (20, 50, 30), VERT, r1.collidepoint(pos))

        r2 = pygame.Rect(LARGEUR // 2 - 200, 320, 400, 60)
        self.boutons["grand_prix"] = dessiner_bouton(ecran, self.p_grande, "GRAND PRIX (8x8)", r2, (50, 40, 15), JAUNE, r2.collidepoint(pos), JAUNE)

        r_rec = pygame.Rect(LARGEUR // 2 - 180, 410, 360, 110)
        pygame.draw.rect(ecran, PANNEAU_BG, r_rec, border_radius=10)
        pygame.draw.rect(ecran, PANNEAU_BORD, r_rec, 1, border_radius=10)
        texte_centre(ecran, self.p_normale, "MEILLEURS SCORES", 422, CYAN)
        rec_r = self.records.get("rallye")
        rec_gp = self.records.get("grand_prix")
        texte_centre(ecran, self.p_petite, f"Rallye : {rec_r if rec_r is not None else '---'} scans", 455, BLANC)
        texte_centre(ecran, self.p_petite, f"Grand Prix : {rec_gp if rec_gp is not None else '---'} scans", 480, BLANC)

        r_son = pygame.Rect(LARGEUR // 2 - 180, 550, 170, 38)
        self.boutons["son"] = dessiner_bouton(ecran, self.p_petite, f"Son : {'ON' if self.son_actif else 'OFF'}", r_son, PANNEAU_BG, GRIS_SOMBRE, r_son.collidepoint(pos))

        r_reset = pygame.Rect(LARGEUR // 2 + 10, 550, 170, 38)
        self.boutons["reset"] = dessiner_bouton(ecran, self.p_petite, "Reset Records", r_reset, PANNEAU_BG, GRIS_SOMBRE, r_reset.collidepoint(pos))
        texte_centre(ecran, self.p_petite, "by Erwan — 2026", 740, (45, 48, 55))

    def _dessiner_cellule(self, gx, gy):
        ecran, tc = self.ecran, self.tc
        px = self.grille_x + gx * tc
        py = self.grille_y + gy * tc
        r_int = pygame.Rect(px + 2, py + 2, tc - 4, tc - 4)
        etat_c = self.partie["cases_flashees"].get((gx, gy))

        if etat_c is None:
            pygame.draw.rect(ecran, ASPHALTE, r_int)
            pygame.draw.line(ecran, (50, 52, 60), (px + 4, py + 2), (px + tc - 5, py + 2))
            if self.cellule_survol == (gx, gy):
                c_bord = VERT_RADAR if self.mode_radar else CYAN
                pygame.draw.rect(ecran, c_bord, r_int, 2, border_radius=3)
            return

        if etat_c == "vide":
            pygame.draw.rect(ecran, ASPHALTE_CLAIR, r_int)
            m = tc // 4
            pygame.draw.line(ecran, GRIS_SOMBRE, (px + m, py + m), (px + tc - m, py + tc - m), 2)
            pygame.draw.line(ecran, GRIS_SOMBRE, (px + tc - m, py + m), (px + m, py + tc - m), 2)
            return

        id_v = self.partie["parking"][gy][gx]
        nom_v = self.partie["vehicules"][id_v]["nom"] if id_v in self.partie["vehicules"] else ""
        c_v = COULEURS_V.get(nom_v, ROUGE)

        if etat_c == "touche":
            pygame.draw.rect(ecran, c_v, r_int)
            pygame.draw.rect(ecran, ORANGE, r_int, 2, border_radius=2)
        elif etat_c == "epave":
            c_sombre = tuple(max(0, c // 2) for c in c_v)
            pygame.draw.rect(ecran, c_sombre, r_int)
            pygame.draw.line(ecran, ROUGE, (px + 4, py + 4), (px + tc - 5, py + tc - 5), 2)
            pygame.draw.line(ecran, ROUGE, (px + tc - 5, py + 4), (px + 4, py + tc - 5), 2)
            pygame.draw.rect(ecran, ROUGE, r_int, 2, border_radius=2)

    def dessiner_jeu(self):
        ecran, t, tc = self.ecran, self.partie["taille"], self.tc
        ecran.fill(NOIR)
        pos = pygame.mouse.get_pos()

                      pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.arme_active:
                        self.arme_active = None
                    else:
                        self.etat = MENU
                elif event.key == pygame.K_m:
                    self.son_actif = not self.son_actif
                elif event.key == pygame.K_r and self.etat == JEU and self.partie and self.partie["mode"] == "grand_prix":
                    if not self.partie["radar_utilise"]:
                        self.mode_radar = not self.mode_radar
                elif event.key == pygame.K_1 and self.etat == JEU and self.partie and self.partie["mode"] == "grand_prix":
                    self.arme_active = "scan" if self.arme_active != "scan" else None
                    self.jouer_son("clic")
                elif event.key == pygame.K_2 and self.etat == JEU and self.partie and self.partie["mode"] == "grand_prix":
                    self.arme_active = "bombe_croix" if self.arme_active != "bombe_croix" else None
                    self.jouer_son("clic")
                elif event.key == pygame.K_3 and self.etat == JEU and self.partie and self.partie["mode"] == "grand_prix":
                    self.arme_active = "bombe_ligne_colonne" if self.arme_active != "bombe_ligne_colonne" else None
                    self.jouer_son("clic")

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.etat == MENU:
                    if self.boutons.get("rallye", pygame.Rect(0,0,0,0)).collidepoint(pos):
                        self.demarrer_partie("rallye")
                    elif self.boutons.get("grand_prix", pygame.Rect(0,0,0,0)).collidepoint(pos):
                        self.demarrer_partie("grand_prix")
                    elif self.boutons.get("son", pygame.Rect(0,0,0,0)).collidepoint(pos):
                        self.son_actif = not self.son_actif
                        self.jouer_son("clic")
                    elif self.boutons.get("reset", pygame.Rect(0,0,0,0)).collidepoint(pos):
                        try:
                            os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)), "records.json"))
                        except OSError:
                            pass
                        self.records = {"rallye": None, "grand_prix": None}
                        self.jouer_son("clic")

                elif self.etat == JEU:
                    if self.boutons.get("retour", pygame.Rect(0,0,0,0)).collidepoint(pos):
                        self.etat = MENU
                        self.jouer_son("clic")
                    elif self.boutons.get("shop_scan", pygame.Rect(0,0,0,0)).collidepoint(pos):
                        self.arme_active = "scan" if self.arme_active != "scan" else None
                        self.jouer_son("clic")
                    elif self.boutons.get("shop_croix", pygame.Rect(0,0,0,0)).collidepoint(pos):
                        self.arme_active = "bombe_croix" if self.arme_active != "bombe_croix" else None
                        self.jouer_son("clic")
                    elif self.boutons.get("shop_ligne", pygame.Rect(0,0,0,0)).collidepoint(pos):
                        self.arme_active = "bombe_ligne_colonne" if self.arme_active != "bombe_ligne_colonne" else None
                        self.jouer_son("clic")
                    else:
                        self._clic_grille(pos)

                elif self.etat == VICTOIRE:
                    if self.boutons.get("rejouer", pygame.Rect(0,0,0,0)).collidepoint(pos):
                        self.demarrer_partie(self.partie["mode"])
                    elif self.boutons.get("menu_btn", pygame.Rect(0,0,0,0)).collidepoint(pos):
                        self.etat = MENU
                        self.jouer_son("clic")

        if self.etat == JEU and self.partie:
            t = self.partie["taille"]
            gx = (pos[0] - self.grille_x) // self.tc
            gy = (pos[1] - self.grille_y) // self.tc
            self.cellule_survol = (gx, gy) if 0 <= gx < t and 0 <= gy < t else None

    def maj(self, dt):
        self.particules = [p for p in self.particules if p.maj()]
        self.anim_pings = [p for p in self.anim_pings if p["t"] < p["dur"]]
        for p in self.anim_pings:
            p["t"] += dt

        if self.flash_ecran > 0:
            self.flash_ecran -= dt
        if self.message_timer > 0:
            self.message_timer -= dt
        self.menu_timer += dt

        if self.etat == VICTOIRE:
            self.victoire_timer += dt
            if random.random() < 0.15:
                emettre_particules(self.particules, random.randint(200, LARGEUR - 200), random.randint(50, 150), "confetti", 3)

        if self.etat == MENU:
            for p in self.parts_menu:
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                if p["y"] < -5:
                    p["y"] = HAUTEUR + 5
                    p["x"] = random.randint(0, LARGEUR)

    def dessiner_menu(self):
        ecran = self.ecran
        ecran.fill(NOIR)
        for p in self.parts_menu:
            pygame.draw.circle(ecran, (p["a"], p["a"], p["a"] + 10), (int(p["x"]), int(p["y"])), p["t"])
  zone = pygame.Rect(self.grille_x - 4, self.grille_y - 4, tc * t + 8, tc * t + 8)
        pygame.draw.rect(ecran, (20, 22, 26), zone, border_radius=6)
        pygame.draw.rect(ecran, JAUNE, zone, 2, border_radius=6)

        for gy in range(t):
            for gx in range(t):
                self._dessiner_cellule(gx, gy)

        for i in range(t + 1):
            pygame.draw.line(ecran, (45, 48, 55), (self.grille_x + i * tc, self.grille_y), (self.grille_x + i * tc, self.grille_y + t * tc))
            pygame.draw.line(ecran, (45, 48, 55), (self.grille_x, self.grille_y + i * tc), (self.grille_x + t * tc, self.grille_y + i * tc))

        lettres = "ABCDEFGH"
        for i in range(t):
            txt = self.p_petite.render(lettres[i], True, MARQUAGE)
            ecran.blit(txt, (self.grille_x + i * tc + tc // 2 - txt.get_width() // 2, self.grille_y - 20))
            txt2 = self.p_petite.render(str(i + 1), True, MARQUAGE)
            ecran.blit(txt2, (self.grille_x - 20, self.grille_y + i * tc + tc // 2 - txt2.get_height() // 2))

        if (self.mode_radar or self.arme_active) and self.cellule_survol:
            sx, sy = self.cellule_survol
            surf = pygame.Surface((tc, tc), pygame.SRCALPHA)
            if self.mode_radar or self.arme_active == "scan":
                surf.fill((0, 255, 100, 35))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if 0 <= sx + dx < t and 0 <= sy + dy < t:
                            ecran.blit(surf, (self.grille_x + (sx + dx) * tc, self.grille_y + (sy + dy) * tc))
            elif self.arme_active == "bombe_croix":
                surf.fill((255, 140, 0, 50))
                for dx, dy in ((0, 0), (0, -1), (0, 1), (-1, 0), (1, 0)):
                    if 0 <= sx + dx < t and 0 <= sy + dy < t:
                        ecran.blit(surf, (self.grille_x + (sx + dx) * tc, self.grille_y + (sy + dy) * tc))
            elif self.arme_active == "bombe_ligne_colonne":
                surf.fill((255, 50, 60, 45))
                for i in range(t):
                    ecran.blit(surf, (self.grille_x + i * tc, self.grille_y + sy * tc))
                    ecran.blit(surf, (self.grille_x + sx * tc, self.grille_y + i * tc))

        if self.radar_info:
            ri = self.radar_info
            cx, cy = ri["centre"]
            if ri["type"] == "balayage":
                surf = pygame.Surface((tc, tc), pygame.SRCALPHA)
                surf.fill((0, 255, 100, 20))
                for zx, zy in ri["zone"]:
                    ecran.blit(surf, (self.grille_x + zx * tc, self.grille_y + zy * tc))
                txt_c = self.p_grande.render(str(ri["compteur"]), True, VERT_RADAR)
                ecran.blit(txt_c, (self.grille_x + cx * tc + tc // 2 - txt_c.get_width() // 2,
                                   self.grille_y + cy * tc + tc // 2 - txt_c.get_height() // 2))
            else:
                for (ax, ay), occ in ri["adjacents"].items():
                    c_pt = VERT_RADAR if occ else (120, 40, 40)
                    pygame.draw.circle(ecran, c_pt, (self.grille_x + ax * tc + tc // 2, self.grille_y + ay * tc + tc // 2), 5 if occ else 3)
                pygame.draw.rect(ecran, JAUNE, (self.grille_x + cx * tc + 1, self.grille_y + cy * tc + 1, tc - 2, tc - 2), 2)

        for ping in self.anim_pings:
            ratio = ping["t"] / ping["dur"]
            c_p = tuple(int(v * max(0, 1 - ratio)) for v in ping["c"])
            pygame.draw.circle(ecran, c_p, (ping["x"], ping["y"]), int(35 * ratio), 2)

        for p in self.particules:
            p.dessiner(ecran)

        px = self.grille_x + t * tc + 40
        pw, ph = LARGEUR - px - 25, t * tc + 8
        pygame.draw.rect(ecran, PANNEAU_BG, (px, self.grille_y, pw, ph), border_radius=10)
        pygame.draw.rect(ecran, PANNEAU_BORD, (px, self.grille_y, pw, ph), 1, border_radius=10)

        txt_scans = self.p_grande.render(f"SCANS: {self.partie['nb_scans']}", True, CYAN)
        ecran.blit(txt_scans, (px + 15, self.grille_y + 12))
        mode_nom = "RALLYE URBAIN" if self.partie["mode"] == "rallye" else "GRAND PRIX"
        ecran.blit(self.p_petite.render(mode_nom, True, JAUNE), (px + 15, self.grille_y + 46))

        if self.partie["mode"] == "grand_prix":
            txt_gold = self.p_petite.render(f"TOUR {self.partie.get('tour', 1)} | OR: {self.partie.get('or', 0)}G (+10/tour)", True, JAUNE)
            ecran.blit(txt_gold, (px + 15, self.grille_y + 68))
            pygame.draw.line(ecran, PANNEAU_BORD, (px + 15, self.grille_y + 90), (px + pw - 15, self.grille_y + 90))
            y_v = self.grille_y + 100
        else:
            pygame.draw.line(ecran, PANNEAU_BORD, (px + 15, self.grille_y + 68), (px + pw - 15, self.grille_y + 68))
            y_v = self.grille_y + 80

        for _, info in sorted(self.partie["vehicules"].items()):
            nom = info["nom"]
            ep = est_epave(info)
            c_past = COULEURS_V.get(nom, BLANC)
            pygame.draw.circle(ecran, c_past, (px + 22, y_v + 8), 5)
            ecran.blit(self.p_petite.render(nom, True, GRIS if ep else BLANC), (px + 34, y_v))
            stat = "ÉPAVE" if ep else (f"{len(info['touches'])}/{info['taille']}" if info['touches'] else "En fuite")
            c_st = ROUGE if ep else (ORANGE if info['touches'] else GRIS_SOMBRE)
            st_s = self.p_petite.render(stat, True, c_st)
            ecran.blit(st_s, (px + pw - st_s.get_width() - 15, y_v))
            y_v += 24

        if self.partie["mode"] == "grand_prix":
            cur_or = self.partie.get("or", 0)

            # Bouton 1 : Scan 20G
            r_b1 = pygame.Rect(px + 15, y_v + 10, pw - 30, 32)
            c1 = (20, 50, 35) if cur_or >= 20 else (25, 25, 25)
            if self.arme_active == "scan": c1 = (30, 80, 50)
            self.boutons["shop_scan"] = dessiner_bouton(
                ecran, self.p_petite, "[1] SCAN RADAR (20G)", r_b1,
                c1, VERT_RADAR if self.arme_active == "scan" else (GRIS_SOMBRE if cur_or < 20 else VERT),
                r_b1.collidepoint(pos), BLANC if cur_or >= 20 else GRIS_SOMBRE
            )

            # Bouton 2 : Bombe Croix 40G
            r_b2 = pygame.Rect(px + 15, y_v + 48, pw - 30, 32)
            c2 = (60, 40, 15) if cur_or >= 40 else (25, 25, 25)
            if self.arme_active == "bombe_croix": c2 = (90, 55, 20)
            self.boutons["shop_croix"] = dessiner_bouton(
                ecran, self.p_petite, "[2] BOMBE CROIX (40G)", r_b2,
                c2, ORANGE if self.arme_active == "bombe_croix" else (GRIS_SOMBRE if cur_or < 40 else ORANGE),
                r_b2.collidepoint(pos), BLANC if cur_or >= 40 else GRIS_SOMBRE
            )

            # Bouton 3 : Bombe Ligne/Col 80G
            r_b3 = pygame.Rect(px + 15, y_v + 86, pw - 30, 32)
            c3 = (60, 20, 25) if cur_or >= 80 else (25, 25, 25)
            if self.arme_active == "bombe_ligne_colonne": c3 = (100, 30, 35)
            self.boutons["shop_ligne"] = dessiner_bouton(
                ecran, self.p_petite, "[3] MÉGA BOMBE (80G)", r_b3,
                c3, ROUGE if self.arme_active == "bombe_ligne_colonne" else (GRIS_SOMBRE if cur_or < 80 else ROUGE),
                r_b3.collidepoint(pos), BLANC if cur_or >= 80 else GRIS_SOMBRE
            )

        r_ret = pygame.Rect(px + 15, self.grille_y + ph - 45, pw - 30, 34)
        self.boutons["retour"] = dessiner_bouton(ecran, self.p_petite, "RETOUR AU MENU", r_ret, PANNEAU_BG, GRIS_SOMBRE, r_ret.collidepoint(pos), GRIS)

        if self.message_timer > 0 and self.message_flash:
            alpha = min(1, self.message_timer / 0.5)
            c_msg = tuple(int(v * alpha) for v in BLANC)
            texte_centre(ecran, self.p_normale, self.message_flash, HAUTEUR - 40, c_msg)

        if self.flash_ecran > 0:
            surf_f = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
            surf_f.fill((255, 255, 255, int(min(255, 120 * (self.flash_ecran / 0.15)))))
            ecran.blit(surf_f, (0, 0))

    def dessiner_victoire(self):
        ecran = self.ecran
        self.dessiner_jeu()
        overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, min(180, int(self.victoire_timer * 400))))
        ecran.blit(overlay, (0, 0))

        if self.victoire_timer < 0.2:
            flash = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
            flash.fill((255, 255, 255, int(255 * (1 - self.victoire_timer / 0.2))))
            ecran.blit(flash, (0, 0))
            return

        pos = pygame.mouse.get_pos()
        texte_centre(ecran, self.p_titre, "VÉHICULES IMMOBILISÉS !", 180, CYAN)
        texte_centre(ecran, self.p_grande, f"Total de scans : {self.partie['nb_scans']}", 260, BLANC)

        if self.nouveau_record:
            texte_centre(ecran, self.p_normale, "★ NOUVEAU RECORD ! ★", 310, JAUNE)

        r_rej = pygame.Rect(LARGEUR // 2 - 210, 390, 190, 50)
        self.boutons["rejouer"] = dessiner_bouton(ecran, self.p_normale, "REJOUER", r_rej, (15, 50, 25), VERT, r_rej.collidepoint(pos))

        r_m = pygame.Rect(LARGEUR // 2 + 20, 390, 190, 50)
        self.boutons["menu_btn"] = dessiner_bouton(ecran, self.p_normale, "MENU", r_m, (50, 30, 15), JAUNE, r_m.collidepoint(pos), JAUNE)

        for p in self.particules:
            p.dessiner(ecran)

    def lancer(self):
        while True:
            dt = self.horloge.tick(FPS) / 1000.0
            self.gerer_evenements()
            self.maj(dt)
            if self.etat == MENU:
                self.dessiner_menu()
            elif self.etat == JEU:
                self.dessiner_jeu()
            elif self.etat == VICTOIRE:
                self.dessiner_victoire()
            pygame.display.flip()


if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            import ctypes
            u32 = ctypes.windll.user32
            hdesk = u32.OpenDesktopW("Default", 0, False, 0x01FF)
            if hdesk:
                u32.SetThreadDesktop(hdesk)
        except Exception:
            pass

    app = TraqueUrbaine()
    app.lancer()
