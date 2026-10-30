"""Contrat des termes d'un marché ; aucune interprétation de mots du scénario."""
from .francais import quantite
from .monde import ErreurMonde


def _forme(proprietes):
    return {"type": "object", "additionalProperties": False,
            "properties": proprietes, "required": list(proprietes)}


def schema_terme(contrepartie=False, service=False):
    formes = [_forme({"type": {"type": "string", "enum": [t]}, "objet": {"type": "string"}})
              for t in ("objet", "part")]
    conditions = [_forme({"objet": {"type": "string"}, cle: valeur}) for cle, valeur in (
        ("allume", {"type": "boolean", "enum": [True]}),
        ("verrouillee", {"type": "boolean", "enum": [True]}),
        ("lieu", {"type": "string"}))]
    if service:
        conditions.append(_forme({"objet": {"type": "string"}, "servir": {"type": "string"}}))
        conditions.append(_forme({'objet': {'type': 'string'}, 'proteger': {'type': 'boolean', 'enum': [True]},
                                  'echeance': {'type': 'integer', 'minimum': 0}}))
    formes.append(_forme({"type": {"type": "string", "enum": ["tache"]},
                          "condition": {"anyOf": conditions}}))
    # Une seule clause nouvelle : une prestation ponctuelle avant un instant absolu.
    for forme in list(formes):
        if forme['properties']['type']['enum'][0] in ('part', 'tache'):
            proprietes = {**forme['properties'], 'limite': {'type': 'integer', 'minimum': 0}}
            if 'condition' in proprietes:
                proprietes['condition'] = {'anyOf': [c for c in conditions if 'proteger' not in c['properties']]}
            formes.append(_forme(proprietes))
    formes.extend([_forme({"type": {"type": "string", "enum": ["pieces"]},
                           "montant": {"type": "integer", "minimum": 1}}),
                   _forme({"type": {"type": "string", "enum": ["pieces"]},
                           "montant": {"type": "integer", "minimum": 1}, "objet": {
                               "type": "string", "description":
                               "Source des pièces : identifiant d'un contenant à pièces, jamais du bien acheté. "
                               "Omettre objet pour payer sur les fonds du donneur."}})])
    if contrepartie:
        formes.append(_forme({"type": {"type": "string", "enum": ["rien"]}}))
    return {"anyOf": formes}


SCHEMA = _forme({"type": {"type": "string", "enum": ["proposition"]},
                 "demande": schema_terme(service=True), "contrepartie": schema_terme(True, service=True)})


def schema_compilation():
    """Entrée libre : le modèle exprime une durée, le moteur fixe l'instant.

    Le contrat d'exécution SCHEMA reste absolu : aucune durée relative ne doit
    survivre dans une transaction, une confirmation ou une sauvegarde.
    """
    import copy
    s = copy.deepcopy(SCHEMA)
    for nom in ('demande', 'contrepartie'):
        for forme in s['properties'][nom]['anyOf']:
            if 'limite' in forme['properties']:
                forme['properties']['limite'] = {'anyOf': [
                    {'type': 'integer', 'minimum': 0,
                     'description': 'Instant absolu explicitement demandé, en dixièmes de seconde de jeu.'},
                    _forme({'dans_secondes': {'type': 'integer', 'minimum': 0,
                        'description': 'Délai relatif depuis la saisie, en secondes ; le moteur calcule la limite.'}})]}
    return s


def compiler_limites(contenu, maintenant):
    """Résout sur copie les durées de compilation ; jamais appelé à l'exécution."""
    import copy
    resultat = copy.deepcopy(contenu)
    for c in resultat:
        if not isinstance(c, dict) or c.get('type') != 'proposition':
            continue
        for nom in ('demande', 'contrepartie'):
            terme = c.get(nom, {})
            if not isinstance(terme, dict):
                continue  # Le validateur commun porte le refus de forme.
            limite = terme.get('limite')
            if isinstance(limite, dict):
                if (set(limite) != {'dans_secondes'}
                        or type(limite['dans_secondes']) is not int or limite['dans_secondes'] < 0):
                    raise ErreurMonde('Précise le délai de cet accord en secondes de jeu.',
                        f'contenu.{nom}.limite : reçu {limite!r} ; attendu {{dans_secondes: entier >= 0}}.')
                terme['limite'] = maintenant + limite['dans_secondes'] * 10
    return resultat


SCHEMA_OFFRE = _forme({"etat": {"type": "string", "enum": ["offre"]},
    "debiteur": {"type": "string"}, "creancier": {"type": "string"},
    "condition": schema_terme(True, service=True), "contrepartie": schema_terme(True)})


