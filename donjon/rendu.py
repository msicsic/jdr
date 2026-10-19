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
    elif o.get("ressource"):
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
        if o.get("humeur"):
            morceaux.append(o["humeur"])
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
        complements.append(designer(o, debut=True) + " est trop loin pour être "
                           + accorder(o, "manipulé") + " d'ici")
    texte = nom + ((" sont " if pluriel(o) else " est ") + enumerer(morceaux) if morceaux else "") + "."
    if complements:
        texte += " " + ". ".join(complements) + "."
    if eclairage(monde)["niveau"] >= 2 and a_portee:
        if o.get("portrait"):
            texte += " " + o["portrait"]
        if o["type"] == "personnage":
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
            noms = {"levier_fin": "petit levier fragile", "couper": "couper",
                    "levier": "levier robuste", "percussion": "frapper",
                    "cale": "caler", "crochetage": "crocheter", "empreinte": "prendre une empreinte",
                    "allumage": "allumer une source de lumière", "couper_bois": "découper du bois",
                    "combustible": "recharger un feu"}
            texte += " Usages usuels : " + ", ".join(noms[u] for u in o["usages"]) + "."
    return texte


def prix(monde, objet):
    # Rabais fixe : pas de relance gratuite jusqu'à obtenir une bonne négociation.
    return max(1, objet["prix"] - max(0, (monde.joueur["stats"]["CHA"] - 10) // 2))


def regarder(monde):
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
            from .spatial import sortie_visible
            if not sortie_visible(monde, salle, direction):
                continue
        nom = monde.data["salles"][sortie["vers"]]["nom"] if sortie["vers"] in monde.data["visitees"] else "inexploré"
        if sortie.get("escalier"):
            depart = monde.data["salles"][salle]
            arrivee = monde.data["salles"][sortie["vers"]]
            monte = arrivee.get("altitude_cm", arrivee.get("niveau", 0) * 240) > depart.get("altitude_cm", depart.get("niveau", 0) * 240)
            nom = ("escalier montant, " if monte else "escalier descendant, ") + nom
        sorties.append(f"{direction} ({nom})")
    for o in monde.presents():
        if o.get("installation") and o["integrite"] == o["maximum"]:
            support = monde.objets[o["installation"]["support"]]
            a = support["appui_vertical"]
            if support["integrite"] and a.get("sol_stable") and a.get("sommet_stable"):
                sorties.append(("monter" if salle == a["bas"] else "descendre") + " par " + designer(o))
    return titre + "\n\n" + fill(" ".join(lignes), width=88) + "\n\nSorties : " + (", ".join(sorties) or "aucun passage directement praticable") + "."


def fiche(monde):
    from .corps import etat as etat_corps
    j = monde.joueur
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
    sac = [decrire(monde, o["id"], article="indefini") if monde.visible(o["id"]) else designer(o, "indefini", debut=True) + " (dans votre besace, non visible)"
           for o in monde.objets.values() if o["lieu"] == "joueur"]
    return (f'\nPERSONNAGE — {j["nom"]}\nPV {j["pv"]}/{j["pv_max"]} | {j["or"]} pièces | '
            f'{monde.charge():.1f}/{j["capacite"]} kg | {monde.data["minutes"]} min\n'
            + stats + ("\n" + " | ".join(profil) if profil else "")
            + "\n" + " | ".join(f"{nom.capitalize()} : {niveau}" for nom, niveau in etat_corps(monde).items())
            + "\nBesace :\n  " + "\n  ".join(sac) + "\n\n" + decrire_accords(monde))


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
        "Il fait entièrement noir : aucune lumière ne vous parvient. Vous ne pouvez pas voir les objets ni lire les inscriptions.",
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
            causes.add(designer(o, debut=True) + (", que vous portez, éclaire la pièce." if o["lieu"] == "joueur" else " éclaire la pièce."))
    lignes.extend(sorted(causes))
    if lumiere["niveau"] > 0:
        for o in monde.presents():
            if "allume" in o and not o["allume"]:
                lignes.append(designer(o, debut=True) + " est " + accorder(o, "éteint") + " et ne produit aucune lumière.")
    return " ".join(lignes)


def toucher(monde, id):
    if not monde.accessible(id):
        raise ErreurMonde("Vous ne savez pas où trouver cet objet au toucher.")
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
