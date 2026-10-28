"""Esprit des PNJ : ce qu'ils perçoivent, ce qu'ils croient et ce qu'ils retiennent.

Un PNJ perçoit avec les règles du joueur, depuis sa propre case : lumière, ligne de vue,
portes. Ses croyances portent une source, une minute et une confiance ; elles peuvent être
fausses ou périmées. Le moteur seul les révise ; Luna ne les modifie pas.

Croyances : ``croyances[sujet][attribut]``, le sujet étant un objet ou « joueur ».
- ``lieu`` : valeur = lieu direct (salle, porteur ou contenant) ou None si l'objet n'est plus
  là où on l'attendait ; ``salle`` et ``case`` disent où il a été vu.
  Une preuve ``possession`` peut accompagner ce lieu : porteur, propriétaire,
  permission et remise autorisée constatés alors. L'adoption de cette preuve
  par les nouvelles n'est pas encore prise en charge.
- ``etat`` : état visible (porte ou contenant ouvert, luminaire allumé ; d'un personnage, ce
  qui presse son corps : ``{"faim", "chaleur", "repos"}`` ; d'une salle, sa lumière là où il se
  tenait et celle de ses propres sources : ``{"eclairee", "niveau", "propre"}``,
  ``constater_lumiere``).
- ``lumiere`` (sujet : un objet) : la lumière qu'il a vue devant, là où il y portait un geste qui
  demande d'y voir (``constater_lumiere_devant``).
- ``pieces`` : ce qu'il croit qu'une bourse contient, su en la tenant ou par un savoir ; jamais
  lu sur l'objet (``planification.enrichir``).
- ``fin`` : destruction ou consommation constatée, datée et conservée même
  après retrait des restes ; distincte de l'état de disponibilité.
- ``verrouillee`` : appris par essai ou savoir ; ouverture ou destruction vue dément le verrou.
- ``eau`` (sujet : une salle) : l'eau qu'il y a vue, en cm (``eau.py``).
- ``prevision`` (sujet : une salle) : avis reçu, avec source et conviction ; valeur =
  [minute du niveau, niveau, montée en cm/h], sans modifier les mesures ``eau``.

Voix (``voix.py``) : ``voix`` liste ceux dont il connaît la voix (il les a entendus parler en les
voyant, ou le scénario les lui fait connaître) ; ``voix_entendues``, les voix inconnues qu'il a
entendues et ce qu'elles ont prétendu ou comment on les a appelées ; ``noms``, ceux dont il a retenu
le nom en les reconnaissant ; ``echange``, les paroles nettes qu'il vient de saisir (``voix.lier``).
Le joueur a ``data["voix_connues"]`` et ``data["voix_entendues"]``. Voir quelqu'un ne fait pas connaître sa voix.
"""
from . import agendas
import copy
from contextlib import contextmanager

from .biens import permis as _permis
from .perception import _par_case, eclairage, faible
from .spatial import (CLES_VUE, _champ, _memo_vue, _murs, _position_vue, a_verifier, carte_lumiere, dans_le_regard,
                      etat_fige, porte_par, poses as salles_posees, sans_memoire, vue_memorisee)
from .vol import proprietaire as _proprietaire

MEMOIRE_MAX = 40
RECENT = 30            # minutes pendant lesquelles ce qu'on a vu, ou ce qu'on vient d'entendre, fait foi
SOURCES = ("vu", "savoir", "essai", "entendu", "se_dit", "devine")   # se_dit : une voix inconnue a dit être lui
ETATS_VISIBLES = {"porte": ("ouverte",), "contenant": ("ouverte",), "luminaire": ("allume", "faible", "charge"),
                  "nourriture": ("disponible",), "consommable": ("disponible",)}
# Un objet porté par quelqu'un d'autre ne se remarque que s'il est encombrant ou allumé.
MASSE_APPARENTE_KG = 1
LONGUEUR_APPARENTE_CM = 50


def pnjs(monde):
    return [id for id, o in monde.objets.items() if o["type"] == "personnage" and not o.get("parti")]


CHAMPS = {"emotions": dict, "signes_lus": dict, "relations": dict, "compagnie": dict, "compagnie_minute": lambda: -1, "portages": dict, "suites": list, "preuves_relations": dict, "croyances": dict, "memoire": list, "intention": lambda: None,
          "recours_propositions": list, "recours_services": list, "recours_intermediaires": list, "service_en_cours": lambda: None,
          "demande_refusee": lambda: None,
          "besoins": dict, "pulsions": list, "renoncements": dict, "visites": dict, **agendas.CHAMPS,
          "libre": int,   # libre : l'instant (dixièmes de seconde) où il aura fini son geste en cours
          "balayage": lambda: None,   # son dernier tour d'horizon : {salle, case, instant}
          "voix": list,   # ceux dont il connaît la voix (``voix.py``)
          "voix_entendues": dict,   # les voix inconnues qu'il a entendues, et ce qu'elles ont prétendu
          "noms": list,   # ceux dont il a retenu le nom en les reconnaissant (``voix.apprendre_nom``)
          "echange": list,   # les paroles nettes qu'il vient de saisir, le temps d'un échange (``voix.lier``)
          "urgences": dict,   # l'effet de seuil de chaque besoin (``deliberation.eveiller``)
          "attentes_bornees": dict,  # un recours borné, jusqu'au changement de ses moyens/entrées
          # le rendez-vous convenu à un appel (``appel``) : qui il attend là où il est (rejoint), ou
          # à qui il a promis de venir (rejoindre)
          "rejoint": lambda: None, "rejoindre": lambda: None,
          # veille : l'instant jusqu'où il attend sans geste en cours (désœuvré, guettant une
          # occasion, assis, près du feu, à l'abri), qu'un événement abrège ; None s'il agit.
          # eveil : l'instant où un événement a changé sa situation (``reconsiderer``) ; il
          # choisit de nouveau son but à la fin de son geste, ou aussitôt s'il attend.
          "veille": lambda: None, "eveil": lambda: None,
          # le geste qu'il vient de manquer, dans cette minute : il ne le retente pas avant la suivante
          "manque": lambda: None,
          # l'instant où a commencé l'attente de son occasion, ou d'un passage, en cours
          # (``pnj.compter_attente`` : le temps passé s'ajoute à ``intention["attente"]``)
          "patience": lambda: None,
          # les personnages qu'il voit, joueur compris (``_percevoir``) ; None avant sa première
          # perception, qui ne fait que l'établir
          "en_vue": lambda: None,
          # la dernière réponse refusée de chaque demande, et ce qu'il croyait de sa cause
          # (``deliberation.retenir_refus``)
          "refus": list,
          # l'état qu'il vient de donner de sa main à une chose : {objet: {attribut: [valeur, minute]}},
          # depuis moins de ``deliberation.DEFAIT`` minutes (``deliberation.changer_etat``)
          "donne": dict,
          # Le dernier appel à l'aide et la fin de son désarroi : ce suivi de recours ne doit
          # pas disparaître avec les quarante souvenirs de la mémoire courante.
          "secours": lambda: None,
          "derniere_confidence": lambda: None,  # minute de la dernière nouvelle confiée
          "faits_dits": dict,  # identités et dernières valeurs dites, hors mémoire courante (social)
          # Besoins bloqués ayant déjà motivé un appel depuis leur dernier apaisement.
          "detresses_appelees": list,
          "aides_attendues": dict,
          # Salles examinées sans y retrouver la personne cherchée, jusqu'à un nouvel indice
          # local, indépendamment de la mémoire courante et du temps écoulé.
          "recherches": dict,
          # Contenus des indices déjà utilisés par personne et lieu, hors mémoire bornée.
          "indices_recherche": dict,
          "presence_recherche": dict}  # Dernière localisation positive, même après un constat d'absence.
ETAPE = {"operation", "cible", "outil", "lieu", "condition"}
CLES_INTENTION = {"but", "motif", "plan", "depuis", "attente"}


def lire(monde, id):
    """Esprit en lecture seule : une consultation ne crée rien dans l'état."""
    if id == "joueur":
        return {**{k: f() for k, f in CHAMPS.items()}, **monde.data.get("connaissances_joueur", {})}
    return monde.data.get("esprits", {}).get(id) or {k: f() for k, f in CHAMPS.items()}


def esprit(monde, id):
    if id == "joueur":
        return monde.data.setdefault("connaissances_joueur", {"croyances": {}, "memoire": [], "faits_dits": {}})
    e = monde.data.setdefault("esprits", {}).setdefault(id, {})
    if not CHAMPS.keys() <= e.keys():
        for cle, defaut in CHAMPS.items():
            if cle not in e:
                e[cle] = defaut()
    return e


