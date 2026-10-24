"""Résolution sommaire des initiatives, sans autoriser des écritures arbitraires.

La prose raconte ; seuls les effets typés changent les propriétés du monde.
Une marque est une inscription sur un support réel, pas un fait géographique.
"""
import copy
import hashlib
import json

from .monde import ErreurMonde, objet, normaliser
from .francais import designer
from .perception import eclairage
from .vol import proprietaire
from .refus import cibles, RefusDeForme, inaccessible


def effet(operation, cible="", destination="", texte="", valeur=0):
    return dict(operation=operation, cible=cible, destination=destination, texte=texte, valeur=valeur)


def issue(recit, effets=None):
    return {"recit": recit, "effets": effets or []}


def proposition(intention, reussite, echec=None, cibles=None, outil="", approche="expression",
                stat="", difficulte=0, minutes=1, bruit=0):
    return dict(action="improviser", intention=intention, cibles=cibles or [], outil=outil,
                approche=approche, stat=stat, difficulte=difficulte, minutes=minutes, bruit=bruit,
                reussite=reussite, echec=echec or issue(""))


APPROCHES = ("expression", "manipulation", "effort", "adresse", "observation")
STAT = ("", "FOR", "DEX", "INT", "PER", "CHA")
FORMES_SONORES = {
    "indetermine": "Tu produis un son.",
    "voix_melodique": "Tu fais entendre des notes de ta voix.",
    "voix_breve": "Tu fais entendre un son de voix bref.",
    "souffle": "Tu produis un son de souffle.",
    "corps_rythmique": "Tu frappes un rythme avec ton corps.",
    "corps_bref": "Tu produis un bruit bref avec ton corps.",
}
SCHEMA_EFFET = {"type": "object", "additionalProperties": False, "properties": {
    "operation": {"type": "string", "enum": ["marquer", "deplacer", "user", "blesser", "son"]},
    "cible": {"type": "string"}, "destination": {"type": "string"},
    "texte": {"type": "string"}, "valeur": {"type": "integer"}}, "required": list(effet(""))}
SCHEMA_ISSUE = {"type": "object", "additionalProperties": False, "properties": {
    "recit": {"type": "string"}, "effets": {"type": "array", "maxItems": 4, "items": SCHEMA_EFFET}},
    "required": ["recit", "effets"]}
SCHEMA = {"type": "object", "additionalProperties": False, "properties": {
    "action": {"type": "string", "enum": ["improviser"]}, "intention": {"type": "string"},
    "cibles": {"type": "array", "maxItems": 6, "items": {"type": "string"}},
    "outil": {"type": "string"}, "approche": {"type": "string", "enum": list(APPROCHES)},
    "stat": {"type": "string", "enum": list(STAT)}, "difficulte": {"type": "integer", "minimum": 0, "maximum": 18},
    "minutes": {"type": "integer", "minimum": 0, "maximum": 15},
    "bruit": {"type": "integer", "minimum": 0, "maximum": 3},
    "reussite": SCHEMA_ISSUE, "echec": SCHEMA_ISSUE},
    "required": list(proposition("", issue("")))}



def texte_valide(s, maxi, vide=False):
    return isinstance(s, str) and (vide or bool(s.strip())) and len(s) <= maxi and all(ord(c) >= 32 for c in s)


def libelle_geste(m, p):
    """Décrit une tentative depuis ses seuls champs structurés et validés."""
    objets = [m.objets[id] for id in p["cibles"]]
    cibles = ", ".join(designer(o) for o in objets)
    outil = m.objets.get(p["outil"])
    complements = (" concernant " + cibles if cibles else "")
    if outil and p["outil"] not in p["cibles"]:
        complements += " avec " + designer(outil)
    return "Geste" + complements


def action_persistante(m, p):
    """Conserve une proposition rejouable sans les brouillons libres du MJ."""
    action = copy.deepcopy(p)
    action["intention"] = libelle_geste(m, p)
    action["reussite"]["recit"] = "Tu réalises ce geste."
    action["echec"]["recit"] = "Tu tentes ce geste sans aboutir." if p["stat"] else ""
    return action


def compiler_effets(m, p, branche):
    simulation, resultat = m.copier(), []
    for numero, e in enumerate(branche["effets"]):
        try:
            resultat.extend(compiler_effet(simulation, p, e))
        except ErreurMonde as exc:
            nom = e.get("operation", "?") if isinstance(e, dict) else "?"
            exc.attendu = f"effet {numero + 1} ({nom}) : " + (exc.attendu or str(exc))
            raise
    return resultat