def offre(debiteur, creancier, condition, contrepartie):
    """Contrepartie promise par le débiteur contre la prestation du créancier.

    Ces termes conditionnels ne sont ni une dette exigible ni une remise accomplie.
    Mission et marché utilisent les mêmes termes, sans interpréter leur prose.
    """
    import copy
    return {"etat": "offre", "debiteur": debiteur, "creancier": creancier,
            "condition": copy.deepcopy(condition), "contrepartie": copy.deepcopy(contrepartie)}


def offre_en_mots(monde, o):
    from .voix import personne_pour_joueur
    def qui(id):
        return "toi" if id == "joueur" else personne_pour_joueur(monde, id, court=True)[0]
    return (f"Offre de {qui(o['debiteur'])} à {qui(o['creancier'])} : "
            f"{en_mots(monde, o['contrepartie'])} contre {en_mots(monde, o['condition'])}. "
            "Cette offre conditionnelle n'est pas une dette exigible ni un paiement.")


def cites_terme(terme):
    c = terme.get("condition", {})
    return [x for x in (terme.get("objet"), c.get("objet"), c.get("lieu")) if x]


def prestation(monde, donneur, receveur, terme):
    """Condition du travail à deviser ; None pour une remise à portée de main.

    Le terme reste une part : une livraison ne cède jamais le lot entier.
    Un service explicite (dont servir un repas) reste toujours une tâche.
    """
    from .biens import disponible_en_main
    if terme["type"] == "tache":
        return terme["condition"]
    if terme["type"] in ("objet", "part") and not disponible_en_main(monde, terme["objet"], donneur):
        return {"objet": terme["objet"], "remettre": receveur}
    return None


def en_mots(monde, terme):
    from .temps import instant
    return _en_mots(monde, terme) + (en_mots_limite(terme['limite'], instant(monde))
                                    if 'limite' in terme else '')


def en_mots_limite(limite, maintenant):
    from .temps import MINUTE, dire_duree
    minute, reste = divmod(limite, MINUTE)
    repere = f'la minute de jeu {minute}' + (' et ' + dire_duree(reste) if reste else '')
    return (' au plus tard à ' + repere + ' ('
            + (dire_duree(limite - maintenant) + ' restantes' if limite >= maintenant else 'limite passée') + ')')


def _en_mots(monde, terme):
    from .francais import designer, complement_de
    from .echanges import phrase_condition
    t = terme["type"]
    if t == "tache":
        return "la promesse que " + phrase_condition(monde, terme["condition"])
    if t == "pieces":
        return (f"{quantite(terme['montant'], 'pièce')}"
                + ((" prise dans " if terme["montant"] == 1 else " prises dans ")
                   + designer(monde.objets[terme["objet"]]) if "objet" in terme else ""))
    if t == "rien":
        return "rien"
    o = monde.objets[terme["objet"]]
    return "une part " + complement_de(o) if t == "part" else designer(o)


def erreur_terme(terme, contrepartie=True):
    """Unique contrat structurel, partagé par les propositions et leurs audits.

    Renvoie le champ, la valeur reçue et l'attendu ; les droits et connaissances
    se valident ensuite dans le monde. Aucun identifiant n'est interprété ici.
    """
    types = ("objet", "part", "tache", "pieces") + (("rien",) if contrepartie else ())
    if not isinstance(terme, dict) or terme.get("type") not in types:
        return "", terme, types
    t = terme["type"]
    if 'limite' in terme:
        if t not in ('part', 'tache'):
            return '.limite', terme['limite'], 'champ absent : paiement présent ; ni crédit ni prêt daté'
        if type(terme['limite']) is not int or terme['limite'] < 0:
            return '.limite', terme['limite'], 'entier >= 0 en dixièmes absolus'
    champs = {"type", *({"objet"} if t in ("objet", "part") else
                        {"condition"} if t == "tache" else {"montant"} if t == "pieces" else set())}
    if t == "pieces" and "objet" in terme:
        champs.add("objet")
    if 'limite' in terme:
        champs.add('limite')
    if set(terme) != champs:
        surplus = sorted(set(terme) - champs)
        if surplus:
            cle = surplus[0]
            return '.' + cle, terme[cle], 'champ absent ; prestation ponctuelle et paiement présent uniquement'
        return "", sorted(terme), sorted(champs)
    if "objet" in terme and not isinstance(terme["objet"], str):
        return ".objet", terme["objet"], "identifiant"
    if t == "pieces" and (type(terme["montant"]) is not int or terme["montant"] <= 0):
        return ".montant", terme["montant"], "entier strictement positif"
    if t == "tache":
        c = terme["condition"]
        if 'limite' in terme and isinstance(c, dict) and set(c) not in (
                {'objet', 'allume'}, {'objet', 'verrouillee'}, {'objet', 'lieu'}, {'objet', 'servir'}):
            return '.condition', c, 'prestation ponctuelle : allume, verrouillee, lieu ou servir ; ni prêt ni maintien continu'
        protection = (isinstance(c, dict) and set(c) == {'objet', 'proteger', 'echeance'}
                      and isinstance(c['objet'], str) and c['proteger'] is True
                      and type(c['echeance']) is int and c['echeance'] >= 0)
        if not protection and (not isinstance(c, dict) or not isinstance(c.get("objet"), str)
                or not (set(c) in ({"objet", "allume"}, {"objet", "verrouillee"})
                        and next(v for k, v in c.items() if k != "objet") is True
                        or set(c) in ({"objet", "lieu"}, {"objet", "servir"})
                        and isinstance(next(v for k, v in c.items() if k != "objet"), str))):
            return ".condition", c, "{objet, allume:true | verrouillee:true | lieu:salle | servir:personnage} ou {objet:personnage, proteger:true, echeance:minute}"
    return None


