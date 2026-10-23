"""Noms appris et désignations visuelles : projection publique des identités du moteur."""
import re
from functools import lru_cache

from .monde import normaliser, ErreurMonde

# Une personne, vivante ou morte : la dépouille garde l'identifiant et le nom du défunt
# (``corps.mourir``), que le joueur ne lit pas plus qu'avant s'il ne l'a jamais entendu.
PERSONNES = ("personnage", "depouille")


@lru_cache(maxsize=256)
def _variantes_nom(nom_reel):
    """Du nom complet au prénom, avec leurs frontières de mot, sans changer leur ordre."""
    variantes = sorted({nom_reel, nom_reel.split(',')[0], nom_reel.split()[0]},
                       key=len, reverse=True)
    return tuple((nom, re.compile(r"(?<!\w)" + re.escape(nom) + r"(?!\w)", re.I))
                 for nom in variantes if nom)


def _numero(entrees, identifiant, nouveaux, personnes=False):
    """Numéro déjà enregistré, sinon rang stable après les numéros existants."""
    numero = entrees.get(identifiant)
    if personnes and identifiant in entrees:
        return entrees[identifiant]["n"]
    if numero:
        return numero
    numeros = (entree["n"] for entree in entrees.values()) if personnes else entrees.values()
    return max(numeros, default=0) + sorted(nouveaux).index(identifiant) + 1


def _nom_reel(monde, identifiant, objet):
    """Le nom que porte la personne : celui du défunt pour une dépouille."""
    defunt = monde.data.get("defunts", {}).get(identifiant) if objet["type"] == "depouille" else None
    return defunt["nom"] if defunt else objet["nom"]


def installer(monde):
    """Installe les mémoires et attribue les références dans l'ordre des identifiants."""
    donnees = monde.data
    donnees.setdefault("noms_connus", list(donnees.get("scenario", {}).get("noms_connus", [])))
    personnes = donnees.setdefault("personnes", {})
    elements = donnees.setdefault("references_personnes", {})
    for identifiant in sorted(monde.objets):
        if identifiant not in elements:
            elements[identifiant] = _numero(elements, identifiant, [identifiant])
    for identifiant, objet in sorted(monde.objets.items()):
        if objet["type"] != "personnage" or identifiant in personnes:
            continue
        base = apparence(objet)
        deja = [entree["nom"] for entree in personnes.values()]
        nom, rang = base, 2
        while nom in deja:
            nom = f"{base} ({rang})"
            rang += 1
        personnes[identifiant] = {"n": _numero(personnes, identifiant, [identifiant], personnes=True),
                                 "nom": nom}


def apparence(o):
    """Première proposition du portrait, sans nom ni fonction sociale ; repli sur le genre."""
    genre = "femme" if o.get("genre") == "f" else "homme"
    texte = o.get("designation_visuelle") or o.get("portrait") or o.get("description_visuelle", "")
    nom = o["nom"].split(",")[0].split()[0]
    texte = re.sub(r"^" + re.escape(nom) + r"\s+est\s+", "", texte, flags=re.I)
    texte = re.split(r"[,.;]", texte, maxsplit=1)[0].strip()
    texte = re.sub(r"^(?:une |un |le |la |l')", "", texte, flags=re.I)
    # Un portrait sans proposition exploitable ne fait pas inventer un trait.
    if not texte or re.search(r"\b" + re.escape(nom) + r"\b", texte, re.I):
        texte = genre
    if not re.search(r"\b(?:homme|femme|garçon|fille|enfant|vieillard)\b", texte, re.I):
        texte = genre + " " + texte
    texte = re.split(r"\s+(?:d['’]|aux\b|au\b|avec\b|les\b|ses\b)", texte, maxsplit=1)[0]
    texte = " ".join(texte.split()[:5])
    if texte[:1].lower() in "aàâeéèêiîoôuùh":
        article = "l'"
    elif o.get("genre") == "f":
        article = "la "
    else:
        article = "le "
    return article + texte


