"""Abords rectangulaires autorisés par l'auteur, complétés une fois par le MJ.

Le MJ choisit le terrain ; le moteur calcule les coordonnées, les dénivelés,
les identifiants et les appuis. Aucun texte libre ne crée de fait physique.
"""
import copy
import math

from .monde import ErreurMonde, objet
from .geometrie import cases
from .perception import eclairage
from .refus import cibles, liste


TERRAINS = ("terre", "pierre", "herbe")
SCHEMA = {"type": "object", "additionalProperties": False,
          "properties": {"abords": {"type": "array", "minItems": 1, "maxItems": 4,
              "items": {"type": "object", "additionalProperties": False,
                        "properties": {"cadre": {"type": "string"},
                                       "terrain": {"type": "string", "enum": list(TERRAINS)}},
                        "required": ["cadre", "terrain"]}}}, "required": ["abords"]}

REGLES = """
Le dossier espace décrit les bords et les sols voisins : absence de sortie à pied ne signifie
pas absence de lieu de l'autre côté. Réponds aux questions d'issues à partir de ces bords,
sans demander une observation supplémentaire lorsque ces faits sont déjà visibles.
observations_visibles est une synthèse calculée depuis la position réelle du personnage.
Elle décrit déjà ce qui est en contrebas : un lieu nommé bas est le sol au-dessous du bord,
pas une destination abstraite dont il faudrait encore inventer le dessous. hauteur_cm mesure
le dénivelé entre ce sol et le palier. Ne déclare pas ces informations absentes.
Pour remonter une échelle depuis son sommet puis descendre ailleurs, composer peut enchaîner :
soulever (cible échelle, destination salle actuelle), appuyer (cible échelle, outil appui du bord
choisi), franchir (cible échelle). Cela retire l'ancien appui, dépose l'objet ici, le déplace et
l'appuie au nouveau bord, puis permet la descente. N'exige pas de revenir au pied.
Ces étapes ont methode simple, difficulte 0, champs inutilisés vides. Elles restent soumises
au poids, à la longueur, aux prises et à la stabilité. Une installation ne fixe pas l'objet.
Pour sauter en contrebas : composer, opération sauter, cible identifiant de l'appui du bord,
destination son bas, outil vide, methode simple, difficulte 0. Le moteur calcule jet et blessures.
Un saut échoué atteint aussi le sol, avec davantage de blessures. Ne le remplace pas par une
descente à l'échelle si le joueur veut sauter. Les conventions de chute sont des règles de JDR.
Le bord opposé à une échelle installée est indiqué dans espace ; il ne dépend pas de son nom.
"""

CONSIGNES_QUESTION = """Tu es le maître du jeu d'une aventure en français. Tutoie le joueur.
Le joueur pose une question, pas une demande d'action : réponds en dialogue, proposition null.
Décris directement ce qu'il peut percevoir à partir de espace.observations_visibles et des
autres faits fournis. Ne récite pas les dossiers : n'écris pas « les faits indiquent »,
« les données ne précisent pas », « le moteur » ou « non défini » dans la réponse.
Un sol et un lieu décrits en contrebas sont ce qu'il y a sous le bord, même sans sortie à pied.
À « sous la terrasse », explique ce qui est en contrebas ; n'invente pas une cave, des piliers
ou un vide sous la dalle. N'étends pas une inconnue à des abords déjà décrits.
Si une ambiguïté change réellement la réponse, distingue brièvement les sens de la question.
Une question de faisabilité d'un geste se propose comme ce geste : le moteur le prépare sans
l'exécuter.
Les indications actuelles priment sur d'anciennes réponses contradictoires de la conversation.
Deux ou trois phrases naturelles suffisent. N'invente ni objets, ni perception supplémentaire.
faits référence les clés publiques utilisées. Appelle repondre_au_joueur exactement une fois.
"""