def verifier(monde, c, champ="contenu", proposant="joueur"):
    """Une forme refusée désigne toujours son champ, sa valeur et les valeurs acceptées."""
    def refuser(champ, recu, accepte):
        raise ErreurMonde("Les termes de cet échange doivent être précisés.",
                          f"{champ} : reçu {recu!r} ; attendu {accepte}.")

    if set(c) != {"type", "demande", "contrepartie"}:
        refuser(champ, sorted(c), "type, demande, contrepartie")
    from .deliberation import _connus
    from .paroles import resoudre
    connus_pnj = set(_connus(monde, proposant)) if proposant != "joueur" else set()
    if proposant != 'joueur':
        from .esprits import lire
        connus_pnj.update(x for x in ('joueur',) if x in lire(monde, proposant)['croyances'])
    def connu(x):
        return resoudre(monde, x) == x if proposant == "joueur" else x in connus_pnj
    for nom in ("demande", "contrepartie"):
        terme = c[nom]
        chemin = f"{champ}.{nom}"
        erreur = erreur_terme(terme, nom == "contrepartie")
        if erreur:
            suffixe, recu, accepte = erreur
            refuser(chemin + suffixe, recu, accepte)
        t = terme["type"]
        if t in ("objet", "part"):
            from .paroles import resoudre
            from .deliberation import besoin_de_part
            objet = terme["objet"]
            if not isinstance(objet, str) or objet not in monde.objets or not connu(objet):
                from .refus import cibles
                connus = [i for i, o in monde.objets.items() if o.get("mobile")
                          and o["type"] not in ("personnage", "depouille") and connu(i)]
                refuser(chemin + ".objet", objet, "identifiant parmi " + cibles(monde, connus))
            o = monde.objets[objet]
            if not o.get("mobile") or o["type"] in ("personnage", "depouille"):
                refuser(chemin + ".objet", objet, "objet mobile, hors personnage")
            if t == "part" and besoin_de_part(o) is None:
                refuser(chemin + ".objet", objet, "ressource comptée")
        elif t == "tache":
            from .deliberation import condition_valide
            from .paroles import resoudre
            condition = terme["condition"]
            if not condition_valide(monde, condition):
                refuser(chemin + ".condition", condition, "condition exécutable : {objet, allume:true | verrouillee:true | lieu:salle | servir:personnage} ou {objet:personnage, proteger:true, echeance:minute}")
            for cle, valeur in condition.items():
                if cle in ("objet", "lieu", "servir") and not (connu(valeur) or proposant != "joueur" and cle == "lieu" and valeur in monde.data["salles"]):
                    refuser(chemin + ".condition." + cle, valeur, "identifiant connu de Corvus")
        elif t == "pieces":
            if "objet" in terme:
                objet = terme["objet"]
                if (not isinstance(objet, str) or not connu(objet)
                        or "pieces" not in monde.objets.get(objet, {})):
                    refuser(chemin + ".objet", objet,
                            "source des pièces : identifiant connu d’un objet à pièces ; "
                            "ce champ ne désigne pas le bien acheté. "
                            f"Pour les fonds du donneur, retirer {chemin}.objet et conserver "
                            f"le terme {{'type': 'pieces', 'montant': {terme['montant']!r}}}")
    for nom, autre in (('demande', 'contrepartie'), ('contrepartie', 'demande')):
        if 'limite' in c[nom] and c[autre]['type'] != 'pieces':
            refuser(f'{champ}.{autre}.type', c[autre]['type'],
                    'pieces payées maintenant contre la prestation datée')