def compiler_effet(simulation, p, e):
    from .operations import compiler, etape
    from .moteur import Moteur
    if (not isinstance(e, dict) or set(e) != set(effet(""))
            or any(not texte_valide(e[k], 160, vide=True) for k in ("operation", "cible", "destination", "texte"))
            or type(e["valeur"]) is not int):
        recus = sorted(e) if isinstance(e, dict) else type(e).__name__
        raise RefusDeForme("Conséquence d'improvisation mal formée.",
                          "un effet a exactement operation, cible, destination, texte (≤ 160 caractères, sans saut "
                          f"de ligne), valeur (entier) ; reçu : {recus}.")
    op, cible, destination, texte, valeur = (e[k] for k in effet(""))
    if cible != "joueur" and cible not in [*p["cibles"], p["outil"]]:
        annonces = [c for c in ["joueur", *p["cibles"], p["outil"]] if c]
        raise RefusDeForme("La conséquence doit viser une cible annoncée.",
                          f"cible « {cible} » : parmi joueur, {cibles(simulation, annonces)} ; si elle est impliquée, ajoute-la à cibles.")
    if op not in ("marquer", "son") and texte:
        raise RefusDeForme("Un texte libre ne peut pas définir un effet physique.",
                          f"{op} : texte vide ; seuls marquer et son portent un texte.")
    if op != "deplacer" and destination:
        raise RefusDeForme("Cette conséquence n'a pas de destination.", f"{op} : destination vide.")
    effets = []
    if op == "deplacer":
        if valeur:
            raise RefusDeForme("Un déplacement ne modifie aucune quantité.", "deplacer : valeur 0.")
        plan = compiler(simulation, etape("deplacer", cible, destination))
        effets = plan.effets
    elif op == "marquer":
        from .proximite import exiger
        exiger(simulation, cible)
        o, t = simulation.objets.get(cible, {}), simulation.objets.get(p["outil"], {})
        supports = ("surface", "porte", "contenant", "materiau", "assemblage")
        fautes = [f for f, mal in (
            ("valeur 0", valeur),
            ("texte = le contenu de la marque, non vide", not texte.strip()),
            (f"{cible} doit être accessible", not simulation.accessible(cible)),
            (f"le support est une surface, porte, contenant, matériau ou assemblage ({cible} : {o.get('type')})",
             o.get("type") not in supports),
            (f"{cible} est brisé", not o.get("integrite")),
            (f"{cible} appartient à autrui", proprietaire(simulation, o) not in (None, "joueur"))) if mal]
        if fautes:
            murs = sorted(i for i, x in simulation.objets.items()
                          if x["type"] == "surface" and simulation.accessible(i))
            raise ErreurMonde("Il faut un support intact et disponible pour y laisser cette marque.",
                              "marquer : " + " ; ".join(fautes) + f" ; supports libres ici : {cibles(simulation, murs)}.")
        usages_marque = {"couper", "couper_bois", "marquer", "graver"}
        if (not t or not simulation.est_porte(p["outil"]) or not t.get("integrite")
                or not set(t.get("usages", [])) & usages_marque):
            outils = sorted(i for i, x in simulation.objets.items() if simulation.est_porte(i)
                            and x.get("integrite") and set(x.get("usages", [])) & usages_marque)
            raise ErreurMonde("Il faut un outil disponible pour tracer ou graver cette marque.",
                              f"outil de l'improvisation : un objet porté qui coupe ou grave, parmi {cibles(simulation, outils)}.")
        if eclairage(simulation)["niveau"] < 2:
            raise ErreurMonde("Tu ne distingues pas assez bien le support pour y tracer une marque.",
                              "marquer exige une lumière franche : allume d'abord une source.")
        effets = [("marque_improvisee", cible, {"texte": texte, "outil": p["outil"]})]
    elif op == "user":
        o = simulation.objets.get(cible, {})
        if (cible != p["outil"] or valeur != 1 or not simulation.est_porte(cible)
                or not o.get("usages") or o.get("integrite", 0) <= 1):
            raise ErreurMonde("Cette usure doit rester limitée à un outil annoncé, porté et en état.",
                              f"user : cible = l'outil annoncé ({p['outil'] or 'aucun'}), porté, intégrité > 1, valeur 1.")
        effets = [("endommager", cible, 1)]
    elif op == "blesser":
        if cible != "joueur" or not 1 <= valeur <= 3 or simulation.joueur["pv"] <= valeur or p["approche"] not in ("effort", "adresse", "manipulation"):
            raise RefusDeForme("Cette blessure dépasse les conséquences mineures de cet arbitrage.",
                              f"blesser : cible joueur, valeur 1 à 3 et inférieure aux PV ({simulation.joueur['pv']}), "
                              "approche effort, adresse ou manipulation.")
        effets = [("blessure_improvisee", "joueur", valeur)]
    elif op == "son":
        if cible != "joueur" or not 1 <= valeur <= 3:
            raise RefusDeForme("Un son improvisé vient du joueur, avec une intensité de 1 à 3.",
                              f"son : cible joueur, valeur 1 à 3 (reçu cible « {cible} », valeur {valeur}).")
        if texte not in FORMES_SONORES:
            raise RefusDeForme("La forme sonore doit être une catégorie acoustique connue.",
                              f"son : texte parmi {', '.join(FORMES_SONORES)} (reçu « {texte} »).")
        forme = texte
        if forme.startswith("voix_") and simulation.joueur.get("peut_parler") is False:
            raise ErreurMonde("Ta voix ne peut actuellement pas produire ce son.",
                              "le joueur ne peut pas parler : une forme sans voix (souffle, corps_rythmique, corps_bref).")
        effets = [("son_improvise", "joueur", {"intensite": valeur, "forme": forme})]
    else:
        raise RefusDeForme("Conséquence non autorisée dans cet arbitrage.",
                          f"operation « {op} » : parmi marquer, deplacer, user, blesser, son.")
    for e_interne in effets:
        Moteur._appliquer(simulation, e_interne, [])
    simulation.verifier()
    return effets


