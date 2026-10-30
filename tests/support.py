"""Doubles de test communs aux parcours qui simulent déjà les réponses du MJ."""

from unittest.mock import patch
from functools import wraps

from donjon.mj import MJOpenAI


def canal_constats_anterieur_337(test):
    """Prémisse des oracles antérieurs : les constats de 55 seuls se confient.

    Les anciens oracles déclarent leurs constats de 55 récemment appris,
    sans confidence de possession/fin concurrente. Une vraie prise ou
    consommation peut désormais ouvrir cette conversation (337) et un
    savoir initial reste silencieux (360) : ces deux garanties sont éprouvées
    sans ce double dans test_garde_ouidire et test_nouvelles_initiales.
    Accusations, enquêtes, constats de 55 et réception restent réels.
    """
    @wraps(test)
    def avec_canal(*args, **kwargs):
        from donjon import social
        constats = social._constats
        def precedents(monde, id):
            return (n for n in constats(monde, id) if n[1]["attribut"] not in ("lieu", "fin"))
        with patch.object(social, "_constats", precedents), patch.object(social, "_initial", return_value=False):
            return test(*args, **kwargs)
    return avec_canal


def question_sans_execution(texte):
    """Oracle U-P : réponse inchangée, suivie du constat moteur sans action.

    Cette valeur attendue n'appelle pas le rendu de production. Les tests
    continuent de comparer le texte entier et tous leurs oracles du monde.
    """
    return texte + "\nQuestion au MJ : aucune action exécutée."


def sans_indices_soupcon_passifs(monde):
    """Projection des oracles antérieurs au 267, sans changer leurs hashes.

    Le monde entier reste validé et rechargé par les appelants. Seul le
    registre perceptif additionnel peut sortir de l'oracle ancien ; toute
    épreuve de soupçon, même levée ou oubliée en mémoire courte, l'interdit.
    """
    import copy
    monde.verifier()
    causes = {"soupcon_deduit", "soupcon_leve"}
    assert not any(c.get("cause") in causes for c in monde.data.get("chronique", [])), "Soupçon dans la chronique historique"
    for e in monde.data["esprits"].values():
        assert not e.get("indices_soupcon", {}).get("soupcons"), "Soupçon actif dans la capture historique"
        assert not any(":soupcon:" in p for p in e["preuves_relations"]), "Épreuve de soupçon dans la capture historique"
        assert not any(s["type"] in causes for s in e["memoire"]), "Souvenir de soupçon dans la capture historique"
        assert not any(m["type"] in causes for r in e["relations"].values() for m in r["motifs"]), "Motif de soupçon dans la capture historique"
    historique = copy.deepcopy(monde.data)
    for e in historique["esprits"].values():
        e.pop("indices_soupcon", None)
    return historique


def simuler_couverture(test):
    """Les tests des autres contrats fournissent un plan tenu pour fidèle.

    Les refus et corrections réels de cette revue sont exercés dans
    test_improvisation, où les appels bruts sont simulés séparément.
    """
    controle = patch.object(MJOpenAI, "_auditer_action")
    controle.start()
    test.addCleanup(controle.stop)


def sans_budget(monde):
    """Lieu sans budget d'invention : ces tests portent sur les capacités elles-mêmes."""
    for salle in monde.data["salles"].values():
        salle.pop("potentiel_invention", None)
    return monde


def refusee(monde, id="brune", par="marchand"):
    """Placement d'auteur : le propriétaire des vivres vient de lui refuser une part, et elle n'a
    pas de quoi la lui payer (``sans_le_sou``).

    Un affamé demande, puis achète s'il le peut, avant de voler ; ces tests portent sur ce qui
    suit le refus quand il ne reste que voler ou attendre.
    """
    from donjon.deliberation import retenir_refus
    retenir_refus(monde, id, par, "demander", "refus", objet="vivres")
    from donjon.esprits import lire
    lire(monde, id)["eveil"] = None  # Le refus est antérieur à cette scène d'auteur.
    return sans_le_sou(monde, id)


def sans_le_sou(monde, *ids):
    """Placement d'auteur : ils n'ont pas une pièce sur eux."""
    for id in ids:
        monde.data["finances_pnj"][id] = 0
    return monde