def installer(monde):
    monde.data.setdefault("esprits", {})
    personnages = set(pnjs(monde)) | {"joueur"}
    for id in pnjs(monde):
        nouveau = "voix" not in monde.data["esprits"].get(id, {})
        migrer_confidences = "faits_dits" not in monde.data["esprits"].get(id, {})
        migrer_recherches = "recherches" not in monde.data["esprits"].get(id, {})
        migrer_indices = "indices_recherche" not in monde.data["esprits"].get(id, {})
        from .relations import installer as installer_relations
        installer_relations(monde, id)
        e = esprit(monde, id)
        for fait in e["faits_dits"].values():
            if isinstance(fait["dit_a"], list):
                fait["dit_a"] = {a: copy.deepcopy(fait["valeur"]) for a in fait["dit_a"]}
        if migrer_confidences:
            from .social import migrer_dits
            migrer_dits(monde, id)
        for souvenir in e["memoire"]:
            if migrer_recherches and souvenir["type"] == "appel_sans_reponse":
                salles = e["recherches"].setdefault(souvenir["qui"], {})
                salles[souvenir["salle"]] = max(salles.get(souvenir["salle"], -1), souvenir["minute"])
        if migrer_indices:
            from .deliberation import consommer_indices_recherche
            for qui, salles in e["recherches"].items():
                for salle in salles:
                    consommer_indices_recherche(monde, id, qui, salle)
        if e["secours"] is None:
            appels = [s for s in e["memoire"] if s["type"] == "appel"]
            if appels:
                from .deliberation import DESESPOIR, urgents
                e["secours"] = {"minute": appels[-1]["minute"],
                                "apaise": (bool(appels[-1].get("apaise"))
                                           and e["besoins"].get("securite", 0) < DESESPOIR
                                           and "securite" not in urgents(monde, id))}
        if nouveau:
            # Début de partie : le scénario déclare qui se connaît déjà (un savoir à son sujet) ;
            # il connaît leur voix. Voir quelqu'un, plus tard, n'y ajoute rien (``voix``).
            e["voix"] = sorted(x for x, attributs in e["croyances"].items() if x in personnages and x != id
                               and any(c.get("source") == "savoir" for c in attributs.values()))
        o = monde.objets[id]
        # Anciennes parties : le trajet devient intention.
        trajet = o.pop("trajet", None)
        if trajet and e["intention"] is None:
            e["intention"] = {"but": {"type": "rejoindre", "lieu": trajet["vers"]}}
        i = e["intention"]
        if i is not None and set(i) - {"attitude"} != CLES_INTENTION:
            # Intention du jalon A : un réflexe d'alerte, sans plan enregistré.
            e["intention"] = {"but": i["but"], "motif": "alerte", "plan": [
                {"operation": "aller", "cible": "", "outil": "", "lieu": i["but"]["lieu"], "condition": ""}],
                              "depuis": i.get("depuis", monde.data["minutes"]), "attente": 0}
        from .deliberation import installer as installer_besoins
        installer_besoins(monde, id)
    # Le joueur arrive en étranger : il ne connaît encore aucune voix.
    from .signes import installer as installer_signes
    installer_signes(monde)
    monde.data.setdefault("voix_connues", [])
    monde.data.setdefault("voix_entendues", {})


def connaitre(monde, qui, autre):
    """``qui`` connaît désormais la voix d'``autre`` (``voix.connaitre``)."""
    from .voix import connaitre as apprendre
    apprendre(monde, qui, autre)


def _croyance_valide(monde, attribut, c):
    assert (isinstance(c, dict) and isinstance(c.get("source"), str)
            and (c["source"] in SOURCES or c["source"].startswith("dit:")) and type(c.get("minute")) is int
            and isinstance(c.get("confiance"), (int, float)) and 0 <= c["confiance"] <= 1), "Croyance mal formée"
    if "confie" in c:
        s = c["confie"]
        assert (isinstance(s, dict) and set(s) == {"valeur", "dit_a"} and isinstance(s["dit_a"], list)
                and all(isinstance(x, str) for x in s["dit_a"])
                and len(s["dit_a"]) == len(set(s["dit_a"]))), "Constat confié invalide"
    if "origine" in c:
        assert (isinstance(c["origine"], dict) and set(c["origine"]) == {"source", "minute"}
                and isinstance(c["origine"]["source"], str)
                and type(c["origine"]["minute"]) is int), "Origine de localisation invalide"
    if attribut == "lieu":
        # Une croyance peut survivre à son objet (détruit, retiré).
        assert (set(c) >= {"valeur", "salle", "case"}
                and (c["valeur"] is None or isinstance(c["valeur"], str))
                and (c["salle"] is None or c["salle"] in monde.data["salles"])
                and (c["case"] is None or (isinstance(c["case"], list) and len(c["case"]) == 2))), "Croyance de lieu invalide"
        if "possession" in c:
            p = c["possession"]
            assert (isinstance(p, dict) and set(p) == {"porteur", "proprietaire", "permis", "remis_par", "remise_autorisee"}
                    and all(p[k] is None or isinstance(p[k], str)
                            for k in ("porteur", "proprietaire", "remis_par"))
                    and type(p["permis"]) is bool and type(p["remise_autorisee"]) is bool), "Possession constatée invalide"
    elif attribut == "fin":
        assert c.get("valeur") in ("detruit", "consomme"), "Fin d'objet crue invalide"
    elif attribut == "etat":
        # Des états vrais ou faux ; d'une salle, aussi les niveaux de lumière vus (0 à 2).
        assert isinstance(c.get("valeur"), dict) and all(
            type(v) is bool or k in ("niveau", "propre", "blessure") and type(v) is int and 0 <= v <= 2
            for k, v in c["valeur"].items()), "Croyance d'état invalide"
    elif attribut == "lumiere":
        # La lumière vue devant un objet, là où un geste demande d'y voir (0 à 2).
        # ``allumees`` : les sources qu'il croyait alors allumées et posées dans la salle.
        assert (type(c.get("valeur")) is int and 0 <= c["valeur"] <= 2
                and isinstance(c.get("allumees", []), list)
                and all(isinstance(k, str) for k in c.get("allumees", []))), "Croyance de lumière invalide"
    elif attribut == "pieces":
        # Ce qu'il croit qu'une bourse contient : appris en la tenant, ou un savoir du scénario.
        assert type(c.get("valeur")) is int and c["valeur"] >= 0, "Croyance de pièces invalide"
    elif attribut == "eau":
        # La hauteur vue ; le niveau qu'elle donnait, le repère et la vitesse qu'on en tire.
        assert (type(c.get("valeur")) is int and c["valeur"] >= 0
                and all(c.get(k) is None or type(c[k]) is int for k in ("niveau", "montee"))
                and (c.get("repere") is None or isinstance(c["repere"], list) and len(c["repere"]) == 2
                     and all(type(v) is int for v in c["repere"]))), "Croyance d'eau invalide"
    elif attribut == "prevision":
        assert ((type(c.get("valeur")) is bool or isinstance(c.get("valeur"), list) and len(c["valeur"]) == 3
                and all(type(v) is int for v in c["valeur"]))
                and type(c.get("rang", 0)) is int and 0 <= c.get("rang", 0) <= 3), "Prévision invalide"
    elif attribut == "verrouillee":
        assert type(c.get("valeur")) is bool, "Attribut de croyance inconnu"
    elif attribut.startswith("attitude:") or attribut in ("emotion", "intention", "parole_doutee"):
        from .signes import SENS
        assert c["valeur"] in SENS and isinstance(c.get("signe"), str) and (c["source"] == "devine" or c["source"].startswith("dit:")), "Lecture invalide"
    elif attribut == "violence":
        assert isinstance(c.get("valeur"), dict) and all(
            isinstance(v, str) and isinstance(d, dict) and set(d) == {"minute", "menace", "operation", "clos"}
            and type(d["minute"]) is int and type(d["menace"]) is bool
            and type(d["clos"]) is bool
            and d["operation"] in ("frapper", "assommer", "pousser")
            for v, d in c["valeur"].items()), "Violence perçue invalide"
    elif attribut == "passage":
        from .matiere import valider_passage
        # Une forme peut être crue fausse ; sa structure reste celle d'une géométrie.
        valider_passage({"id": "croyance", "bloque_passage": True}, c.get("valeur"))
    else:
        # Les relations ne sont plus des croyances ; les avis sont dérivés par ``croyance``.
        assert False, "Attribut de croyance inconnu"


def _contre_offre_valide(monde, id, refus):
    from .deliberation import condition_valide
    o = refus["contre_offre"]
    if (not isinstance(o, dict) or set(o) != {"etat", "debiteur", "creancier", "condition", "contrepartie"}
            or o["etat"] != "offre" or o["debiteur"] != refus["de"] or o["creancier"] != id
            or o["contrepartie"] not in ({"type": "objet", "objet": refus.get("objet")},
                                         {"type": "part", "objet": refus.get("objet")})):
        return False
    c = o["condition"]
    return (isinstance(c, dict) and (
        set(c) == {"type", "montant"} and c["type"] == "pieces" and type(c["montant"]) is int and c["montant"] > 0
        or set(c) == {"type", "condition"} and c["type"] == "tache"
        and isinstance(c["condition"], dict) and c["condition"].get("servir") == o["debiteur"]
        and condition_valide(monde, c["condition"])))