def connait(monde, qui, autre):
    """Un lien nominal vient d'un apprentissage ou d'un savoir d'auteur, jamais d'une vue."""
    if qui == autre:
        return True
    if qui == "joueur":
        return autre in monde.data.get("noms_connus", [])
    from .esprits import lire  # esprits installe lui-même la mémoire des noms.
    esprit = lire(monde, qui)
    if autre in esprit["noms"] or autre in monde.objets.get(qui, {}).get("connait_noms", []):
        return True
    # Un savoir est déclaré par l'auteur ; une perception n'est jamais une présentation.
    return any(c.get("source") == "savoir"
               for c in esprit["croyances"].get(autre, {}).values())


def apprendre(monde, qui, autre):
    """Ajoute une fois le nom à la mémoire de son auditeur."""
    if connait(monde, qui, autre):
        return False
    from .esprits import esprit
    noms = monde.data["noms_connus"] if qui == "joueur" else esprit(monde, qui)["noms"]
    noms.append(autre)
    return True


def designation(monde, id):
    """Référence opaque d'un corps, persistée ou calculée sans mutation."""
    personnes = monde.data.get("personnes", {})
    nouveaux = (identifiant for identifiant, objet in monde.objets.items()
                if objet["type"] == "personnage" and identifiant not in personnes)
    return f"personne_{_numero(personnes, id, nouveaux, personnes=True)}"


def nom(monde, id, observateur="joueur"):
    """Désignation visuelle d'après l'observateur, jamais la vue du joueur pour un PNJ."""
    if observateur == "joueur":
        vu = monde.visible(id) or id in monde.data.get("personnages_vus", [])
    else:
        from .esprits import lire, percoit
        vu = percoit(monde, observateur, id) or any(
            c.get("source") == "vu" for c in lire(monde, observateur)["croyances"].get(id, {}).values())
    if not vu:
        return 'une personne inconnue'
    return monde.data.get("personnes", {}).get(id, {}).get("nom") or apparence(monde.objets[id])


def resoudre(monde, reference):
    """Une désignation ne vise que quelqu'un de perçu ou reconnu de vue, jamais un nom deviné."""
    reference_normale = normaliser(reference or "")

    def sans_article(texte):
        return re.sub(r"^(?:le |la |l'|un |une )", "", normaliser(texte))

    candidats = []
    for identifiant in monde.data.get("personnes", {}):
        if not (monde.designable(identifiant) or identifiant in monde.data.get("personnages_vus", [])):
            continue
        if (reference_normale == designation(monde, identifiant)
                or sans_article(reference_normale) == sans_article(nom(monde, identifiant))):
            candidats.append(identifiant)
    if candidats:
        return candidats[0] if len(candidats) == 1 else None
    from .voix import reel
    cible = reel(monde, reference)
    if (isinstance(reference, str) and reference.startswith("element_")
            and cible in monde.objets and monde.designable(cible)):
        return cible
    elements = _elements(monde)
    candidats = [identifiant for identifiant in elements if monde.designable(identifiant)
                 and sans_article(reference_normale) == sans_article(texte(monde, monde.objets[identifiant]["nom"]))]
    return candidats[0] if len(candidats) == 1 else None


def _designation_texte(monde, identifiant, objet, observateur):
    """Désigne un inconnu d'après le corps vu ou la voix entendue par l'observateur."""
    # social et voix emploient eux-mêmes noms pour leurs rendus.
    if observateur != "joueur":
        from .social import _qui
        return _qui(monde, identifiant, observateur)
    if objet["type"] == "depouille":
        return nom(monde, identifiant)
    from .voix import designation as voix, nom_pour_joueur
    identite = voix(monde, identifiant)
    if identite.startswith("personne_"):
        return nom(monde, identifiant)
    if identite != identifiant:
        return nom_pour_joueur(monde, identifiant)
    return "une personne inconnue"