def installer(m):
    """Migration additive du cadre d'auteur, sans réinitialiser les objets ni la partie."""
    if m.data.get("espace_version") or "mur_atelier" not in m.objets:
        return
    a = m.objets["mur_atelier"].get("appui_vertical", {})
    if a.get("bas") != "cour" or a.get("haut") != "terrasse":
        return
    m.data["salles"]["cour"].setdefault("altitude_cm", 0)
    m.data["salles"]["terrasse"].setdefault("altitude_cm", a["hauteur_cm"])
    a.setdefault("direction", "sud")
    a.setdefault("prise_sommet", True)
    m.data.setdefault("cadres_spatiaux", {})["terrasse_nord"] = {
        "haut": "terrasse", "direction": "nord", "profondeur_m": 3,
        "altitude_cm": 0, "sol_stable": True, "sommet_stable": True,
        "prise_sommet": True, "recul_cm": 90}
    # Les côtés latéraux sont des limites d'auteur explicites, pas des sorties oubliées.
    m.data["salles"]["terrasse"].setdefault("bords_fermes", ["est", "ouest"])
    for direction in m.data["salles"]["terrasse"]["bords_fermes"]:
        id = "terrasse_mur_" + direction
        if id not in m.objets:
            m.objets[id] = objet(id, "mur " + direction, "surface", "terrasse",
                                 aliases=["mur " + direction], materiau="pierre")
    m.data["espace_version"] = 1


def a_completer(m):
    if eclairage(m)["niveau"] < 2:
        return {}
    return {k: copy.deepcopy(c) for k, c in m.data.get("cadres_spatiaux", {}).items()
            if c["haut"] == m.joueur["salle"] and not c.get("complete")}