def compiler_branche(m, p, nom):
    try:
        return compiler_effets(m, p, p[nom])
    except ErreurMonde as exc:
        exc.attendu = f"branche {nom}, " + (exc.attendu or str(exc))
        raise


def preparer(m, p, origine):
    from .moteur import Plan
    if not isinstance(p, dict) or set(p) != set(proposition("", issue(""))) or p["action"] != "improviser":
        recus = sorted(p) if isinstance(p, dict) else type(p).__name__
        raise RefusDeForme("Arbitrage sommaire mal formé.",
                          f"improviser a exactement les champs {', '.join(proposition('', issue('')))} ; reçu : {recus}.")
    fautes = [f for f, mal in (
        ("intention : texte non vide de 240 caractères au plus, sans saut de ligne", not texte_valide(p["intention"], 240)),
        ("outil : un identifiant ou vide", not isinstance(p["outil"], str)),
        (f"approche parmi {', '.join(APPROCHES)}", p["approche"] not in APPROCHES),
        (f"stat parmi {', '.join(s or 'vide' for s in STAT)}", p["stat"] not in STAT),
        ("cibles : liste de 0 à 6 identifiants distincts", not isinstance(p["cibles"], list) or len(p["cibles"]) > 6
         or any(not isinstance(id, str) for id in p["cibles"]) or len(set(p["cibles"])) != len(p["cibles"]))) if mal]
    if fautes:
        raise RefusDeForme("Précise l'intention et ses cibles existantes.", " ; ".join(fautes) + ".")
    for champ, mini, maxi in (("minutes", 0, 15), ("bruit", 0, 3), ("difficulte", 10 if p["stat"] else 0, 18 if p["stat"] else 0)):
        if type(p[champ]) is not int or not mini <= p[champ] <= maxi:
            # Une cause par refus : le champ fautif, nommé.
            raise RefusDeForme({"minutes": "La durée", "bruit": "Le bruit", "difficulte": "La difficulté"}[champ]
                              + " de ce geste sort des limites d'un arbitrage sommaire.",
                              f"{champ} : entier de {mini} à {maxi} (reçu {p[champ]!r})"
                              + (" ; avec stat vide, difficulte 0" if champ == "difficulte" and not p["stat"] else
                                 " ; avec une stat, difficulte 10 à 18" if champ == "difficulte" else "") + ".")
    if m.joueur["pv"] <= 0:
        raise ErreurMonde("Tu n'es plus en état d'entreprendre ce geste.", "le joueur est hors de combat : aucun geste.")
    for id in p["cibles"]:
        if not m.accessible(id):
            raise inaccessible(m, id, champ="cibles")
    # Les cibles sont les objets impliqués dans le geste, pas son public. L'approche
    # décrit sa manière ; elle ne donne aucune capacité physique d'agir à distance.
    from .proximite import exiger
    for id in p["cibles"]:
        exiger(m, id)
    if p["outil"] and (not m.accessible(p["outil"]) or not m.est_porte(p["outil"]) or not m.objets[p["outil"]]["integrite"]):
        portes = sorted(i for i, x in m.objets.items() if m.est_porte(i) and x.get("integrite"))
        raise ErreurMonde("L'outil annoncé doit être accessible et porté.",
                          f"outil « {p['outil']} » : un objet porté et intact, parmi {cibles(m, portes)}, ou vide.")
    for nom in ("reussite", "echec"):
        b = p[nom]
        if not isinstance(b, dict) or set(b) != {"recit", "effets"}:
            recus = sorted(b) if isinstance(b, dict) else type(b).__name__
            raise RefusDeForme("Issue d'improvisation mal formée.",
                              f"{nom} a exactement les champs recit et effets ; reçu : {recus}.")
        if not texte_valide(b["recit"], 600, vide=(nom == "echec" and not p["stat"])):
            raise RefusDeForme("Issue d'improvisation mal formée.",
                              f"{nom}.recit : texte de 600 caractères au plus, sans saut de ligne"
                              + (", non vide (un jet exige un récit d'échec)" if nom == "echec" else ", non vide") + ".")
        if not isinstance(b["effets"], list) or len(b["effets"]) > 4:
            raise RefusDeForme("Issue d'improvisation mal formée.", f"{nom}.effets : une liste de 0 à 4 effets.")
        if sum(e.get("valeur", 0) for e in b["effets"] if isinstance(e, dict) and e.get("operation") == "blesser" and type(e.get("valeur")) is int) > 3:
            raise RefusDeForme("Le total des blessures doit rester mineur : au plus 3 PV.",
                              f"{nom} : la somme des valeurs blesser est au plus 3.")
    if not p["stat"] and p["echec"] != issue(""):
        raise RefusDeForme("Un geste sans jet n'a pas de branche d'échec.",
                          "stat vide : echec = {recit: \"\", effets: []} ; ou une stat et difficulte 10 à 18 pour un jet.")
    effets = compiler_branche(m, p, "reussite")
    echec = compiler_branche(m, p, "echec")
    if any(e[0] == "blessure_improvisee" for e in effets+echec) and not p["stat"]:
        raise RefusDeForme("Un risque de blessure doit être annoncé dans une tentative à confirmer.",
                          "blesser exige un jet : stat et difficulte 10 à 18, ou retire l'effet blesser.")
    if any(e[0] == "endommager" for e in effets+echec) and not p["stat"]:
        raise RefusDeForme("Un risque pour l'outil doit être annoncé avant confirmation.",
                          "user exige un jet : stat et difficulte 10 à 18, ou retire l'effet user.")
    if p["approche"] == "observation" and p["cibles"] and not effets and not echec:
        raise RefusDeForme("L'observation d'une cible existante doit passer par une action de perception du moteur "
                          "(observer, examiner, toucher, lire ou ecouter).",
                          f"pour percevoir {', '.join(p['cibles'])} : action examiner (ou toucher, lire, ecouter) avec "
                          "cet identifiant, pas improviser.")
    # Le libellé vient uniquement des champs validés ; le brouillon du MJ ne décrit pas le monde.
    libelle = libelle_geste(m, p)
    plan = Plan(copy.deepcopy(p), m.data["revision"], libelle + ".", origine=origine)
    recits = {"reussite": "Tu réalises ce " + libelle.lower() + ".",
              "echec": "Tu tentes ce " + libelle.lower() + " sans aboutir."}
    plan.stat, plan.dd, plan.minutes = p["stat"], p["difficulte"], p["minutes"]
    # Le bruit du geste découle au moins du son qu'il produit réellement.
    plan.bruit = max([p["bruit"], *(e[2]["intensite"] for e in effets + echec if e[0] == "son_improvise")])
    # Les descriptions et le DD proposé ne changent pas les contraintes d'une méthode.
    signature = {"version": 1, "intention": normaliser(p["intention"]), "approche": p["approche"], "stat": p["stat"],
        "salle": m.joueur["salle"], "outil": p["outil"], "lumiere": eclairage(m)["niveau"],
        "cibles": [{k: m.objets[id].get(k) for k in ("id", "type", "lieu", "materiau", "integrite", "masse", "attache", "verrouillee", "installation", "usages")}
                   for id in sorted(set(p["cibles"]) | ({p["outil"]} if p["outil"] else set()))],
        "effets": [[{k: e[k] for k in ("operation", "cible", "destination", "valeur")} for e in p[b]["effets"]] for b in ("reussite", "echec")]}
    if p["stat"]:
        plan.cle_arbitrage = "improvisation:" + hashlib.sha256(json.dumps(signature, sort_keys=True).encode()).hexdigest()
        ancien = m.data["arbitrages"].get(plan.cle_arbitrage)
        if ancien:
            plan.dd, plan.origine = ancien["dd"], "arbitrage mémorisé"
        risques = []
        for nom, branche in (("réussite", p["reussite"]), ("échec", p["echec"])):
            pv = sum(e["valeur"] for e in branche["effets"] if e["operation"] == "blesser")
            usure = sum(e["valeur"] for e in branche["effets"] if e["operation"] == "user")
            risques.append(("En cas de réussite : " if nom == "réussite" else "En cas d'échec : ") + recits["reussite" if nom == "réussite" else "echec"].strip() +
                           (f" ({pv} PV perdus)" if pv else "") + (f" (outil : -{usure} intégrité)" if usure else ""))
        plan.risque = "\n".join(risques)
    trace = {"approche": p["approche"], "cibles": p["cibles"], "outil": p["outil"]}
    plan.effets = effets + [("recit_improvise", "", {"texte": recits["reussite"].strip(), **trace})]
    plan.echec = echec + [("recit_improvise", "", {"texte": recits["echec"].strip(), **trace})]
    return plan