def _complement_defunt(monde, identifiant, designe):
    """Passe de la désignation définie du vivant au complément « d'un… » du corps."""
    article = "une " if monde.data["defunts"].get(identifiant, {}).get("genre") == "f" else "un "
    defini = re.match(r"(?:le |la |l')", designe)
    if defini:
        indefini = article + designe[defini.end():]
    elif re.match(r"(?:une? |quelqu'un)", designe):
        indefini = designe
    else:
        indefini = article + designe
    return ("d'" if indefini[:1].lower() in "aeiouhéèê" else "de ") + indefini


def _remplacer_noms(monde, partie, observateur):
    """Remplace dans l'ordre du monde les noms que cet observateur n'a pas appris."""
    personnes = monde.objets.items()
    if observateur != "joueur":
        personnes = [("joueur", monde.joueur), *personnes]
    for identifiant, objet in personnes:
        if identifiant != "joueur" and objet["type"] not in PERSONNES:
            continue
        if connait(monde, observateur, identifiant):
            continue
        reel = monde.joueur["nom"] if identifiant == "joueur" else _nom_reel(monde, identifiant, objet)
        variantes = _variantes_nom(reel)
        if not any(motif.search(partie) for _, motif in variantes):
            continue
        designe = _designation_texte(monde, identifiant, objet, observateur)
        if identifiant != "joueur" and objet["type"] == "depouille":
            complement = _complement_defunt(monde, identifiant, designe)

            def remplacer_complement(correspondance):
                return complement

            for variante, _ in variantes:
                motif = r"(?<!\w)de\s+" + re.escape(variante) + r"(?!\w)"
                partie = re.sub(motif, remplacer_complement, partie, flags=re.I)

        def remplacer_nom(correspondance):
            if correspondance.group()[:1].isupper():
                return designe[:1].upper() + designe[1:]
            return designe

        for _, motif in variantes:
            partie = motif.sub(remplacer_nom, partie)
    return partie


def _motif_citations(monde):
    """Protège les citations et les appellations portées par des voix déjà entendues."""
    # Ces désignations proviennent de voix réellement entendues ; elles ne nomment pas leur corps.
    portees = {e.get(k) for e in monde.data.get("voix_entendues", {}).values() for k in ("se_dit", "appelee")}
    voix = []
    for id in portees:
        if id in monde.objets or id == "joueur":
            n = (monde.joueur if id == "joueur" else monde.objets[id])["nom"].split(",")[0]
            voix.extend(prefixe + n for prefixe in ("une voix qui se dit ", "la voix qui se dit ",
                                                   "une voix qu'on appelle ", "la voix qu'on appelle "))
    return r"(«[^»]*»" + ("|" + "|".join(re.escape(v) for v in voix) if voix else "") + ")"


def texte(monde, valeur, citations=False, observateur="joueur"):
    """Rendu des textes du moteur : les citations sont des mots effectivement prononcés."""
    if not isinstance(valeur, str):
        return valeur
    if not citations:
        return _remplacer_noms(monde, valeur, observateur)
    morceaux = re.split(_motif_citations(monde), valeur, flags=re.I)
    return "".join(morceau if indice % 2 else _remplacer_noms(monde, morceau, observateur)
                   for indice, morceau in enumerate(morceaux))


def _elements(monde):
    """Les références de détails liés à une personne, sans dépendre de l'orthographe des ids."""
    parents = {}
    for identifiant, objet in monde.objets.items():
        vus, parent = {identifiant}, objet.get("lieu")
        while parent in monde.objets and parent not in vus:
            vus.add(parent)
            if monde.objets[parent]["type"] in PERSONNES:
                parents[identifiant] = parent
                break
            parent = monde.objets[parent].get("lieu")
    return parents


def reference(monde, id):
    """Masque l'identifiant d'une personne inconnue et de ses éléments associés."""
    if monde.objets.get(id, {}).get("type") in PERSONNES and not connait(monde, "joueur", id):
        from .voix import designation as voix
        ref = voix(monde, id)
        return ref if ref != id else designation(monde, id)
    parent = _elements(monde).get(id)
    if parent and not connait(monde, "joueur", parent):
        numeros = monde.data.get("references_personnes", {})
        nouveaux = (identifiant for identifiant in monde.objets if identifiant not in numeros)
        return f"element_{_numero(numeros, id, nouveaux)}"
    return id