def preparer(m, proposition, revision=None):
    if revision is not None and revision != m.data["revision"]:
        raise ErreurMonde("Le monde a changé avant la description des abords.", "re-propose à partir des faits actuels.")
    if not isinstance(proposition, dict) or set(proposition) != {"abords"}:
        recus = sorted(proposition) if isinstance(proposition, dict) else type(proposition).__name__
        raise ErreurMonde("Complément spatial mal formé.", f"espace a exactement le champ abords ; reçu : {recus}.")
    ajouts, autorises = proposition["abords"], a_completer(m)
    if not isinstance(ajouts, list) or not 1 <= len(ajouts) <= 4:
        raise ErreurMonde("Nombre d'abords invalide.", "abords : une liste de 1 à 4 éléments {cadre, terrain}.")
    travail, vus = m.copier(), set()
    for ajout in ajouts:
        if (not isinstance(ajout, dict) or set(ajout) != {"cadre", "terrain"}
                or any(not isinstance(v, str) for v in ajout.values())):
            raise ErreurMonde("Complément spatial mal formé.", "chaque abord a exactement les champs cadre et terrain (textes).")
        if ajout["cadre"] not in autorises or ajout["cadre"] in vus:
            raise ErreurMonde("Cet abord est déjà établi ou n'est pas autorisé.",
                              f"cadre « {ajout['cadre']} » : un cadre à compléter, une seule fois, parmi "
                              f"{liste(sorted(set(autorises) - vus))}.")
        if ajout["terrain"] not in TERRAINS:
            raise ErreurMonde("Ce terrain n'est pas connu.",
                              f"terrain parmi {', '.join(TERRAINS)} (reçu « {ajout['terrain']} »).")
        id, terrain = ajout["cadre"], ajout["terrain"]
        vus.add(id)
        c = travail.data["cadres_spatiaux"][id]
        haut = travail.data["salles"][c["haut"]]
        plan = haut["plan"]
        w, h = len(plan["sol"][0]), len(plan["sol"])
        if any(l != "." * w for l in plan["sol"]):
            raise ErreurMonde("Ce cadre demande une plateforme rectangulaire.", f"cadre {id} non complétable : retire-le des abords.")
        profondeur, direction = c["profondeur_m"], c["direction"]
        if type(profondeur) is not int or not 2 <= profondeur <= 8 or direction not in ("nord", "sud", "est", "ouest"):
            raise ErreurMonde("Cadre spatial invalide.", f"cadre {id} non complétable : retire-le des abords.")
        x, y = plan["origine"]
        nx, ny, nw, nh = {"nord": (x, y-profondeur-1, w, profondeur),
                          "sud": (x, y+h+1, w, profondeur),
                          "est": (x+w+1, y, profondeur, h),
                          "ouest": (x-profondeur-1, y, profondeur, h)}[direction]
        altitude = c["altitude_cm"]
        hauteur = haut["altitude_cm"] - altitude
        if type(hauteur) is not int or not 1 <= hauteur <= 1000:
            raise ErreurMonde("Dénivelé absent ou incohérent.", f"cadre {id} non complétable : retire-le des abords.")
        nouveaux = {(nx+i, ny+j) for i in range(nw) for j in range(nh)}
        for salle in travail.data["salles"].values():
            if salle.get("altitude_cm", 0) != altitude:
                continue
            ox, oy = salle["plan"]["origine"]
            if nouveaux & {(ox+i, oy+j) for i, j in cases(salle)}:
                raise ErreurMonde("L'extension chevaucherait un lieu existant.", f"cadre {id} non complétable : retire-le des abords.")
        bas, support = "abord_" + id, "appui_" + id
        if bas in travail.data["salles"] or support in travail.objets or bas + "_sol" in travail.objets:
            raise ErreurMonde("Un identifiant spatial est déjà utilisé.", f"cadre {id} déjà complété : retire-le des abords.")
        travail.data["salles"][bas] = {"nom": "Passage extérieur au " + direction,
            "sorties": {}, "fenetres": 0, "exterieur": True, "lumiere_naturelle": 2,
            "altitude_cm": altitude, "niveau": altitude / 240,
            "plan": {"origine": [nx, ny], "sol": ["."*nw]*nh, "repere": "P"}}
        travail.objets[bas + "_sol"] = objet(bas + "_sol", "sol", "surface", bas,
                                            aliases=["sol"], materiau=terrain)
        travail.objets[support] = objet(support, "bord " + direction, "surface", c["haut"],
            aliases=["bord " + direction, "mur " + direction], materiau="pierre",
            appui_vertical={"bas": bas, "haut": c["haut"], "direction": direction,
                "hauteur_cm": hauteur, **{k: c[k] for k in ("recul_cm", "sol_stable", "sommet_stable", "prise_sommet")}})
        c.update(complete=True, bas=bas, support=support, terrain=terrain)
    travail.data["revision"] += 1
    travail.data.setdefault("enrichissements", []).append({"revision": travail.data["revision"],
        "origine": "MJ spatial", "ajouts": copy.deepcopy(ajouts)})
    if travail.data.get("mode_cases"):
        from .spatial import installer
        installer(travail)
    travail.verifier()
    return travail


def dossier(m):
    if eclairage(m)["niveau"] < 2:
        return None
    salle, bords = m.joueur["salle"], []
    for id, o in m.objets.items():
        a = o.get("appui_vertical")
        if not a or salle not in (a["bas"], a["haut"]) or not a.get("direction"):
            continue
        if m.data.get("mode_cases"):
            from .spatial import proche
            if not m.visible(id) or not proche(m, id):
                continue
        autre = a["bas"] if salle == a["haut"] else a["haut"]
        bords.append({"appui": id, **a, "lieu_voisin": m.data["salles"][autre]["nom"],
                      "position_relative": "en contrebas" if salle == a["haut"] else "en hauteur",
                      "terrain": next((s["materiau"] for s in m.objets.values() if s["lieu"] == a["bas"] and s["nom"] == "sol"), None)})
    if not bords:
        return None
    oppose = {"nord": "sud", "sud": "nord", "est": "ouest", "ouest": "est"}
    echelles = []
    for id, o in m.objets.items():
        if o.get("installation") and m.accessible(id):
            a = m.objets[o["installation"]["support"]]["appui_vertical"]
            echelles.append({"objet": id, "support": o["installation"]["support"],
                            "bord_oppose": oppose.get(a.get("direction"))})
    observations = []
    for b in bords:
        hauteur = f"{b['hauteur_cm']/100:g}".replace(".", ",")
        if b["position_relative"] == "en contrebas":
            observations.append(f"Au {b['direction']} : {b['lieu_voisin']}, à {hauteur} m en contrebas."
                                + (f" Le sol visible en dessous de ce bord est en {b['terrain']}." if b["terrain"] else ""))
        else:
            observations.append(f"{b['lieu_voisin']} se trouve à {hauteur} m au-dessus du sol où tu te tiens.")
    return {"bords": bords, "observations_visibles": observations,
            "bords_fermes": m.data["salles"][salle].get("bords_fermes", []),
            "installations": echelles}