def verifier(monde):
    if "connaissances_joueur" in monde.data:
        e = monde.data["connaissances_joueur"]
        assert isinstance(e, dict) and set(e) == {"croyances", "memoire", "faits_dits"}, "Connaissances du joueur invalides"
        assert isinstance(e["croyances"], dict), "Croyances du joueur invalides"
        for sujet, attributs in e["croyances"].items():
            assert (isinstance(sujet, str) and isinstance(attributs, dict)
                    and (sujet in monde.data["salles"] and set(attributs) <= {"eau", "prevision"}
                         or set(attributs) <= {"fin", "lieu", "etat", "verrouillee"})), "Perception du joueur invalide"
            for attribut, c in attributs.items():
                _croyance_valide(monde, attribut, c)
        assert isinstance(e["memoire"], list) and len(e["memoire"]) <= MEMOIRE_MAX, "Mémoire du joueur invalide"
        from .social import DITS_MAX
        assert isinstance(e["faits_dits"], dict) and len(e["faits_dits"]) <= DITS_MAX, "Faits dits du joueur invalides"
    from .signes import verifier as verifier_signes
    verifier_signes(monde)
    esprits = monde.data.get("esprits", {})
    assert isinstance(esprits, dict), "Esprits invalides"
    for id, e in esprits.items():
        assert id in monde.objets and monde.objets[id]["type"] == "personnage", "Esprit sans personnage"
        assert agendas.champs_esprit(e) == set(CHAMPS), "Esprit mal formé"
        from .relations import verifier as verifier_relations
        verifier_relations(monde, id)
        from .pnj_propositions import verifier as verifier_recours
        verifier_recours(e)
        p = monde.objets[id].get("profil")
        if p is not None:
            from .deliberation import verifier_profil
            verifier_profil(monde, id, p)
        from .deliberation import seuils
        assert (isinstance(e["besoins"], dict) and set(e["besoins"]) <= (set(seuils(monde, id)) if p else {"faim", "repos", "chaleur"})
                and all(isinstance(v, (int, float)) and 0 <= v <= 100 for v in e["besoins"].values())), "Besoins de PNJ invalides"
        # Satisfaite (True), rompue (False), jamais satisfaite depuis qu'il la connaît (None).
        assert (isinstance(e["pulsions"], list) and len(e["pulsions"]) in (0, len(p["pulsions"]) if p else 0)
                and all(v is None or type(v) is bool for v in e["pulsions"])), "Pulsions de PNJ invalides"
        # Entiers : anciennes sauvegardes sans cause, conservées sans inventer
        # de preuve. Les renoncements nouveaux n'ont aucune date de réveil.
        assert isinstance(e["renoncements"], dict) and all(
            isinstance(k, str) and (type(v) is int or isinstance(v, list) and all(
                isinstance(r, dict) and set(r) == {"instant", "but", "cause"}
                and type(r["instant"]) is int and r["instant"] >= 0 and isinstance(r["but"], dict)
                and isinstance(r["cause"], dict)
                and r["cause"].get("type") in ("temoins", "passage", "corps")
                and r["cause"].get("salle") in monde.data["salles"]
                and isinstance(r["cause"].get("etape"), dict)
                and (r["cause"]["type"] == "corps" or
                     (isinstance(r["cause"].get("temoins"), dict) and "nature" in r["cause"]
                     if r["cause"]["type"] == "temoins" else
                     isinstance(r["cause"].get("arrivees"), list)
                     and all(s in monde.data["salles"] and isinstance(c, list) and len(c) == 2
                             and all(type(x) is int for x in c) for s, c in r["cause"]["arrivees"])))
                for r in v)) for k, v in e["renoncements"].items()), "Renoncements invalides"
        assert isinstance(e["attentes_bornees"], dict) and all(
            isinstance(k, str) and isinstance(v, str) for k, v in e["attentes_bornees"].items()
        ), "Attentes de recherche invalides"
        assert all(b in seuils(monde, id) and isinstance(u, dict) and set(u) == {"etat", "depuis"}
                   and u["etat"] in ("presse", "apaise", "attente") and type(u["depuis"]) is int
                   for b, u in e["urgences"].items()), "Urgences de PNJ invalides"
        assert type(e["libre"]) is int and e["libre"] >= 0, "Geste en cours de PNJ invalide"
        assert (e["derniere_confidence"] is None or type(e["derniere_confidence"]) is int
                and e["derniere_confidence"] >= 0), "Date de confidence invalide"
        assert all(v is None or type(v) is int and v >= 0 for v in (e["veille"], e["eveil"])),             "Attente ou éveil de PNJ invalide"
        assert e["patience"] is None or type(e["patience"]) is int, "Patience de PNJ invalide"
        assert e["manque"] is None or (isinstance(e["manque"], dict) and set(e["manque"]) == {"etape", "minute"}
                                       and isinstance(e["manque"]["etape"], dict)
                                       and type(e["manque"]["minute"]) is int), "Geste manqué de PNJ invalide"
        assert e["en_vue"] is None or (isinstance(e["en_vue"], list) and e["en_vue"] == sorted(set(e["en_vue"]))
                                       and all(isinstance(x, str) for x in e["en_vue"])), "Personnages en vue invalides"
        b = e["balayage"]
        assert b is None or (isinstance(b, dict) and set(b) == {"salle", "case", "instant"}
                             and b["salle"] in monde.data["salles"] and isinstance(b["case"], list)
                             and len(b["case"]) == 2 and all(type(v) is int for v in b["case"])
                             and type(b["instant"]) is int and b["instant"] >= 0), "Tour d'horizon de PNJ invalide"
        assert all(s in monde.data["salles"] and type(v) is int for s, v in e["visites"].items()), "Visites invalides"
        from .appel import verifier as verifier_rendez_vous
        verifier_rendez_vous(monde, e)
        assert isinstance(e["voix"], list) and all(
            isinstance(x, str) for x in e["voix"]  # Comme une croyance, il survit à qui a quitté la partie.
        ) and len(set(e["voix"])) == len(e["voix"]), "Voix connues invalides"
        from .voix import verifier_echange, verifier_entrees
        verifier_entrees(e["voix_entendues"])
        verifier_echange(e["echange"])
        assert isinstance(e["noms"], list) and all(isinstance(x, str) for x in e["noms"]) and len(set(e["noms"])) == len(e["noms"]), "Noms retenus invalides"
        agendas.verifier(monde, id)
        for sujet, attributs in e["croyances"].items():
            assert isinstance(sujet, str) and isinstance(attributs, dict), "Sujet de croyance invalide"
            for attribut, c in attributs.items():
                _croyance_valide(monde, attribut, c)
        from .deliberation import DETAILS_REFUS
        assert isinstance(e.get("refus", []), list) and all(
            isinstance(s, dict) and set(s) <= {"de", "operation", "raison", "minute", "cause", *DETAILS_REFUS}
            and isinstance(s["de"], str) and isinstance(s["operation"], str) and isinstance(s["raison"], str)
            and type(s["minute"]) is int and type(s.get("prix", 0)) is int
            and type(s.get("condition_tenue", False)) is bool
            and ("repere" not in s or isinstance(s["repere"], dict)
                 and set(s["repere"]) == {"lieu", "revision"}
                 and s["repere"]["lieu"] in monde.data["salles"]
                 and type(s["repere"]["revision"]) is int and s["repere"]["revision"] >= 0)
            and ("information" not in s or isinstance(s["information"], dict)
                 and {"lieu", "minute", "source"} <= set(s["information"]) <= {"lieu", "minute", "source", "origine"}
                 and s["information"]["lieu"] in monde.data["salles"]
                 and type(s["information"]["minute"]) is int
                 and isinstance(s["information"]["source"], str)
                 and ("origine" not in s["information"] or isinstance(s["information"]["origine"], dict)
                      and set(s["information"]["origine"]) == {"source", "minute"}
                      and isinstance(s["information"]["origine"]["source"], str)
                      and type(s["information"]["origine"]["minute"]) is int))
            and ("contre_offre" not in s or _contre_offre_valide(monde, id, s))
            and isinstance(s.get("cause", []), list) and all(isinstance(f, list) and len(f) == 4 for f in s.get("cause", []))
            and ("offre" not in s or isinstance(s["offre"], dict) and set(s["offre"]) == {"cause", "gain"}
                 and isinstance(s["offre"]["gain"], (int, float)) and s["offre"]["gain"] >= 0
                 and isinstance(s["offre"]["cause"], list)
                 and all(isinstance(f, list) and len(f) == 4 for f in s["offre"]["cause"]))
            for s in e.get("refus", [])
        ), "Refus retenus de PNJ invalides"
        from .deliberation import ETATS_DONNES
        assert isinstance(e["donne"], dict) and all(
            isinstance(o, str) and isinstance(a, dict) and all(
                x in ETATS_DONNES and isinstance(v, list) and len(v) == 2 and type(v[1]) is int for x, v in a.items())
            for o, a in e["donne"].items()), "États donnés de PNJ invalides"
        assert (isinstance(e["memoire"], list) and len(e["memoire"]) <= MEMOIRE_MAX
                and all(isinstance(s, dict) and isinstance(s.get("type"), str) and type(s.get("minute")) is int
                        for s in e["memoire"])), "Mémoire de PNJ invalide"
        from .social import DITS_MAX
        assert (isinstance(e["faits_dits"], dict) and len(e["faits_dits"]) <= DITS_MAX
                and all(isinstance(k, str) and isinstance(v, dict) and {"valeur", "dit_a"} <= set(v)
                        and set(v) <= {"valeur", "dit_a", "entendu_a", "valeur_inconnue", "portee_a"}
                        and isinstance(v.get("portee_a", {}), dict)
                        and all(isinstance(a, str) and isinstance(p, list) and len(p) == 2
                                and p[0] in (0, 1, 2) and p[1] in (-1, 0, 1)
                                for a, p in v.get("portee_a", {}).items())
                        and isinstance(v.get("valeur_inconnue", False), bool)
                        and isinstance(v["dit_a"], dict) and all(isinstance(a, str) for a in v["dit_a"])
                        and isinstance(v.get("entendu_a", {}), dict)
                        and all(isinstance(a, str) and isinstance(valeurs, list)
                                for a, valeurs in v.get("entendu_a", {}).items())
                        for k, v in e["faits_dits"].items())), "Faits dits invalides"
        assert e["secours"] is None or (
            isinstance(e["secours"], dict) and set(e["secours"]) == {"minute", "apaise"}
            and type(e["secours"]["minute"]) is int and type(e["secours"]["apaise"]) is bool
        ), "Suivi de secours de PNJ invalide"
        assert (isinstance(e["detresses_appelees"], list)
                and all(b in e["besoins"] for b in e["detresses_appelees"])
                and len(set(e["detresses_appelees"])) == len(e["detresses_appelees"])), "Détresses appelées invalides"
        from .deliberation import condition_valide
        assert isinstance(e["aides_attendues"], dict) and all(
            o in monde.objets and isinstance(x, dict) and set(x) == {"qui", "condition", "minute"}
            and x["qui"] in monde.objets and type(x["minute"]) is int
            and x["condition"].get("objet") == o and condition_valide(monde, x["condition"])
            for o, x in e["aides_attendues"].items()), "Aides attendues invalides"
        assert isinstance(e["recherches"], dict) and all(
            q in monde.objets or q == "joueur" for q in e["recherches"]
        ) and all(isinstance(salles, dict) and all(s in monde.data["salles"] and type(t) is int
                  for s, t in salles.items()) for salles in e["recherches"].values()), "Recherches de PNJ invalides"
        assert isinstance(e["indices_recherche"], dict) and all(
            (q in monde.objets or q == "joueur") and isinstance(salles, dict)
            and all(s in monde.data["salles"] and isinstance(indices, list)
                    and all(isinstance(x, list) and len(x) in (3, 4)
                            and ((x[0] == "presence" and len(x) == 3 and type(x[1]) is int and 0 <= x[1] <= 2)
                                 or (x[0] == "bruit" and len(x) == 4 and type(x[1]) is int and x[1] > 0
                                     and (x[2] is None or x[2] == "joueur" or x[2] in monde.objets)))
                            and (x[-1] is None or isinstance(x[-1], list) and len(x[-1]) == 2
                                 and all(type(n) is int for n in x[-1])) for x in indices)
                    for s, indices in salles.items())
            for q, salles in e["indices_recherche"].items()), "Indices de recherche invalides"
        assert isinstance(e["presence_recherche"], dict) and all(
            (q in monde.objets or q == "joueur") and isinstance(p, list) and len(p) == 2
            and p[0] in monde.data["salles"] and (p[1] is None or isinstance(p[1], list)
                and len(p[1]) == 2 and all(type(n) is int for n in p[1]))
            for q, p in e["presence_recherche"].items()), "Présences de recherche invalides"
        i = e["intention"]
        assert i is None or (isinstance(i, dict) and set(i) - {"attitude"} == CLES_INTENTION
                             and isinstance(i["but"], dict) and isinstance(i["but"].get("type"), str)
                             and isinstance(i["motif"], str) and type(i["depuis"]) is int
                             and type(i["attente"]) is int and i["attente"] >= 0
                             and isinstance(i["plan"], list)), "Intention de PNJ invalide"
        if i:
            from .deliberation import OPERATIONS
            for etape in i["plan"]:
                # Un geste social porte son contenu : ce qui est affirmé, ou la tâche confiée.
                assert (isinstance(etape, dict) and set(etape) in (ETAPE, ETAPE | {"contenu"})
                        and etape["operation"] in OPERATIONS and isinstance(etape.get("contenu", {}), dict)
                        and etape["condition"] in ("", "sans_temoin", "dans_le_dos")), "Étape de plan invalide"