def appliquer(m, e, lignes):
    op, cible, valeur = e
    if op == "recit_improvise":
        lignes.append(valeur["texte"])
        m.data.setdefault("gestes_improvises", []).append({"tour": m.data["revision"]+1,
            "lieu": m.joueur["salle"], **copy.deepcopy(valeur)})
        m.data["gestes_improvises"] = m.data["gestes_improvises"][-60:]
    elif op == "blessure_improvisee":
        m.joueur["pv"] -= valeur
        lignes.append(f"Tu perds {valeur} PV.")
    elif op == "marque_improvisee":
        numero = m.data.get("numero_marque", 0)+1
        id = "marque_" + str(numero)
        while id in m.objets:
            numero += 1
            id = "marque_" + str(numero)
        m.data["numero_marque"] = numero
        support = m.objets[cible]
        m.objets[id] = objet(id, "marque " + str(numero), "motif", cible,
            aliases=["marque " + str(numero), "marque", "inscription"], genre="f",
            materiau=support["materiau"], motif="Une marque représente : « " + valeur["texte"] + " ».",
            inscription=valeur["texte"], origine_description="geste du joueur", outil=valeur["outil"])
        lignes.append("Une marque reste sur " + designer(support) + " : « " + valeur["texte"] + " ».")
    elif op == "son_improvise":
        # Il retentit par l'ouïe commune à la fin du geste (``moteur``, ``ouie.SONS``) ; on l'inscrit
        # avec ceux qui l'entendent.
        from .ouie import SONS
        from .sons import entendants
        n = SONS[valeur["intensite"]]
        ids = entendants(m, n)
        son = {"tour": m.data["revision"]+1, "minute": m.data["minutes"], "origine": m.joueur["salle"],
               "nature": "geste sonore", "forme": valeur["forme"],
               "intensite": valeur["intensite"], "bruit": n, "auditeurs": ids}
        m.data.setdefault("sons", []).append(son)
        m.data["sons"] = m.data["sons"][-40:]
        lignes.append(FORMES_SONORES[valeur["forme"]])
        for id in ids:
            if m.visible(id):
                lignes.append(designer(m.objets[id], debut=True) + " entend ce son.")


def contexte(m):
    return {"gestes_recents": [copy.deepcopy(e) for e in m.data.get("gestes_improvises", []) if e["lieu"] == m.joueur["salle"]][-4:],
            "regle": "Les gestes sont des événements passés. Les marques sont des objets persistants ; leur texte n'établit pas la véracité de ce qu'elles affirment."}