def demande_utile(monde, id, demande):
    """Un lot divisible sert une unité ; les pièces couvrent le manque propre.

    La source reste nommée : ni cession du contenant, ni paiement sur une
    autre bourse. Une quantité inconnue n'est jamais inventée.
    """
    from math import ceil
    from .biens import richesse
    from .caractere import besoin_d_argent
    from .deliberation import besoin_de_part
    from .esprits import croyance
    objet = demande.get("objet")
    if objet is None and demande["type"] != "pieces":
        return demande
    manque = max(0, ceil(besoin_d_argent(monde, id) - richesse(monde, id)))
    if objet is None:
        n = min(demande["montant"], manque)
        return {**demande, "montant": n} if n > 0 else None
    o = monde.objets[objet]
    if "pieces" in o:
        crue = croyance(monde, id, objet, "pieces")
        n = min(crue["valeur"] if crue else 0, manque, demande.get("montant", manque))
        return {"type": "pieces", "objet": objet, "montant": n} if n > 0 else None
    return {"type": "part" if besoin_de_part(o) else "objet", "objet": objet}


def taches_crues(monde, id, autre):
    """Services typés suggérés par un manque observé, jamais par le profil adverse.

    Une propriété publique ne suffit pas : l'état à réparer doit être connu.
    Les conditions déjà entendues dans un refus sont également réutilisables.
    """
    from .deliberation import _connus, _cru, condition_valide, satisfaite, salle_crue
    from .biens import proprietaire
    from .esprits import lire
    conditions = []
    for refus in lire(monde, id)["refus"]:
        offre = refus.get("contre_offre", {})
        terme = offre.get("condition", {})
        if refus["de"] == autre and terme.get("type") == "tache":
            conditions.append(terme["condition"])
    for o in sorted(_connus(monde, id)):
        if o not in monde.objets:
            continue
        possesseur = proprietaire(monde, o)
        if possesseur != autre and not (possesseur is None and
                salle_crue(monde, id, o) == salle_crue(monde, id, autre)):
            continue
        etat = _cru(monde, id, o, "etat") or {}
        if "allume" in etat and (not etat["allume"] or etat.get("faible")):
            conditions.append({"objet": o, "allume": True})
        if _cru(monde, id, o, "verrouillee") is False:
            conditions.append({"objet": o, "verrouillee": True})
    vus = []
    for c in conditions:
        if c not in vus and condition_valide(monde, c) and not satisfaite(monde, id, c):
            vus.append(c)
            yield {"type": "tache", "condition": c}


def payer_terme(monde, de, a, terme):
    """Paiement commun, éventuellement prélevé sur la seule source convenue."""
    from .biens import payer, bourse, noter_compte, compte
    n = terme["montant"]
    if "objet" not in terme:
        payer(monde, de, a, n)
        return
    monde.objets[terme["objet"]]["pieces"] -= n
    if a == "joueur":
        monde.joueur["or"] += n
    else:
        monde.data["finances_pnj"][a] = bourse(monde, a) + n
    noter_compte(monde, compte(de, a, montant=n, etat="rendu"))


def demande_financee(monde, id, demande, contrepartie):
    """Les pièces demandées ne dépassent ni le manque ni le prix offert.

    Pour les biens indivisibles, l'évaluation commune décide si le marché
    a encore une chance ; aucune fraction d'outil n'est inventée.
    """
    from .biens import prix
    from .echanges import PRIX_SANS_PRIX
    from .esprits import croyance
    if demande["type"] != "pieces":
        return demande
    t = contrepartie["type"]
    if t == "pieces":
        n = contrepartie["montant"]
    elif t in ("objet", "part"):
        objet = contrepartie["objet"]
        n = prix(monde, objet, t == "part") or PRIX_SANS_PRIX
        if t == "objet" and "pieces" in monde.objets[objet]:
            crue = croyance(monde, id, objet, "pieces")
            n += crue["valeur"] if crue else 0
    elif t == "tache":
        # Le prix d'un travail n'est pas le prix d'un objet. Son devis et
        # l'utilité pour le payeur sont jugés par le marché commun.
        return demande
    else:
        return None
    return {**demande, "montant": min(demande["montant"], n)} if n > 0 else None