def croyance(monde, id, sujet, attribut):
    """Sa croyance sur ``sujet`` (``attribut``), telle quelle, ou None. Ce qu'il éprouve envers une
    personne ne se lit que par ``relations`` (``relations.croyance``)."""
    from .relations import FIABLE, croyance as relation
    if attribut == FIABLE:
        return relation(monde, id, sujet)
    c = lire(monde, id)["croyances"].get(sujet, {}).get(attribut)
    if c and "signe" in c:
        limite = RECENT if attribut in ("emotion", "intention", "parole_doutee") else 120
        if monde.data["minutes"] - c["minute"] >= limite:
            return None
    return c


def croire(monde, id, sujet, attribut, valeur, source, confiance=1.0, **lieu):
    monde_minute = monde.data["minutes"]
    ancienne = lire(monde, id)["croyances"].get(sujet, {}).get(attribut)
    croyance = {"valeur": valeur, "source": source, "minute": monde_minute, "confiance": confiance, **lieu}
    esprit(monde, id)["croyances"].setdefault(sujet, {})[attribut] = croyance
    observations = getattr(monde, "_observations_communes", None)
    if observations is not None and source == "vu" and id in observations:
        observations[id].append({"type": "affirmation", "sujet": sujet,
                                 "attribut": attribut, "valeur": copy.deepcopy(valeur),
                                 "details": {k: copy.deepcopy(v) for k, v in lieu.items()
                                             if k in ("montee", "niveau", "repere")}})
    if attribut == "lieu" and source in ("vu", "entendu") and valeur in monde.data["salles"]:
        # Le contexte d'une réponse retenue change avec un déplacement
        # réellement perçu de la personne, jamais avec une date, une autre
        # case dans la même salle ou la répétition d'un renseignement tiers.
        for reponse in esprit(monde, id).get("refus", ()):
            if reponse["operation"] != "enqueter_lieu" or reponse.get("objet") != sujet:
                continue
            repere = reponse.get("repere")
            if repere is None or repere["lieu"] != valeur:
                reponse["repere"] = {"lieu": valeur, "revision": (repere["revision"] if repere else 0) + 1}
    if attribut == "lieu":
        from .defense import approche_vue
        approche_vue(monde, id, sujet, ancienne or {}, croyance)
    if attribut == "eau" and source in ("vu", "essai"):
        # Une preuve propre postérieure dément l'avis durablement : le perdre de vue
        # ensuite ne doit pas ressusciter une ancienne prévision reçue.
        avis = [a for a in lire(monde, id)["croyances"].values() if "prevision" in a]
        propre = prevision_propre(monde, id) if avis else None
        if propre and propre["source"] in ("vu", "essai"):
            for a in avis:
                if propre["minute"] > a["prevision"]["minute"]:
                    del a["prevision"]
    from .social import reviser_dits
    if attribut != "prevision":  # Le fait dit est la menace, pas les coefficients de sa prévision.
        reviser_dits(monde, id, sujet, attribut, valeur, precedente=ancienne or {}, **lieu)
    if attribut == "lieu" and sujet in lire(monde, id)["recherches"] and valeur in monde.data["salles"]:
        # Un contenu positif nouveau rouvre ce lieu seul ; une répétition ou une absence,
        # même datée de nouveau, n'annule pas le résultat d'une recherche.
        from .deliberation import contact_recherche, indice_recherche
        if source == "vu" and (not ancienne or ancienne["valeur"] != valeur
                               or ancienne.get("case") != lieu.get("case")):
            contact_recherche(monde, id, sujet, valeur)
        indice_recherche(monde, id, valeur, sujet)
    if attribut == "etat" and (valeur.get("conscient") is False or valeur.get("reddition")):
        from .defense import constater_fin
        constater_fin(monde, id, sujet)


def poids_source(monde, id, c):
    """Poids d'un avis (§ 7.3), distinct de sa conviction ; aucune persuasion aléatoire."""
    source = c["source"]
    if source.startswith("dit:"):
        from .voix import auteur_dit
        from .relations import envers, ETRANGER
        auteur, inconnue = auteur_dit(source)
        r = ETRANGER if inconnue else envers(monde, id, auteur)
        return .7 * r["confiance"] / 100 * (1 + r["affection"] / 200)
    return {"vu": 1, "essai": 1, "savoir": 1, "entendu": .8, "devine": .4}.get(source, 0)


def prevision_propre(monde, id):
    """L'estimation et la qualité de ses preuves, borne comprise, sans les modifier."""
    from .eau import estimation, borner
    e = estimation(monde, id)
    if e is None:
        return None
    vues = [c for a in lire(monde, id)["croyances"].values()
            if (c := a.get("eau")) and c.get("niveau") is not None]
    ancre = max(vues, key=lambda c: (c["minute"], c["niveau"]))
    pente = max((c for c in vues if c.get("repere") is not None and c.get("montee") is not None),
                key=lambda c: (c["repere"][0], c["montee"]))
    e, borne = borner(monde, id, (ancre["minute"], ancre["niveau"], e[2]))
    preuves = [ancre, pente] + ([borne] if borne else [])
    faible = min(preuves, key=lambda c: poids_source(monde, id, c) * c["confiance"])
    minute = max(ancre["minute"], pente["repere"][0], borne["minute"] if borne else 0)
    return {"valeur": list(e), "minute": minute,
            "source": faible["source"], "confiance": faible["confiance"]}


def prevision(monde, id, salle):
    """Prévision retenue pour ce lieu : preuves propres ou avis, jamais une mesure inventée.

    Une estimation propre étayée plus récente dément l'ancien avis ; à défaut, poids × conviction
    départage, l'égalité gardant la croyance déjà acquise.
    """
    propre = prevision_propre(monde, id)
    recue = lire(monde, id)["croyances"].get(salle, {}).get("prevision")
    if recue is None:
        return propre
    if propre and (propre["source"] in ("vu", "essai") and propre["minute"] > recue["minute"]
                   or poids_source(monde, id, propre) * propre["confiance"]
                   > poids_source(monde, id, recue) * recue["confiance"]):
        return propre
    if type(recue["valeur"]) is not bool:
        from .eau import borner
        valeur, _ = borner(monde, id, recue["valeur"])
        return {**recue, "valeur": list(valeur)}
    return recue


def recevoir_prevision(monde, id, locuteur, noyau, rang, *, departage=False):
    from .voix import source_dite
    from .pnj import _chroniquer
    actuelle = prevision(monde, id, noyau["objet"])
    candidate = {"valeur": noyau["prevision"], "minute": noyau["observe"],
                 "source": source_dite(monde, id, locuteur), "confiance": noyau["conviction"]}
    poids = round(poids_source(monde, id, candidate) * candidate["confiance"], 12)
    acquis = round(poids_source(monde, id, actuelle) * actuelle["confiance"], 12) if actuelle else 0
    if (actuelle and actuelle["source"] in ("vu", "essai") and actuelle["minute"] > candidate["minute"]
            or poids < acquis or poids == acquis and not departage):
        return "doute"
    croire(monde, id, noyau["objet"], "prevision", copy.deepcopy(candidate["valeur"]),
           candidate["source"], candidate["confiance"], minute=candidate["minute"], rang=rang + 1)
    from .social import _qui
    _chroniquer(monde, id, f"{_qui(monde, id)} révise sa prévision de l'eau.", "social")
    monde.data["chronique"][-1]["changement_avis"] = "dit"
    reconsiderer(monde, id)
    return "crue"