def sans_evacues(monde):
    """Placement d'auteur : le Relais des jalons A à C, sans Ilse, Aubin, ses planches ni le fanal.

    Ces tests isolent Gorm et Brune ; la vie à quatre PNJ est couverte par test_social.
    """
    for id in ("ilse", "aubin", "planches", "fanal"):
        monde.objets.pop(id, None)
        for table in monde.data.values():
            if isinstance(table, dict):
                table.pop(id, None)
        # Ce placement d'auteur retire les entités de la scène initiale ; il
        # ne simule pas leur disparition en partie. Le moteur ne purge plus
        # les souvenirs à distance d'après le seul registre des objets.
        for e in monde.data.get("esprits", {}).values():
            e["croyances"].pop(id, None)
    for o in monde.objets.values():
        if "liens" in o.get("profil", {}):
            o["profil"]["liens"] = {x: a for x, a in o["profil"]["liens"].items() if x in monde.objets or x == "joueur"}
        if "protege" in o.get("profil", {}):
            o["profil"]["protege"] = [x for x in o["profil"]["protege"] if x in monde.objets]
    return monde


def calme(monde, *ids):
    """Placement d'auteur : ces PNJ n'ont aucun besoin pressant et restent où ils sont ; leurs
    rondes viennent d'être faites, la routine ne les fait pas bouger de sitôt."""
    from donjon.esprits import lire
    for id in ids:
        besoins = lire(monde, id)["besoins"]
        for b in besoins:
            besoins[b] = 0.0
        for x in monde.objets[id]["profil"]["pulsions"]:
            if "periode" in x["condition"]:
                lire(monde, id)["visites"][x["condition"]["lieu"]] = monde.data["minutes"]
    return monde


def sans_souci(monde, *ids):
    """Scène d'auteur : acteurs sans souci spontané d'autrui, hors leurs charges.

    Données explicites, sans neutraliser le mécanisme du secours : les tests
    d'un appel, d'un prêt ou d'un refus peuvent ainsi conserver leur cause.
    Les besoins, croyances, droits, engagements et liens restent inchangés.
    """
    acteurs = ids or tuple(i for i, o in monde.objets.items() if o.get('profil'))
    for id in acteurs:
        monde.objets[id]['profil']['valeurs'].update(altruisme=0, empathie=0)
    return monde


def regarder(monde, qui, vers):
    """Placement d'auteur : ``qui`` (un PNJ ou le joueur) regarde vers un personnage, le joueur, un
    objet ou une case de sa salle."""
    from donjon.spatial import orientation_vers, position_cible
    if qui == "joueur":
        o = {**monde.joueur, "lieu": monde.joueur["salle"]}
        cible = tuple(vers) if not isinstance(vers, str) else position_cible(monde, vers, o["lieu"])
        monde.joueur["orientation"] = orientation_vers(tuple(o["position"]), cible) or monde.joueur.get("orientation")
        return monde
    o = monde.objets[qui]
    if vers == "joueur":
        cible = tuple(monde.joueur["position"])
    elif isinstance(vers, str):
        cible = position_cible(monde, vers, o["lieu"])
    else:
        cible = tuple(vers)
    o["orientation"] = orientation_vers(tuple(o["position"]), cible) or o.get("orientation", "sud")
    return monde


def presentes(monde, *ids):
    """Placement d'auteur : ces personnes ont déjà été présentées au joueur, noms entendus.

    Les tests d'identités (test_noms) partent sans cette préparation.
    """
    from donjon.noms import apprendre
    for id in ids or tuple(i for i,o in monde.objets.items() if o["type"] == "personnage"):
        apprendre(monde, "joueur", id)
    return monde


def possessions_deja_confiees(monde):
    """Placement d'auteur : les portages actuellement vus ont déjà été racontés.

    Isole les scènes qui éprouvent une autre parole ou un geste en cours des
    confidences d'inventaire initiales. Un transfert ou un changement de droits
    ultérieur reste une nouvelle, avec les vrais registres de faits dits.
    """
    from donjon.esprits import percevoir_tous, pnjs
    from donjon.social import nouvelles, retenir_dit
    percevoir_tous(monde)
    for id in pnjs(monde):
        for _, noyau, _, _ in nouvelles(monde, id):
            if noyau["type"] == "constat" and noyau["attribut"] == "lieu":
                for autre in pnjs(monde):
                    if autre != id:
                        retenir_dit(monde, id, autre, noyau)
    return monde


def lier(monde, id, autre, fiable, source="savoir"):
    """Placement d'auteur : un lien chiffré, remplaçant l'ancien savoir booléen des scènes."""
    from donjon import relations
    from donjon.esprits import esprit
    axes = {"confiance": 65 if fiable else 15, "affection": 20 if fiable else 0}
    r = relations._nouvelle(axes, monde.data["minutes"])
    r["source"] = source
    esprit(monde, id)["relations"][autre] = r


def relation(monde, id, autre):
    """Avis dérivé, pour les assertions des anciens contrats de parole (sans croyance stockée)."""
    from donjon import relations
    r = relations.envers(monde, id, autre)
    return {"valeur": relations.fiable(monde, id, autre), "source": r["source"], "minute": r["minute"]}
