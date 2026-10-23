"""Rendu local déterministe ; les conversations libres sont gérées séparément."""
from textwrap import fill
from .monde import ErreurMonde
from .perception import eclairage
from .carte import carte
from .francais import accorder, designer, enumerer, pluriel, relation_physique


def decrire(monde, id, detail=False, article="defini", technique=True):
    if not monde.visible(id):
        raise ErreurMonde("Cet objet n'est pas visible.")
    o = monde.objets[id]
    if detail and eclairage(monde)["niveau"] < 2:
        return designer(o, debut=True) + " : la pénombre permet de distinguer sa présence, pas ses détails."
    if o["type"] == "partie_corps" and eclairage(monde)["niveau"] >= 2 and o.get("description_visuelle"):
        return o["description_visuelle"]
    matiere = o["materiau"]
    matiere_deja_nommee = matiere and any(p + matiere in o["nom"] for p in ("de ", "d'", "en "))
    nom = designer(o, article, debut=True) + (f' en {matiere}' if matiere and not matiere_deja_nommee else "")
    morceaux, complements = [], []
    if o.get("physique"):
        from .matiere import decrire as decrire_physique
        complements.append(decrire_physique(o))
    if "passage" in o:
        from .matiere import decrire_passage
        complements.append(decrire_passage(o))
    if o.get("contenu"):
        from .matiere import decrire_contenu
        complements.append(decrire_contenu(o))
    if o.get("ressource") and not o.get("physique"):
        if "longueur_cm" in o:
            complements.append(f"Longueur disponible : {o['longueur_cm'] / 100:g} m")
        if "diametre_cm" in o:
            complements.append(f"Diamètre : {o['diametre_cm']:g} cm")
    if o.get("assemblage"):
        complements.append(f"Longueur : {o['longueur_cm'] / 100:g} m ; largeur : {o['largeur_cm']:g} cm ; {o['barreaux']} barreaux")
        if o.get("installation"):
            complements.append("Elle est appuyée contre " + designer(monde.objets[o['installation']['support']]))
    if o.get("appui_vertical"):
        complements.append(f"Un palier surplombe le pied du mur de {o['appui_vertical']['hauteur_cm'] / 100:g} m")
    if o.get("fixee_sur"):
        complements.append("Elle est fixée sur " + o["fixee_sur"])
    if o.get("relation_support") and o["lieu"] in monde.objets:
        morceaux.append(relation_physique(o, monde.objets[o["lieu"]], o["relation_support"]))
    if o["integrite"] == 0:
        morceaux.append(accorder(o, "brisé"))
    elif o["integrite"] < o["maximum"]:
        morceaux.append(accorder(o, "abîmé") + (f' ({o["integrite"]}/{o["maximum"]})' if technique else ""))
    if o["type"] in ("porte", "contenant"):
        morceaux.append(accorder(o, "ouvert" if o["ouverte"] else "fermé"))
        if o["verrouillee"]:
            morceaux.append(accorder(o, "verrouillé"))
    if o.get("detachee"):
        complements.append("Le battant est dégondé, au sol ; le passage est libre")
    if o.get("bloque_par"):
        morceaux.append(accorder(o, "calé") + " par " + designer(monde.objets[o["bloque_par"]]))
    if o["type"] == "fixation":
        morceaux.append("en place et amovible" if o["attache"] else accorder(o, "retiré"))
    if o.get("bloquee"):
        morceaux.append(accorder(o, "bloqué"))
    if o.get("en_vente"):
        morceaux.append(f'en vente : {prix(monde, o)} pièces')
    if o["type"] == "personnage":
        from .corps import blessure, conscient
        if not conscient(monde, o["id"]):
            # Sans connaissance, il ne montre aucun signe (comme une dépouille, ``signes``).
            morceaux.append("à terre, sans connaissance")
        else:
            # La reddition est une posture visible du corps (``corps.visible``), pas un signe ;
            # une phrase à part, car elle ne s'accorde pas derrière « est ».
            if o.get("corps", {}).get("reddition"):
                complements.append(designer(o, debut=True) + " a cessé de résister")
            if blessure(monde, o["id"]):
                morceaux.append(accorder(o, "grièvement blessé" if blessure(monde, o["id"]) == 2 else "blessé"))
    if o["type"] == "depouille":
        from .corps import blessure
        if blessure(monde, id):
            morceaux.append("grièvement blessé" if blessure(monde, id) == 2 else "blessé")
    if o.get("cale_de"):
        complements.append("Cet objet maintient la porte ouverte")
    if o.get("charges") == 0:
        complements.append("Il n'en reste plus")
    elif "charges" in o and technique:
        complements.append(f'Il reste {o["charges"]} utilisation' + ("s" if o["charges"] > 1 else ""))
    if "allume" in o:
        morceaux.append(accorder(o, "allumé" if o["allume"] else "éteint"))
        if o.get("combustible") == 0:
            complements.append(designer(o, debut=True) + " n'a plus de combustible")
        elif technique:
            complements.append(f'Combustible restant : {o["combustible"]} min')
    if o.get("sonorite"):
        complements.append(designer(o, debut=True) + " peut produire un son audible")
    if o.get("constats_capacites"):
        from .capacites_objet import (absence as absence_capacite, aptitude_coupe,
                                     empreinte as empreinte_capacite)
        for observation in o["constats_capacites"]:
            positive = observation["issue"] == "etablie"
            phrase = (aptitude_coupe(o, observation) if positive else
                      absence_capacite(o, observation["capacite"], observation))
            moyen = monde.objets.get(observation["moyen_id"])
            if (observation["empreinte"] != empreinte_capacite(o, usure=not positive)
                    or positive and o["integrite"] == 0
                    or observation["moyen_id"] and
                    (moyen is None or observation["empreinte_moyen"] !=
                     empreinte_capacite(moyen, usure=not positive)
                     or positive and moyen["integrite"] == 0)):
                phrase = "Constat dans un état antérieur : « " + phrase + " »"
            complements.append(phrase)
    from .spatial import proche
    a_portee = not monde.data.get("mode_cases") or proche(monde, id)
    if not a_portee:
        # De loin, ni la main ni l'œil n'atteignent le détail d'un objet : le moteur n'en livre aucun
        # (aspect fin, inscription) et n'en laisse établir aucun (``faits_locaux.supports``). Un
        # personnage, lui, peut se décrire de souvenir (``enrichissement``, « souvenir d'une rencontre »).
        complements.append(designer(o, debut=True) + (" sont" if pluriel(o) else " est") + " trop loin pour être "
                           + accorder(o, "manipulé") + " d'ici" + ("" if o["type"] == "personnage" else
                                                                   " ; de là, " + ("leurs" if pluriel(o) else "ses")
                                                                   + " détails t'échappent"))
    texte = nom + ((" sont " if pluriel(o) else " est ") + enumerer(morceaux) if morceaux else "") + "."
    if complements:
        texte += " " + ". ".join(complements) + "."
    if eclairage(monde)["niveau"] >= 2 and a_portee:
        if o.get("portrait"):
            texte += " " + o["portrait"]
        if o["type"] in ("personnage", "depouille"):
            if o["type"] == "depouille":
                texte += " " + o["designation_visuelle"].capitalize() + "."
            for facette, valeur in o.get("facettes", {}).items():
                if "texte" in valeur and facette not in ("voix", "temperament"):
                    texte += " " + valeur["texte"]
            for enfant in monde.enfants(id):
                if enfant["type"] == "partie_corps" and monde.visible(enfant["id"]):
                    texte += " " + enfant.get("description_visuelle", "")
        if o.get("description_visuelle"):
            texte += " " + o["description_visuelle"]
    if detail:
        if o.get("motif"):
            texte += " " + o["motif"]
            if o["lieu"] in monde.objets and monde.objets[o["lieu"]]["integrite"] == 0:
                texte += " Le support est brisé ; l'inscription est illisible."
            elif o.get("inscription"):
                texte += f' Inscription : « {o["inscription"]} ».'
                if id in monde.data["lus"] and o.get("sens"):
                    texte += " " + o["sens"]
        enfants = [designer(e) for e in monde.enfants(id) if monde.visible(e["id"])]
        if enfants:
            texte += " Eléments accessibles : " + enumerer(enfants) + "."
        if o["type"] == "porte":
            fixes = sum(e.get("attache", False) for e in monde.enfants(id))
            texte += f' Masse : {o["masse"]} kg. Fixations en place : {fixes}.'
        if o.get("usages"):
            from .matiere import SUBSTANCES
            from .perception import FOYER, substance
            # Un combustible recharge ce qui brûle sa substance (``perception.recharge``).
            matiere = substance(o)
            noms = {"levier_fin": "petit levier fragile", "couper": "couper",
                    "levier": "levier robuste", "percussion": "frapper",
                    "cale": "caler", "crochetage": "crocheter", "empreinte": "prendre une empreinte",
                    "allumage": "allumer une source de lumière", "couper_bois": "découper du bois",
                    "combustible": "recharger un feu" if matiere in (None, FOYER)
                    else "recharger ce qui brûle " + SUBSTANCES[matiere]["article"]}
            texte += " Usages usuels : " + ", ".join(noms[u] for u in o["usages"]) + "."
    from .noms import texte as texte_public
    return texte_public(monde, texte)