def memoriser(monde, id, evenement):
    if evenement["type"] == "dit" and "valeur" in evenement:
        from .social import retenir_dit
        retenir_dit(monde, id, evenement["a"], {"type": "affirmation", **{
            k: evenement[k] for k in ("sujet", "attribut", "valeur")}})
    memoire = esprit(monde, id)["memoire"]
    souvenir = copy.deepcopy({"minute": monde.data["minutes"], **evenement})
    from .relations import identifier
    from .temps import instant
    identifier(souvenir, instant(monde))
    memoire.append(souvenir)
    del memoire[:-MEMOIRE_MAX]
    from .relations import souvenir as eprouver_souvenir
    eprouver_souvenir(monde, id, souvenir)
    from .defense import retenir as retenir_violence
    retenir_violence(monde, id, souvenir)


def dernier_son(monde, id):
    """Le dernier bruit qu'il a entendu sans en voir la cause, tel que l'ouïe commune le retient
    (``ouie._bruit_inconnu`` : un souvenir par lieu) : {minute, salle, nature, niveau[, qui]} ; None.
    La case d'où il l'a situé ne sert qu'à aller voir : le MJ n'en reçoit que le lieu."""
    sons = [s for s in lire(monde, id)["memoire"] if s["type"] == "bruit"]
    return {k: v for k, v in copy.deepcopy(sons[-1]).items() if k not in ("type", "case")} if sons else None


def _porteur(monde, o):
    """Personnage (ou joueur) qui porte l'objet, s'il y en a un."""
    vus, lieu = set(), o["lieu"]
    while lieu in monde.objets and lieu not in vus:
        vus.add(lieu)
        if monde.objets[lieu]["type"] == "personnage":
            return lieu
        lieu = monde.objets[lieu]["lieu"]
    return "joueur" if lieu == "joueur" else None


def apparent(o):
    """Porté par quelqu'un, un objet ne se remarque que s'il est encombrant ou allumé."""
    return bool(o.get("allume") or o.get("masse", 0) >= MASSE_APPARENTE_KG
                or o.get("longueur_cm", 0) >= LONGUEUR_APPARENTE_CM)


def cache_par_porteur(monde, o, observateur):
    """Vrai pour un objet porté par un autre personnage que l'observateur et trop discret pour être vu."""
    porteur = _porteur(monde, o)
    return (porteur not in (None, observateur) and o["type"] != "partie_corps" and not apparent(o))


def _remarquable(acteur, o):
    """Ni lui-même, ni un détail, ni ce qui est incorporé, ni une surface ou une partie du corps."""
    return not (o["id"] == acteur or o.get("detail_local") or o.get("incorpore")
                or o["type"] in ("surface", "partie_corps"))


def _pertinent(monde, acteur, o):
    return _remarquable(acteur, o) and not cache_par_porteur(monde, o, acteur)


def percus(monde, acteur):
    """Entités perçues maintenant par un PNJ et lieux observés : {id: (salle, case)}, champ.

    Pendant la vie des PNJ (``spatial.vue_memorisee``), la perception d'un acteur est gardée tant
    que l'état dont elle dépend n'a pas changé (``spatial.etat_vue``) ; dans un état nouveau, elle se
    tire de la précédente quand c'est possible (``_percus_depuis``)."""
    from .corps import conscient
    from .presence import parti
    if not conscient(monde, acteur) or parti(monde, acteur):
        return {}, set()
    memo = _memo_vue(monde) if monde.data.get("mode_cases") else None
    if memo is None:
        return _percus(monde, acteur, None)
    if ("percus", acteur) not in memo:
        derniers = monde._cache_vue.setdefault("percus_derniers", {})
        dernier = derniers.pop(acteur, None)
        trouve = None if dernier is None else _percus_depuis(monde, acteur, memo, dernier)
        memo["percus", acteur] = trouve if trouve is not None else _percus(monde, acteur, memo)
        if "etat" in memo and monde.objets[acteur]["lieu"] in monde.data["salles"]:
            derniers[acteur] = (memo["etat"], memo["percus", acteur][0], _champ(monde, acteur, memo), memo)
    vus, champ = memo["percus", acteur]
    if a_verifier():
        with sans_memoire(monde):
            frais = _percus(monde, acteur, None)
        assert frais == (vus, champ), f"Perception mémorisée périmée : {acteur}"
    return {id: (s, None if c is None else list(c)) for id, (s, c) in vus.items()}, set(champ)


def _percus(monde, acteur, memo):
    salle = monde.objets[acteur]["lieu"]
    poses = salles_posees(monde, memo)
    # Ce qu'il porte lui-même, il le sait sans le voir.
    vus = {id: (None, None) for id, o in monde.objets.items()
           if poses[id] in (None, acteur) and porte_par(monde, id, acteur) and _pertinent(monde, acteur, o)}
    if salle not in monde.data["salles"]:
        return vus, set()
    if monde.data.get("mode_cases"):
        champ = _champ(monde, acteur, memo)
        salles_du_champ = {c[0] for c in champ}
        salles_vues = [s for s in monde.data["salles"] if s in salles_du_champ]
        for id, o in monde.objets.items():
            if id in vus:
                continue
            vu = _vu_dans_le_champ(monde, memo, acteur, id, o, poses[id], champ, salles_du_champ, salles_vues)
            if vu is not None:
                vus[id] = vu
        j = monde.joueur
        if not j.get("parti") and (j["salle"], *j["position"]) in champ:
            vus["joueur"] = (j["salle"], list(j["position"]))
        return vus, set(champ)
    if eclairage(monde, salle)["niveau"] == 0:
        return vus, set()
    for id, o in monde.objets.items():
        if id not in vus and _pertinent(monde, acteur, o) and monde.present_physique(id, salle=salle):
            vus[id] = (salle, None)
    if not monde.joueur.get("parti") and monde.joueur["salle"] == salle:
        vus["joueur"] = (salle, None)
    return vus, {salle}


def _vu_dans_le_champ(monde, memo, acteur, id, o, pose, champ, salles_du_champ, salles_vues):
    """Où l'acteur voit l'objet ``id`` (salle, case), ou None : ``visible``, sans le cas des surfaces,
    qui ne sont pas pertinentes ; la première place dans le champ, et l'objet accroché au mur n'est vu
    que si ce mur l'est ; porté par un autre, s'il se remarque."""
    from .presence import parti
    if parti(monde, id) or not _remarquable(acteur, o) or pose is not None and pose not in salles_du_champ:
        return None
    premiere, vu = None, False
    for s in salles_vues if pose is None else (pose,):
        p = _position_vue(monde, memo, id, s)
        if p is None or (s, p[0], p[1]) not in champ:
            continue
        if premiere is None:
            premiere = (s, list(p))
        ancrage = o.get("ancrage_carte")
        if ancrage and tuple(ancrage) not in _murs(monde, champ, acteur, memo).get(s, set()):
            continue
        vu = True
        break
    return premiere if vu and not cache_par_porteur(monde, o, acteur) else None


def _percus_depuis(monde, acteur, memo, dernier):
    """La perception de l'acteur dans cet état (``_percus``), tirée de celle d'un état précédent
    (``dernier`` : l'empreinte de cet état, ce qu'il y percevait, son champ) quand seuls ont changé des
    objets qui ne bornent pas la vue (ni porte ni objet opaque), pas lui-même, et que son champ est le
    même : seuls les objets changés et ce qu'ils portent ou contiennent (la chaîne de leurs lieux), et
    les objets installés sur un support, sont revus ; le reste se voit de même. None sinon."""
    ancien, vus_avant, champ_avant, memo_avant = dernier
    etat = memo.get("etat")
    if etat is None:
        return None
    changes = _changes(memo, ancien, etat)
    if changes is None or acteur in changes:
        return None
    objets = monde.objets
    contenus, installes = _chaines(monde, memo)
    touches = changes | installes | {id for id, chaine in contenus if not changes.isdisjoint(chaine)}
    _heriter_signatures(memo, memo_avant, ancien, etat, touches)
    champ = _champ(monde, acteur, memo)
    if champ != champ_avant:
        return None
    poses = salles_posees(monde, memo)
    porte = (None, None)
    salles_du_champ = {c[0] for c in champ}
    salles_vues = [s for s in monde.data["salles"] if s in salles_du_champ]
    # Chaque objet revu : porté par lui, vu (où), ou ni l'un ni l'autre.
    revus = {}
    for id in touches:
        if id not in objets:
            continue
        o = objets[id]
        if poses[id] in (None, acteur) and porte_par(monde, id, acteur) and _pertinent(monde, acteur, o):
            revus[id] = porte
        else:
            revus[id] = _vu_dans_le_champ(monde, memo, acteur, id, o, poses[id], champ, salles_du_champ, salles_vues)
    j = monde.joueur
    joueur = (j["salle"], list(j["position"])) if not j.get("parti") and (j["salle"], *j["position"]) in champ else None
    if all((vus_avant.get(id) == porte) == (vu == porte) and (vus_avant.get(id) is None) == (vu is None)
           for id, vu in revus.items()) and ("joueur" in vus_avant) == (joueur is not None):
        # Aucun ne change de rubrique : l'ordre d'un calcul complet est celui d'avant.
        vus = dict(vus_avant)
        vus.update((id, vu) for id, vu in revus.items() if vu is not None)
        if joueur is not None:
            vus["joueur"] = joueur
        return vus, set(champ)
    # Dans l'ordre d'un calcul complet : ce qu'il porte, puis ce qu'il voit, puis le joueur.
    vus = {}
    for id in objets:
        if (revus[id] if id in revus else vus_avant.get(id)) == porte:
            vus[id] = porte
    for id in objets:
        if id not in vus:
            vu = revus[id] if id in revus else vus_avant.get(id)
            if vu is not None:
                vus[id] = vu
    if joueur is not None:
        vus["joueur"] = joueur
    return vus, set(champ)