def description(m):
    d = dossier(m)
    if not d:
        return []
    lignes = []
    for b in d["bords"]:
        if m.joueur["salle"] == b["haut"]:
            lignes.append(f"Au {b['direction']}, le bord surplombe {b['lieu_voisin'].lower()} de {b['hauteur_cm']/100:g} m"
                          + (f" ; le sol en contrebas est en {b['terrain']}." if b["terrain"] else "."))
    return lignes


def compiler_saut(m, e, justification, origine):
    from .moteur import Plan
    from .artisanat import appui
    if e["outil"] or e["methode"] != "simple" or e["difficulte"]:
        raise ErreurMonde("Un saut se fait sans outil ni jet annoncé.", "sauter : outil vide, methode simple, difficulte 0.")
    if not m.accessible(e["cible"]):
        bords = sorted(i for i, x in m.objets.items() if x.get("appui_vertical") and m.accessible(i))
        raise ErreurMonde("Il faut un bord visible et identifié pour ce saut.",
                          f"cible : un bord établi, parmi {cibles(m, bords)} (reçu « {e['cible']} »).")
    a = appui(m, e["cible"])
    from .proximite import exiger
    exiger(m, e["cible"])
    if m.joueur["pv"] <= 0:
        raise ErreurMonde("Tu n'es plus en état de sauter.", "le joueur est hors de combat : aucun saut.")
    if m.joueur["salle"] != a["haut"] or e["destination"] != a["bas"]:
        raise ErreurMonde("Ce saut doit partir du bord et rejoindre son sol en contrebas.",
                          f"depuis {a['haut']} (le joueur est en {m.joueur['salle']}), destination = {a['bas']} "
                          f"(reçu « {e['destination']} »).")
    if eclairage(m)["niveau"] < 2:
        raise ErreurMonde("Tu ne distingues pas suffisamment la zone de réception.",
                          "sauter exige une lumière franche : allume d'abord une source.")
    hauteur = a["hauteur_cm"]
    p = Plan({"action": "composer", "justification": justification}, m.data["revision"],
             f"Sauter {hauteur/100:g} m en contrebas vers {m.data['salles'][a['bas']]['nom'].lower()}.", origine=origine)
    p.stat, p.dd, p.bruit = "DEX", min(25, 8 + math.ceil(hauteur/50)), 3
    amorti, manque = max(0, math.ceil((hauteur-100)/100)), math.ceil(hauteur/50)
    arrivee = None
    if m.data.get("mode_cases"):
        from .spatial import destination_appui
        arrivee = destination_appui(m, e["cible"], a["bas"])
    trajet = ("voyager", a["bas"], arrivee)
    p.effets = [trajet, ("blessure_chute", "", amorti)]
    p.echec = [trajet, ("blessure_chute", "", manque)]
    p.risque = f"Tu atteins le sol dans les deux cas : {amorti} PV perdus si tu amortis la chute, {manque} PV en cas d'échec."
    return p


def verifier(m):
    for c in m.data.get("cadres_spatiaux", {}).values():
        assert c["haut"] in m.data["salles"], "Cadre sans plateforme"
        if c.get("complete"):
            a = m.objets[c["support"]]["appui_vertical"]
            assert a["bas"] == c["bas"] and a["haut"] == c["haut"], "Abord incohérent"
            assert a["hauteur_cm"] == m.data["salles"][a["haut"]]["altitude_cm"] - m.data["salles"][a["bas"]]["altitude_cm"], "Altitudes contradictoires"