def _garde_citations(conteneur, champ, citations):
    """Champs dont le contenu représente des paroles ou des résultats déjà enregistrés."""
    evenement = "locuteur" in conteneur and "auditeurs" in conteneur and "revision" in conteneur
    return (citations or evenement and champ == "texte"
            or conteneur.get("voix_inconnue") is True and champ == "nom"
            or champ in ("conversation_validee", "paroles_entendues", "evenements_recents",
                         "resultat_resolu", "attestations"))


def public(monde, valeur, citations=False):
    """Projection des références et descriptions ; seules les paroles enregistrées gardent leurs mots."""
    if isinstance(valeur, list):
        return [public(monde, v, citations) for v in valeur]
    if isinstance(valeur, dict):
        inconnue = valeur.get("type") in PERSONNES and not connait(monde, "joueur", valeur.get("id"))
        if inconnue and "aliases" in valeur:
            valeur = {**valeur, "aliases": []}
        projection = {}
        for champ, contenu in valeur.items():
            champ_public = public(monde, champ)
            if champ in ("noms_pour_repliques", "noms_entendus"):
                projection[champ_public] = contenu
            else:
                citations_contenu = _garde_citations(valeur, champ, citations)
                projection[champ_public] = public(monde, contenu, citations_contenu)
        return projection
    if isinstance(valeur, str):
        if valeur in monde.objets:
            return reference(monde, valeur)
        if valeur.startswith("objet:") and valeur[6:] in monde.objets:
            return "objet:" + reference(monde, valeur[6:])
        return texte(monde, valeur, citations)
    return valeur


CHAMPS_REFERENCES = {"cible", "outil", "personnage", "sujet", "valeur", "ancrage", "support", "objet", "moyen",
                     "destination", "lieu", "porteur", "auteur", "locuteur"}
LISTES_REFERENCES = {"cibles", "destinataires"}


def verifier_references(monde, valeur, faits):
    """À l'entrée du MJ, une référence privée devinée ne remplace pas la référence fournie.

    Les textes libres et le nom revendiqué du contenu nominal sont des mots, pas des corps.
    Ils gardent leurs contrats propres ; cette vérification ne les réécrit jamais.
    """
    from .refus import RefusDeForme
    from .voix import reel
    publiques = set()

    def collecter(valeur):
        """Les mots et les clés effectivement fournis, sans en inférer de références."""
        if isinstance(valeur, str):
            publiques.add(valeur)
        elif isinstance(valeur, list):
            for element in valeur:
                collecter(element)
        elif isinstance(valeur, dict):
            for champ, contenu in valeur.items():
                publiques.add(champ)
                collecter(contenu)

    collecter(faits)

    def verifier_reference(valeur, champ):
        if not isinstance(valeur, str):
            return
        identifiant = reel(monde, valeur)
        opaque = bool(re.fullmatch(r'(?:personne|element|voix|voix_reconnue)_\d+', valeur))
        prive = identifiant in monde.objets and reference(monde, identifiant) != identifiant
        if (prive and valeur == identifiant) or (opaque and valeur not in publiques):
            acceptes = sorted(mot for mot in publiques if reel(monde, mot) in monde.objets)
            raise RefusDeForme("Cette référence de personne n'a pas été fournie au MJ.",
                              f"{champ} : reçu « {valeur} » ; une référence publique fournie, parmi {', '.join(acceptes)}, ou vide si le champ ne s'applique pas.")

    def parcourir(valeur, chemin='proposition'):
        if isinstance(valeur, list):
            for indice, element in enumerate(valeur):
                parcourir(element, f'{chemin}[{indice}]')
        elif isinstance(valeur, dict):
            for cle, contenu in valeur.items():
                champ = f'{chemin}.{cle}'
                if cle == 'sujet' and valeur.get('type') == 'nom':
                    continue
                if cle in CHAMPS_REFERENCES:
                    verifier_reference(contenu, champ)
                elif cle in LISTES_REFERENCES and isinstance(contenu, list):
                    for indice, reference_ in enumerate(contenu):
                        verifier_reference(reference_, f'{champ}[{indice}]')
                parcourir(contenu, champ)

    parcourir(valeur)