def _changes(memo, ancien, etat):
    """Les objets dont l'entrée diffère entre deux empreintes (``spatial.etat_vue``), et « joueur » si
    sa place ou son regard a changé ; None si les objets ne sont plus les mêmes ou si une porte ou un
    objet opaque a changé (ce qui borne la vue). Gardé dans le mémo de l'état, par état précédent."""
    cle = ("changes", id(ancien))
    garde = memo.get(cle)
    if garde is not None and garde[0] is ancien:
        return garde[1]
    changes = set()
    if len(ancien[3]) != len(etat[3]):
        changes = None
    else:
        type_, opaque = CLES_VUE.index("type"), CLES_VUE.index("bloque_vue")
        for avant, apres in zip(ancien[3], etat[3]):
            if avant != apres:
                if avant[0] != apres[0] or any(x[1][type_] == "porte" or x[1][opaque] for x in (avant, apres)):
                    changes = None
                    break
                changes.add(avant[0])
        if changes is not None and ancien[:3] != etat[:3]:
            changes.add("joueur")
    memo[cle] = (ancien, changes)
    return changes


def _heriter_signatures(memo, memo_avant, ancien, etat, touches):
    """Les signatures de la vue de chaque salle (``spatial.signature_salle`` : portes et contenants
    ouverts, objets opaques, sources allumées et leur place) sont celles de l'état précédent quand rien
    de ce qu'elles lisent n'a changé : aucun objet changé, ni rien de ce qu'il porte ou contient
    (``touches``), n'est allumé ni opaque, et aucun n'a changé d'ouverture. L'état partage alors les
    signatures de l'autre (``memo["signatures"]``), qu'ils complètent ensemble."""
    if memo_avant is memo:
        return
    ouverte, opaque = CLES_VUE.index("ouverte"), CLES_VUE.index("bloque_vue")
    avant = {x[0]: x for x in ancien[3]}
    for x in etat[3]:
        if x[0] in touches:
            y = avant[x[0]]
            if x[2] or y[2] or x[1][opaque] or y[1][opaque] or x[1][ouverte] != y[1][ouverte]:
                return
    partagees = memo_avant.get("signatures")
    if partagees is None:
        partagees = memo_avant["signatures"] = {}
    propres = memo.get("signatures")
    if propres is not None and propres is not partagees:
        partagees.update(propres)
    memo["signatures"] = partagees


def _chaines(monde, memo):
    """Pour l'état : chaque objet contenu ou porté (son lieu n'est pas une salle), avec la chaîne de
    ses lieux jusqu'à une salle ; et les objets installés sur un support, dont la place suit ce support
    (``spatial._salle_position``). Une fois par état."""
    if "chaines" not in memo:
        objets, contenus, installes = monde.objets, [], set()
        for id, o in objets.items():
            if "installation" in o:
                installes.add(id)
            lieu, chaine = o["lieu"], [id]
            while lieu not in chaine and (lieu in objets or lieu == "joueur"):
                chaine.append(lieu)
                if lieu == "joueur":
                    break
                lieu = objets[lieu]["lieu"]
            if len(chaine) > 1:
                contenus.append((id, frozenset(chaine[1:])))
        memo["chaines"] = contenus, frozenset(installes)
    return memo["chaines"]


def percoit(monde, acteur, sujet):
    return sujet in percus(monde, acteur)[0]


def _perception_commune(monde, id):
    """Lecture physique unique par témoin dans une perception immuable."""
    regards = getattr(monde, "_regards_communs", None)
    if regards is None:
        return percus(monde, id)
    if id not in regards:
        regards[id] = percus(monde, id)
    return regards[id]


def _observe(monde, champ, croyance):
    """Le lieu où l'on attendait le sujet est-il sous les yeux du PNJ ?

    Sans case connue (un lieu qu'on lui a dit), il faut voir au moins la moitié de la salle.
    """
    if croyance["salle"] is None:
        return False
    if not monde.data.get("mode_cases"):
        return croyance["salle"] in champ
    if croyance["case"] is None:
        from .geometrie import cases
        sol = cases(monde.data["salles"][croyance["salle"]])
        return 2 * sum((croyance["salle"], x, y) in champ for x, y in sol) >= len(sol)
    return (croyance["salle"], *croyance["case"]) in champ


def reviser(monde, id, sujet, attribut, valeur, source="vu", **lieu):
    """Ce qu'il constate remplace ce qu'on lui a dit ; une contradiction trahit le locuteur.

    Passé ``RECENT`` minutes, le monde a pu changer depuis la parole : elle n'est que périmée. Un
    objet qu'il voit dans les mains de quelqu'un a pu être déplacé depuis : ce n'est pas un démenti.
    """
    ancienne = lire(monde, id)["croyances"].get(sujet, {}).get(attribut)
    porte = attribut == "lieu" and (valeur == "joueur" or monde.objets.get(valeur or "", {}).get("type") == "personnage")
    if (ancienne and ancienne["source"].startswith("dit:") and ancienne["valeur"] != valeur and not porte
            and monde.data["minutes"] - ancienne["minute"] <= RECENT):
        from .voix import auteur_dit, retenir
        locuteur, inconnue = auteur_dit(ancienne["source"])
        if inconnue:
            # Une voix qu'il ne savait à qui prêter : il se méfie d'elle, sans savoir qui c'était.
            if locuteur in monde.objets or locuteur == "joueur":
                retenir(monde, id, locuteur)["mefiance"] = True
        else:
            memoriser(monde, id, {"type": "mensonge_decouvert", "locuteur": locuteur, "sujet": sujet})
    croire(monde, id, sujet, attribut, valeur, source, **lieu)


def prete(monde, id, objet, a):
    return any(s["type"] == "pret" and s.get("objet") == objet and s.get("a") == a for s in lire(monde, id)["memoire"])


def constater_possession(monde, id, sujet, source, *, salle=None, case=None, remis_par=None, autorise=False):
    """Preuve propre du lieu et des droits lors d'une vue ou d'une remise.

    L'état réel n'est consulté qu'ici, au constat, jamais par la fin de garde.
    La preuve est sauvegardée avec le lieu daté ;
    aucune entité ni nouveau moyen n'est ajouté au planificateur.
    """
    assert source in ("vu", "essai")
    o = monde.objets[sujet]
    porteur = _porteur(monde, o)
    details = {}
    if porteur is not None:
        proprietaire = _proprietaire(monde, o)
        permis = porteur == proprietaire or _permis(monde, porteur, sujet)
        # Le droit de porter (prêt ou garde confiée) ne décharge pas le
        # gardien. Il faut une restitution ou une livraison mandatée.
        p = {"porteur": porteur, "proprietaire": proprietaire,
             "permis": bool(permis), "remis_par": remis_par,
             "remise_autorisee": bool(remis_par is not None and (porteur == proprietaire or autorise))}
        ancienne = croyance(monde, id, sujet, "lieu") or {}
        precedent = ancienne.get("possession", {})
        if remis_par is None and all(precedent.get(k) == p[k] for k in ("porteur", "proprietaire")):
            p["remis_par"] = precedent.get("remis_par")
            p["remise_autorisee"] = precedent.get("remise_autorisee", False)
        details["possession"] = p
    reviser(monde, id, sujet, "lieu", o["lieu"], source, salle=salle, case=case, **details)
    if source == "vu":
        voir_ensemble(monde, id, sujet, "lieu", o["lieu"])


def _vu_porter(monde, id, sujet):
    """Le propriétaire qui voit son bien aux mains d'un autre, sans le lui avoir prêté, découvre un vol."""
    o = monde.objets[sujet]
    porteur = _porteur(monde, o)
    from .relations import oublier_portage, portage_connu
    if porteur in (None, id) or _proprietaire(monde, o) != id:
        oublier_portage(monde, id, sujet)
        return
    if (prete(monde, id, sujet, porteur)
            or _permis(monde, porteur, sujet) or portage_connu(monde, id, sujet, porteur)):
        return
    from .deliberation import VOL, relancer
    memoriser(monde, id, {"type": "vu_porter", "auteur": porteur, "objet": sujet})
    relancer(monde, id, "biens", VOL)
    reconsiderer(monde, id)


@contextmanager
def constats_geste(monde, id, *sujets):
    """Conséquences matérielles d'un geste propre, réussi ou non."""
    from .perception import fin_objet
    avant = {s: fin_objet(monde.objets[s]) for s in sujets if s in monde.objets}
    yield
    for sujet, fin in avant.items():
        if sujet in monde.objets and fin_objet(monde.objets[sujet]) != fin:
            constater_fin_objet(monde, id, sujet, "essai")