def prix(monde, objet):
    # Rabais fixe : pas de relance gratuite jusqu'à obtenir une bonne négociation.
    return max(1, objet["prix"] - max(0, (monde.joueur["stats"]["CHA"] - 10) // 2))


def regarder(monde):
    from .corps import conscient
    if not conscient(monde):
        return "Ta partie est terminée." if monde.data.get("fin") else "Tu es sans connaissance."
    salle = monde.joueur["salle"]
    titre = "\n== " + monde.data["salles"][salle]["nom"].upper() + " =="
    lignes = []
    lumiere = eclairage(monde)
    if lumiere["niveau"] == 0:
        # En cases, une zone éclairée au loin reste visible depuis l'obscurité.
        lignes.append("Autour de toi, il fait noir ; plus loin, une zone éclairée se détache."
                      if monde.presents() else "Il fait entièrement noir. Tu ne distingues rien autour de toi.")
    else:
        if lumiere["niveau"] == 1:
            lignes.append("Dans la pénombre, tu distingues les objets, mais leurs détails t'échappent.")
        causes = []
        for c in lumiere["contributions"]:
            if c["direction"]:
                phrase = "Une lueur te parvient de l'" + c["direction"] + "." if c["direction"] in ("est", "ouest") else "Une lueur te parvient du " + c["direction"] + "."
            elif c["source"] == "jour":
                phrase = "Tu es à la lumière du jour." if monde.data["salles"][salle].get("exterieur") else "La lumière du jour éclaire la pièce."
            else:
                source = monde.objets[c["source"]]
                phrase = designer(source, "possessif" if source["lieu"] == "joueur" else "defini", debut=True) + " éclaire la pièce."
            if phrase not in causes:
                causes.append(phrase)
        lignes.extend(causes)
        surfaces = [o for o in monde.presents() if o["type"] == "surface"
                    and (o["lieu"] == salle or o.get("appui_vertical"))]
        if lumiere["niveau"] == 2:
            for materiau in dict.fromkeys(o["materiau"] for o in surfaces):
                groupe = [o for o in surfaces if o["materiau"] == materiau]
                noms = enumerer(designer(o) for o in groupe)
                verbe = " sont " if len(groupe) > 1 or pluriel(groupe[0]) else " est "
                lignes.append(noms[:1].upper() + noms[1:] + verbe + "en " + materiau + ".")
            if monde.data["salles"][salle]["fenetres"] == 0 and not monde.data["salles"][salle].get("exterieur"):
                lignes.append("Aucune fenêtre.")
            from .espace import description as description_espace
            lignes.extend(description_espace(monde))
            for o in surfaces:
                if o.get("appui_vertical"):
                    if salle == o["appui_vertical"]["bas"]:
                        lignes.append(f"Un palier borde le sommet du mur, à {o['appui_vertical']['hauteur_cm'] / 100:g} m du sol.")
    from .eau import decrire as decrire_eau
    eau = decrire_eau(monde, salle)
    if eau:
        # L'eau se sent, même dans le noir.
        lignes.append(("L'eau a noyé la salle : elle t'arrive " if eau["etat"] == "noyee" else "L'eau couvre le sol : elle t'arrive ")
                      + eau["hauteur"] + f" ({eau['profondeur_cm']} cm).")
    for o in monde.presents():
        if o["lieu"] == "joueur" or o["type"] == "surface":
            continue
        # Les composants apparaissent à l'examen de leur parent ; pas de doublons.
        if o["lieu"] in monde.objets and o["type"] != "porte" and not o.get("scene_detail"):
            continue
        au_dela = (monde.data.get("mode_cases") and o["lieu"] in monde.data["salles"]
                   and o["lieu"] != salle and o["type"] != "porte" and not o.get("installation"))
        if lumiere["niveau"] <= 1:
            lignes.append(("Au-delà du passage, tu distingues " if au_dela else "Tu distingues ")
                          + designer(o, "indefini") + ".")
        else:
            description = decrire(monde, o["id"], article="defini" if o["type"] == "porte" else "indefini", technique=False)
            if o["type"] != "personnage" and " est " not in description:
                description = "Tu vois " + description[:1].lower() + description[1:]
            if au_dela:
                description = "Au-delà du passage : " + description[:1].lower() + description[1:]
            lignes.append(description)
    sorties = []
    for direction, sortie in monde.data["salles"][salle]["sorties"].items():
        if monde.data.get("mode_cases"):
            from .spatial import sortie_connue
            if not sortie_connue(monde, salle, direction):
                continue
        nom = monde.data["salles"][sortie["vers"]]["nom"] if sortie["vers"] in monde.data["visitees"] else "inexploré"
        if sortie.get("escalier"):
            depart = monde.data["salles"][salle]
            arrivee = monde.data["salles"][sortie["vers"]]
            monte = arrivee.get("altitude_cm", arrivee.get("niveau", 0) * 240) > depart.get("altitude_cm", depart.get("niveau", 0) * 240)
            nom = ("escalier montant, " if monte else "escalier descendant, ") + nom
        from .eau import voisines
        if sortie["vers"] in voisines(monde, salle) and decrire_eau(monde, sortie["vers"]):
            nom += (", eau trop haute pour passer" if decrire_eau(monde, sortie["vers"])["etat"] == "noyee"
                    else ", sous l'eau")
        sorties.append(f"{direction} ({nom})")
    for o in monde.presents():
        if o.get("installation") and o["integrite"] == o["maximum"]:
            support = monde.objets[o["installation"]["support"]]
            a = support["appui_vertical"]
            if support["integrite"] and a.get("sol_stable") and a.get("sommet_stable"):
                sorties.append(("monter" if salle == a["bas"] else "descendre") + " par " + designer(o))
    if monde.data.get("mode_cases"):
        # Il ne connaît que les sorties qu'il a vues ou foulées : n'en connaître aucune ne dit pas qu'il
        # n'y en a pas, et la phrase ne doit pas trahir qu'il en reste d'autres.
        fin = "\n\nSorties que tu connais : " + (", ".join(sorties) or "aucune pour l'instant") + "."
    else:
        fin = "\n\nSorties : " + (", ".join(sorties) or "aucun passage directement praticable") + "."
    from .signes import publics, impressions
    # Deux signes peuvent laisser la même impression : elle ne se dit qu'une fois.
    fin += "\n" + "\n".join(dict.fromkeys(s["texte"] for s in publics(monde) + impressions(monde)))
    return titre + "\n\n" + fill(" ".join(lignes), width=88) + fin


def fiche(monde):
    from .corps import etat as etat_corps
    from .defense import dangers
    from .voix import nom_pour_joueur as nom_percu
    j = monde.joueur
    menaces = dangers(monde, "joueur")
    profil = []
    if j.get("espece"):
        profil.append(" ".join(filter(None, (j["espece"], j.get("stade_vie")))).capitalize())
    if "taille_cm" in j:
        profil.append(f"Taille : {j['taille_cm']//100} m {j['taille_cm']%100:02d}")
    if "age_ans" in j:
        profil.append(f"Âge : {j['age_ans']} ans")
    for champ, titre in (("couleur_yeux", "Yeux"), ("couleur_cheveux", "Cheveux"), ("corpulence", "Corpulence")):
        if champ in j:
            profil.append(titre + " : " + j[champ])
    stats = "  ".join(f"{k} {v} ({(v - 10) // 2:+d})" for k, v in j["stats"].items())
    sac = [decrire(monde, o["id"], article="indefini") if monde.visible(o["id"]) else designer(o, "indefini", debut=True) + " (sur toi, non visible)"
           for o in monde.objets.values() if o["lieu"] == "joueur"]
    return (f'\nPERSONNAGE — {j["nom"]}\nPV {j["pv"]}/{j["pv_max"]} | {j["or"]} pièces | '
            f'{monde.charge():.1f}/{j["capacite"]} kg | {monde.data["minutes"]} min\n'
            + stats + ("\n" + " | ".join(profil) if profil else "")
            + "\n" + " | ".join(f"{nom.capitalize()} : {niveau}" for nom, niveau in etat_corps(monde).items())
            + ("\nDanger perçu : " + ", ".join(nom_percu(monde, x) for x in menaces) + "." if menaces else "")
            + "\nBesace :\n  " + "\n  ".join(sac) + "\n\n" + decrire_accords(monde) + decrire_comptes(monde))


def decrire_comptes(monde):
    """Ce qu'on doit au joueur, ce qu'il a prêté et ce qu'on lui a prêté (``biens.comptes_joueur``)."""
    from .biens import comptes_joueur
    lignes = comptes_joueur(monde)
    return ("\nComptes :\n  " + "\n  ".join(lignes)) if lignes else ""


def decrire_accords(monde):
    from .dialogues import contrats_publics
    accords = contrats_publics(monde)
    if not accords:
        return "Accords : aucune récompense proposée pour le moment."
    statuts = {"propose": "offre à accepter", "accepte": "accord accepté", "refuse": "offre refusée", "paye": "récompense payée"}
    return "Accords :\n" + "\n".join(
        f"  {monde.data['missions'][id]['nom']} : {a['montant']} pièces, {statuts[a['statut']]}. {a['condition']}"
        for id, a in accords.items())


def decrire_perception(monde):
    piece = monde.data["salles"][monde.joueur["salle"]]
    lumiere = eclairage(monde)
    lignes = ["Tu es à l'extérieur." if piece.get("exterieur") else "Cette pièce n'a pas de fenêtre." if piece["fenetres"] == 0 else
              f'Cette pièce possède {piece["fenetres"]} fenêtre(s).']
    lignes.append([
        "Il fait noir là où tu te tiens : tu ne peux rien lire, mais une zone éclairée reste visible plus loin."
        if monde.presents() else
        "Il fait entièrement noir : aucune lumière ne te parvient. Tu ne peux ni voir les objets ni lire les inscriptions.",
        "Il ne fait pas entièrement noir : une pénombre permet de distinguer les objets, mais pas de lire les inscriptions.",
        "Il ne fait pas noir : la lumière est suffisante pour voir les objets et leurs détails.",
    ][lumiere["niveau"]])
    causes = set()
    for contribution in lumiere["contributions"]:
        if contribution["direction"]:
            causes.add("Une lueur passe par l'ouverture vers " + contribution["direction"] + ".")
        elif contribution["source"] == "jour":
            causes.add("La pièce reçoit de la lumière naturelle.")
        else:
            o = monde.objets[contribution["source"]]
            causes.add(designer(o, debut=True) + (", que tu portes, éclaire la pièce." if o["lieu"] == "joueur" else " éclaire la pièce."))
    lignes.extend(sorted(causes))
    if lumiere["niveau"] > 0:
        for o in monde.presents():
            if "allume" in o and not o["allume"]:
                lignes.append(designer(o, debut=True) + " est " + accorder(o, "éteint") + " et ne produit aucune lumière.")
    return " ".join(lignes)


def toucher(monde, id):
    if not monde.accessible(id):
        raise ErreurMonde("Tu ne sais pas où trouver cet objet au toucher.")
    o = monde.objets[id]
    if o["type"] == "contenant" and o["ouverte"]:
        contenu = [e for e in monde.enfants(id) if monde.present_physique(e["id"])]
        if not contenu:
            return designer(o, debut=True) + " est vide : tes mains n'y trouvent rien."
        return ("En fouillant " + designer(o) + ", tu reconnais au toucher "
                + enumerer(designer(e, "indefini") for e in contenu) + ".")
    if o.get("description_tactile"):
        return designer(o, debut=True) + " : " + o["description_tactile"]
    return designer(o, debut=True) + f' : vous en sentez le matériau ({o["materiau"]}).'


def decrire_contexte(monde):
    contexte = monde.contexte_scenario()
    lignes = [contexte["debut"], "Tu te trouves dans : " + contexte["position"] + "."]
    if contexte["dernier_deplacement"]:
        lignes.append("Dernier déplacement enregistré : " + " ".join(contexte["dernier_deplacement"]))
    return "\n".join(lignes)


# Le rendu porte des noms publics ; l'état mécanique garde ses identifiants.
def _rendu_public(f):
    def rendre(monde, *args, **kwargs):
        from .noms import texte
        return texte(monde, f(monde, *args, **kwargs))
    return rendre

for _fonction in ("regarder", "decrire_contexte", "toucher"):
    globals()[_fonction] = _rendu_public(globals()[_fonction])