def references(monde, valeur):
    """Décode seulement les champs de référence, jamais la prose ou les mots du joueur."""
    from .voix import reel
    if isinstance(valeur, list):
        return [references(monde, v) for v in valeur]
    if isinstance(valeur, dict):
        decodee = {}
        for champ, contenu in valeur.items():
            liste = (champ in LISTES_REFERENCES and isinstance(contenu, list)
                     and all(isinstance(element, str) for element in contenu))
            ancrage_parole = champ == "ancrage" and valeur.get("type") == "parole"
            if liste:
                decodee[champ] = [reel(monde, element) for element in contenu]
            elif champ in CHAMPS_REFERENCES and isinstance(contenu, str) and not ancrage_parole:
                decodee[champ] = reel(monde, contenu)
            else:
                decodee[champ] = references(monde, contenu)
        return decodee
    return valeur


def entendre(monde, qui, auteur, mots, adresses=()):
    """Relie seulement une présentation du locuteur ou un destinataire appelé par son nom.

    Une mention de tiers n'indique pas à l'auditeur lequel des corps porte ce nom.
    ``adresses`` vient du contrat typé de parole, jamais d'une recherche parmi les vrais noms.
    """
    from .voix import identifie, nom_dit, connait_nom, nommer, se_nommer
    from .paroles import nom_dans
    nom_affirme = nom_dans(monde, mots)
    if nom_affirme == auteur:
        se_nommer(monde, qui, auteur, nom_affirme)
    for id in adresses:
        if id != auteur and id != nom_affirme and connait_nom(monde, auteur, id) \
                and nom_dit(monde, id, mots) and identifie(monde, qui, id):
            nommer(monde, qui, id, id)


def presenter(monde, qui, auteur, presentation, mots):
    """Une présentation typée attribue les mots au locuteur, sans nommer un autre corps."""
    if (not isinstance(presentation, str) or not presentation.strip()
            or not re.search(r'(?<!\w)' + re.escape(presentation) + r'(?!\w)', mots)):
        raise ErreurMonde("La présentation ne correspond pas aux mots prononcés.",
                          "presentation : le nom littéral contenu dans la citation du locuteur.")
    from .paroles import _nom_dit
    from .voix import se_nommer
    nom_ = _nom_dit(monde, presentation)
    if nom_:
        se_nommer(monde, qui, auteur, nom_)


def _designation_valide(identifiant, entree):
    """Forme d'une entrée persistante, avant le contrôle d'unicité des numéros."""
    if not isinstance(identifiant, str) or not isinstance(entree, dict):
        return False
    if set(entree) != {"n", "nom"}:
        return False
    if type(entree["n"]) is not int or entree["n"] <= 0:
        return False
    return isinstance(entree["nom"], str) and 1 <= len(entree["nom"]) <= 100


def verifier(monde):
    """Contrôle séparément la mémoire nominale, les désignations et leurs numéros uniques."""
    noms = monde.data.get("noms_connus", [])
    assert (isinstance(noms, list) and all(isinstance(nom, str) for nom in noms)
            and len(set(noms)) == len(noms)), "Noms appris invalides"
    personnes = monde.data.get("personnes", {})
    assert (isinstance(personnes, dict)
            and all(_designation_valide(identifiant, entree)
                    for identifiant, entree in personnes.items())), "Désignations invalides"
    assert len({e["n"] for e in personnes.values()}) == len(personnes), "Pseudonymes ambigus"
    refs = monde.data.get("references_personnes", {})
    assert (isinstance(refs, dict)
            and all(isinstance(identifiant, str) and type(numero) is int and numero > 0
                    for identifiant, numero in refs.items())), "Références publiques invalides"
    assert len(set(refs.values())) == len(refs), "Références publiques ambiguës"