def constater_fin_objet(monde, id, sujet, source):
    """Appelé seulement pour un objet vu ou touché par son propre geste.

    La preuve datée reste dans les croyances, hors de la mémoire bornée. Une
    suppression du registre réel n'est jamais, à elle seule, une observation.
    Les lectures habituelles d'état et de disponibilité restent inchangées.
    """
    from .perception import fin_objet
    assert source in ("vu", "essai")
    cause = fin_objet(monde.objets[sujet])
    ancienne = lire(monde, id)["croyances"].get(sujet, {}).get("fin")
    if cause and (not ancienne or ancienne["valeur"] != cause):
        croire(monde, id, sujet, "fin", cause, source)
    elif not cause and ancienne:
        # Une réparation ou une réserve reconstituée peut démentir le constat.
        # Cela ne réactive pas les projets déjà terminés.
        del esprit(monde, id)["croyances"][sujet]["fin"]


def voir_ensemble(monde, id, sujet, attribut, valeur):
    """Un constat visuel public, avec les témoins visibles du même sujet.

    Appelé au point d'acquisition de la propriété visible : ni une croyance
    privée, ni un essai dans le noir ne constituent une observation commune.
    """
    from .social import observation_commune
    if id == "joueur":
        return  # Le joueur choisit lui-même ses paroles.
    vus = _perception_commune(monde, id)[0]
    if sujet not in vus:
        return
    temoins = [autre for autre in vus if autre in pnjs(monde)
               and sujet in _perception_commune(monde, autre)[0]]
    # Le champ géométrique du joueur n'atteste pas qu'il a acquis ce fait.
    # Ses paroles ont une audience enregistrée ; une rotation silencieuse
    # ne constitue pas une communication publique de son savoir aux PNJ.
    observation_commune(monde, id, {"type": "affirmation", "sujet": sujet,
                                   "attribut": attribut, "valeur": valeur}, temoins, vus=vus)


def constater(monde, id, sujet, source):
    """Croit l'état visible de l'objet tel qu'il est : vu, ou laissé ainsi de sa propre main.
    D'un personnage, joueur compris, se voit ce qui presse son corps : la faim, le froid, la
    fatigue (``corps``), sous les noms des besoins du corps."""
    from .deliberation import proteges
    protege = (sujet == "joueur" or monde.objets[sujet]["type"] in ("personnage", "depouille")) and sujet in proteges(monde, id)
    if sujet == "joueur" or monde.objets[sujet]["type"] == "personnage":
        from .corps import CORPS, visible
        besoins = monde.joueur.get("besoins", {}) if sujet == "joueur" else lire(monde, sujet)["besoins"]
        ancien = croyance(monde, id, sujet, "etat")
        if ancien and "parti" in ancien["valeur"]:
            reviser(monde, id, sujet, "etat", {**ancien["valeur"], "parti": False}, source)
        if besoins:
            croire(monde, id, sujet, "etat",
                   {**{nom: besoins.get(nom, 0) >= regle["urgence"] for nom, regle in CORPS.items()},
                    **visible(monde, sujet),
                    **({"parti": False} if ancien and "parti" in ancien["valeur"] else {})}, source)
            if source == "vu":
                voir_ensemble(monde, id, sujet, "etat", croyance(monde, id, sujet, "etat")["valeur"])
        if (source == "vu" and not visible(monde, sujet)["conscient"]
                and (not ancien or ancien["valeur"].get("conscient") is not False)
                and protege):
            from .deliberation import ATTEINTE, relancer
            relancer(monde, id, "devoir", ATTEINTE)
        return
    o = monde.objets[sujet]
    if source in ("vu", "essai"):
        constater_fin_objet(monde, id, sujet, source)
        if o["type"] in ("porte", "contenant") and (o.get("ouverte") or o.get("integrite") == 0):
            reviser(monde, id, sujet, "verrouillee", False, source)
    if "passage" in o:
        # La forme ne se devine pas de la catégorie ; pas de croyance neuve pour
        # les anciens objets non décrits (empreintes inchangées).
        croire(monde, id, sujet, "passage", copy.deepcopy(o["passage"]), source)
    if o["type"] == "depouille":
        from .deliberation import inquieter, relancer
        ancien = croyance(monde, id, sujet, "etat")
        croire(monde, id, sujet, "etat", {"mort": True}, source)
        if source == "vu":
            voir_ensemble(monde, id, sujet, "etat", {"mort": True})
        if source == "vu" and not (ancien and ancien["source"] == "vu" and ancien["valeur"].get("mort")):
            memoriser(monde, id, {"type": "mort_vue", "objet": sujet, "salle": o["lieu"]})
            from .corps import evenement
            evenement(monde, "mort_vue", sujet, temoin=id,
                      delai=monde.data["minutes"] - monde.data["defunts"][sujet]["minute"])
            inquieter(monde, id, "mort")
            if protege:
                relancer(monde, id, "devoir", 30)
            from .pnj import _chroniquer
            _chroniquer(monde, id, monde.objets[id]["nom"].split(",")[0] + " découvre " + o["nom"] + ".", "geste")
        return
    if "pieces" in o and _porteur(monde, o) == id:
        # Ce qu'une bourse contient se sait en la tenant, pas en la voyant.
        croire(monde, id, sujet, "pieces", o["pieces"], source)
    etats = ETATS_VISIBLES.get(o["type"])
    if etats:
        valeurs = {**o, "disponible": o.get("portions", o.get("charges", 0)) > 0, "faible": faible(o),
                   "charge": o.get("combustible", 0) > 0}
        etat = {k: bool(valeurs.get(k)) for k in etats}
        if o["type"] == "contenant" and o.get("ouverte"):
            visible = source == "vu" or (monde.visible(sujet) if id == "joueur" else sujet in percus(monde, id)[0])
            if visible:
                etat["vide"] = not any(x["lieu"] == sujet for x in monde.objets.values())
            else:
                # Toucher le battant dans le noir ne dément pas le contenu vu.
                ancien = croyance(monde, id, sujet, "etat")
                if ancien and "vide" in ancien["valeur"]:
                    etat["vide"] = ancien["valeur"]["vide"]
        croire(monde, id, sujet, "etat", etat, source)
        if source == "vu":
            voir_ensemble(monde, id, sujet, "etat", etat)


def _flamme_sous_les_yeux(monde, id, sujet, lieu):
    """La place où il croit la source est-elle sous son regard ? Un objet fixe ne bouge pas."""
    o = monde.objets[sujet]
    if o.get("mobile", True):
        return False  # Absente à son ancienne case, une source mobile a pu être déplacée.
    if lieu and lieu["valeur"] is not None:
        if lieu["valeur"] not in monde.data["salles"]:
            # Portée ou contenue, elle peut avoir quitté sa dernière case avec
            # son support. Ne pas y voir sa flamme ne constate pas son extinction.
            return False
        salle, case = lieu.get("salle"), lieu.get("case")
    elif not o.get("mobile") and o["lieu"] in monde.data["salles"]:
        salle, case = o["lieu"], o.get("position")
    else:
        return False
    if salle is None or salle not in monde.data["salles"]:
        return False
    if not monde.data.get("mode_cases"):
        return monde.objets[id]["lieu"] == salle
    return case is not None and dans_le_regard(monde, salle, case, id)


def constater_lumiere(monde, id):
    """Il sait quelle lumière il y a là où il se tient, même sans en voir la source (0 noir,
    1 pénombre, 2 éclairé, ``perception``). La lumière qu'on porte, lui ou un autre, n'y compte
    pas : elle suit son porteur (il sait ce qu'il porte, il voit ce que portent les autres).

    Une seule règle pour ce qu'il en retient : ``niveau`` est ce qu'il a sur sa case, lueur d'une
    salle voisine comprise (sa chance au crochetage, celle du jet) ; ``propre`` est ce que la
    salle tient de ses propres sources, et ``eclairee`` en dit autant (``propre`` > 0). La lueur
    d'une autre salle n'éclaire que les cases où elle entre : de loin, il juge la salle à sa
    propre lumière (``deliberation.lumiere_crue``), et ne la prend pas pour un lieu éclairé
    parce qu'il en a vu le seuil (ni abri, ni lumière à rejoindre)."""
    salle = monde.objets[id]["lieu"]
    if salle not in monde.data["salles"]:
        return
    niveau, propre = lumiere_ici(monde, id)
    croire(monde, id, salle, "etat", {"eclairee": propre > 0, "niveau": niveau, "propre": propre}, "vu")


def lumiere_ici(monde, id):
    """(niveau, propre) sur sa case, sans la lumière qu'on porte (``constater_lumiere``). ``propre``
    est ce que la salle a partout : ses propres sources, et la lueur diffuse qui la baigne tout
    entière (``perception.CarteLumiere.ambiance`` : jour, reflets d'une source voisine par une
    ouverture) ; pas la lumière directe d'une source d'une autre salle, qui n'atteint que les
    cases qu'elle voit (un seuil). Sans cases, la lueur d'une voisine baigne toute la salle.

    Dans un état figé (``spatial.etat_fige``), gardée pour l'état : elle n'en lit que ce que lit
    ``spatial.etat_vue`` (sa place, les sources, qui les porte)."""
    cache = getattr(monde, "_cache_vue", None)
    fige = None if cache is None else cache.get("fige")
    if fige is not None and ("lumiere_ici", id) in fige:
        assert not a_verifier() or fige["lumiere_ici", id] == _lumiere_ici(monde, id), \
            f"Lumière mémorisée périmée : {id}"
        return fige["lumiere_ici", id]
    resultat = _lumiere_ici(monde, id)
    if fige is not None:
        fige["lumiere_ici", id] = resultat
    return resultat


def _lumiere_ici(monde, id):
    salle = monde.objets[id]["lieu"]
    porte = lambda source: source in monde.objets and _porteur(monde, monde.objets[source]) is not None
    position = monde.objets[id].get("position") if monde.data.get("mode_cases") else None
    lumieres = [c for c in eclairage(monde, salle, position)["contributions"] if not porte(c["source"])]
    niveau = max((c["niveau"] for c in lumieres), default=0)
    if not _par_case(monde, salle):
        return niveau, niveau
    diffuse = max((c["niveau"] for c in carte_lumiere(monde, salle).ambiance(salle) if not porte(c["source"])),
                  default=0)
    return niveau, max(diffuse, max((c["niveau"] for c in lumieres if c["source"] is not None), default=0))


def constater_lumiere_devant(monde, id, objet):
    """Là où il accomplit un geste qui demande d'y voir, il constate la lumière de sa case et la
    retient de ce qu'il touche (croyance ``lumiere`` : sans ce qu'on porte, comme celle d'une
    salle). Sa salle aussi (``constater_lumiere``). De loin, sa chance devant cet objet se juge
    sur ce qu'il y a vu (``planification.Vue.lumiere_devant``), pas sur la case d'où il partait.

    Il retient aussi les sources qu'il croyait alors allumées et posées dans la salle
    (``allumees``) : une source allumée ou posée depuis près de l'objet compte de loin dans ce
    qu'il en croit (``deliberation.apport_cru``)."""
    from .deliberation import sources_posees_crues
    constater_lumiere(monde, id)
    croire(monde, id, objet, "lumiere", lumiere_ici(monde, id)[0], "vu",
           allumees=sorted(sources_posees_crues(monde, id, monde.objets[id]["lieu"])))


def reconsiderer(monde, id):
    """Un événement change la situation d'un PNJ qui délibère : un bruit qu'il interprète
    (``ouie``), quelqu'un qui entre dans son regard ou en sort, l'état visible d'une chose qu'il
    voit qui change sous ses yeux (une porte, un feu), une parole qui lui est adressée ou qui lui
    apprend quelque chose. Il choisit de nouveau son but à la fin de son geste en cours, ou aussitôt
    s'il ne fait qu'attendre (``pnj._avancer``). L'instant est dans son esprit : le même laps,
    découpé autrement, donne le même monde. Sans cases, tout vit à la minute, comme avant."""
    from .corps import conscient
    if not conscient(monde, id):
        return
    o = monde.objets.get(id)
    if not o or not o.get("profil") or not monde.data.get("mode_cases"):
        return
    from .temps import instant
    e, t = esprit(monde, id), instant(monde)
    e["eveil"] = t if e["eveil"] is None else min(e["eveil"], t)


def percevoir(monde, id):
    """Révise les croyances d'un PNJ d'après ce qu'il perçoit maintenant."""
    from .corps import conscient
    if not conscient(monde, id):
        return
    with etat_fige(monde):  # Percevoir ne révise que son esprit.
        regards = getattr(monde, "_regards_communs", None)
        if regards is None:
            # Même hors d'une passe collective, tous les constats de cette
            # perception portent sur la même photographie physique.
            monde._regards_communs = {}
        try:
            _percevoir(monde, id)
        finally:
            monde._regards_communs = regards


def _percevoir(monde, id):
    vus, champ = _perception_commune(monde, id)
    croyances = esprit(monde, id)["croyances"]
    # Une disparition du registre n'apprend rien à un observateur distant.
    # Conserver aussi une fin déjà constatée, même si ses restes sont retirés.
    constater_lumiere(monde, id)
    from .eau import percevoir as percevoir_eau
    percevoir_eau(monde, id)
    # Qui entre dans son regard ou en sort, et ce qui change sous ses yeux, change sa situation.
    # Sa première perception ne fait qu'établir ce qu'il voit.
    e = esprit(monde, id)
    en_vue = sorted(x for x in vus if x == "joueur" or monde.objets[x]["type"] == "personnage")
    premiere = e["en_vue"] is None
    change = not premiere and en_vue != e["en_vue"]
    e["en_vue"] = en_vue
    for sujet, (salle, case) in vus.items():
        if sujet == "joueur":
            croire(monde, id, "joueur", "lieu", salle, "vu", salle=salle, case=case)
            constater(monde, id, "joueur", "vu")
            continue
        o = monde.objets[sujet]
        if o["type"] != "porte":
            constater_possession(monde, id, sujet, "vu", salle=salle, case=case)
            _vu_porter(monde, id, sujet)
        avant = croyances.get(sujet, {}).get("etat") if o["type"] in ETATS_VISIBLES or o["type"] == "personnage" else None
        constater(monde, id, sujet, "vu")
        if avant is not None:
            apres = croyances[sujet]["etat"]["valeur"]
            # Les besoins visibles gardent leur cadence ; les nouveaux états du corps
            # interrompent aussi l'attente, comme une porte ou un feu.
            change |= (any(avant["valeur"].get(k) != apres.get(k) for k in ("blessure", "conscient"))
                       if o["type"] == "personnage" else avant["valeur"] != apres)
    for sujet, attributs in list(croyances.items()):
        etat = attributs.get("etat")
        if (sujet not in vus and sujet in monde.objets and "allume" in monde.objets[sujet]
                and etat and etat["valeur"].get("allume") and _flamme_sous_les_yeux(monde, id, sujet, attributs.get("lieu"))):
            # Une flamme se voit de loin, même dans le noir : là où il regarde, rien ne brille.
            # Ce qui reste à brûler ne se voit pas : un feu vu baisser s'est consumé ; un feu vu
            # vif a pu être éteint, il garde ce qu'il en croyait.
            valeur = etat["valeur"]
            reviser(monde, id, sujet, "etat", {**valeur, "allume": False, "faible": False,
                                               "charge": bool(valeur.get("charge")) and not valeur.get("faible")})
            change = True
    for sujet, attributs in croyances.items():
        lieu = attributs.get("lieu")
        if sujet != "joueur" and sujet not in monde.objets:
            continue
        if sujet in vus or not lieu or lieu["valeur"] is None or not _observe(monde, champ, lieu):
            continue
        contenant = monde.objets.get(lieu["valeur"])
        if contenant and contenant["type"] == "contenant" and not contenant.get("ouverte"):
            continue  # Un contenant fermé peut toujours le cacher.
        if lieu["valeur"] == "joueur" or contenant and contenant["type"] == "personnage":
            continue  # Porté par quelqu'un : son absence de la case ne prouve rien.
        if sujet in monde.objets and monde.objets[sujet]["type"] != "personnage" and not monde.objets[sujet].get("mobile"):
            continue  # Un objet fixe fait partie du lieu : ne pas le voir d'ici ne le déplace pas.
        reviser(monde, id, sujet, "lieu", None, salle=None, case=None)
        if sujet != "joueur" and monde.objets[sujet]["type"] != "personnage":
            change = True  # Ce qu'il attendait là n'y est plus.
            memoriser(monde, id, {"type": "absence", "objet": sujet, "salle": lieu["salle"]})
            from .vol import proprietaire
            if proprietaire(monde, monde.objets[sujet]) == id:
                from .deliberation import relancer
                relancer(monde, id, "biens", 30)
    # Ce qu'il voit changer par son propre geste (ses pas, se tourner, une porte qu'il ouvre), il s'y
    # attendait : son plan le prévoyait, il le poursuit (la fin du plan, un geste manqué et la minute
    # le font choisir de nouveau). Seul ce que font les autres, ou le monde, l'éveille.
    if change and not premiere and getattr(monde, "_agit", None) != id:
        reconsiderer(monde, id)


def percevoir_tous(monde):
    with vue_memorisee(monde), etat_fige(monde):  # Percevoir ne révise que des esprits.
        # Photographier les acquisitions de CETTE perception commune, pas les
        # croyances privées laissées par les perceptions précédentes. Cela
        # couvre toute propriété observée par la voie commune, sans catalogue
        # de types de faits, ni assimilation d'une conclusion à une observation.
        observations = {id: [] for id in pnjs(monde)}
        precedent = getattr(monde, "_observations_communes", None)
        regards_precedents = getattr(monde, "_regards_communs", None)
        perceptions = {id: percus(monde, id) for id in observations}
        regards = {id: p[0] for id, p in perceptions.items()}
        supports = {id: set(vus) | {case[0] if isinstance(case, tuple) else case for case in champ}
                    for id, (vus, champ) in perceptions.items()}
        monde._observations_communes = observations
        monde._regards_communs = perceptions
        try:
            for id in observations:
                percevoir(monde, id)
        finally:
            monde._observations_communes = precedent
            monde._regards_communs = regards_precedents
        from .social import faits_dits, observation_commune
        acquis = {id: dict(f for n in contenus for f in faits_dits(n))
                  for id, contenus in observations.items()}
        for id, contenus in observations.items():
            vus = regards[id]
            for noyau in contenus:
                faits = faits_dits(noyau)
                temoins = [autre for autre in observations if autre != id and autre in vus
                           and (noyau["sujet"] in supports[id] & supports[autre]
                                or noyau["sujet"] in monde.data["salles"])
                           and all(cle in acquis[autre] and acquis[autre][cle] == valeur
                                   for cle, valeur in faits)]
                observation_commune(monde, id, noyau, temoins, vus=vus)
        from .perception import fin_objet
        croyances_joueur = lire(monde, "joueur")["croyances"]
        for sujet, o in monde.objets.items():
            ancien = croyances_joueur.get(sujet, {}).get("etat")
            if ancien and "parti" in ancien["valeur"] and monde.visible(sujet):
                reviser(monde, "joueur", sujet, "etat", {**ancien["valeur"], "parti": False})
            if _porteur(monde, o) is not None and monde.visible(sujet):
                constater_possession(monde, "joueur", sujet, "vu")
            fin_connue = "fin" in croyances_joueur.get(sujet, {})
            if (fin_objet(o) or fin_connue) and monde.visible(sujet):
                constater_fin_objet(monde, "joueur", sujet, "vu")
