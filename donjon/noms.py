"""Noms appris et désignations visuelles : projection publique des identités du moteur."""
import re

from .monde import normaliser, ErreurMonde


def installer(monde):
    d = monde.data
    d.setdefault("noms_connus", list(d.get("scenario", {}).get("noms_connus", [])))
    d.setdefault("personnes", {})
    elements = d.setdefault("references_personnes", {})
    for id in sorted(monde.objets):
        if id not in elements:
            elements[id] = max(elements.values(), default=0) + 1
    for id, o in sorted(monde.objets.items()):
        if o["type"] != "personnage" or id in d["personnes"]:
            continue
        base = apparence(o)
        deja = [e["nom"] for e in d["personnes"].values()]
        nom, rang = base, 2
        while nom in deja:
            nom = f"{base} ({rang})"
            rang += 1
        d["personnes"][id] = {"n": 1 + max((e["n"] for e in d["personnes"].values()), default=0), "nom": nom}


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
    return ("l'" if texte[:1].lower() in "aàâeéèêiîoôuùh" else "la " if o.get("genre") == "f" else "le ") + texte


def connait(monde, qui, autre):
    if qui == autre:
        return True
    if qui == "joueur":
        return autre in monde.data.get("noms_connus", [])
    from .esprits import lire
    e = lire(monde, qui)
    if autre in e["noms"] or autre in monde.objets.get(qui, {}).get("connait_noms", []):
        return True
    # Un savoir est déclaré par l'auteur ; une perception n'est jamais une présentation.
    return any(c.get("source") == "savoir"
               for c in e["croyances"].get(autre, {}).values())


def apprendre(monde, qui, autre):
    if connait(monde, qui, autre):
        return False
    from .esprits import esprit
    noms = monde.data["noms_connus"] if qui == "joueur" else esprit(monde, qui)["noms"]
    noms.append(autre)
    return True


def designation(monde, id):
    personnes = monde.data.get("personnes", {})
    if id in personnes:
        n = personnes[id]["n"]
    else:
        nouveaux = sorted(i for i, o in monde.objets.items() if o["type"] == "personnage" and i not in personnes)
        n = max((e["n"] for e in personnes.values()), default=0) + nouveaux.index(id) + 1
    return f"personne_{n}"


def nom(monde, id):
    if not monde.visible(id) and id not in monde.data.get('personnages_vus',[]):
        return 'une personne inconnue'
    return monde.data.get("personnes", {}).get(id, {}).get("nom") or apparence(monde.objets[id])


def resoudre(monde, reference):
    """Une désignation ne vise que quelqu'un de perçu ou reconnu de vue, jamais un nom deviné."""
    reference_normale = normaliser(reference or "")
    def sans_article(s):
        return re.sub(r"^(?:le |la |l'|un |une )", "", normaliser(s))
    candidats = [id for id in monde.data.get("personnes", {})
                 if (monde.designable(id) or id in monde.data.get("personnages_vus", []))
                 and (reference_normale == designation(monde, id) or sans_article(reference_normale) == sans_article(nom(monde, id)))]
    if candidats:
        return candidats[0] if len(candidats) == 1 else None
    from .voix import reel
    cible = reel(monde, reference)
    if isinstance(reference,str) and reference.startswith("element_") and cible in monde.objets and monde.designable(cible):
        return cible
    elements = _elements(monde)
    candidats = [id for id in elements if monde.designable(id)
                 and sans_article(reference_normale) == sans_article(texte(monde,monde.objets[id]["nom"]))]
    return candidats[0] if len(candidats) == 1 else None


def texte(monde, valeur, citations=False, observateur="joueur"):
    """Rendu des textes du moteur : les citations sont des mots effectivement prononcés."""
    if not isinstance(valeur, str):
        return valeur
    def remplacer(partie):
        personnes = [("joueur", monde.joueur), *monde.objets.items()] if observateur != "joueur" else monde.objets.items()
        for id, o in personnes:
            if (id != "joueur" and o["type"] != "personnage") or connait(monde, observateur, id):
                continue
            noms=sorted({o['nom'],o['nom'].split(',')[0],o['nom'].split()[0]},key=len,reverse=True)
            if not any(n and re.search(r'(?<!\w)'+re.escape(n)+r'(?!\w)',partie,re.I) for n in noms):
                continue
            if observateur == "joueur":
                from .voix import designation as voix, nom_pour_joueur
                identite=voix(monde,id)
                designe = (nom(monde,id) if identite.startswith('personne_') else
                           nom_pour_joueur(monde,id) if identite!=id else 'une personne inconnue')
            else:
                from .social import _qui
                designe = _qui(monde, id, observateur)
            for n in noms:
                if n:
                    partie = re.sub(r"(?<!\w)" + re.escape(n) + r"(?!\w)", lambda m: (designe[:1].upper() + designe[1:] if m.group()[:1].isupper() else designe), partie, flags=re.I)
        return partie
    if not citations:
        return remplacer(valeur)
    # Ces désignations proviennent de voix réellement entendues ; elles ne nomment pas leur corps.
    portees = {e.get(k) for e in monde.data.get("voix_entendues", {}).values() for k in ("se_dit", "appelee")}
    voix = []
    for id in portees:
        if id in monde.objets or id == "joueur":
            n = (monde.joueur if id == "joueur" else monde.objets[id])["nom"].split(",")[0]
            voix.extend(prefixe + n for prefixe in ("une voix qui se dit ", "la voix qui se dit ",
                                                   "une voix qu'on appelle ", "la voix qu'on appelle "))
    motif = r"(«[^»]*»" + ("|" + "|".join(re.escape(v) for v in voix) if voix else "") + ")"
    morceaux = re.split(motif, valeur, flags=re.I)
    return "".join(p if i % 2 else remplacer(p) for i, p in enumerate(morceaux))


def _elements(monde):
    """Les références de détails liés à une personne, sans dépendre de l'orthographe des ids."""
    parents = {}
    for id, o in monde.objets.items():
        vus, parent = {id}, o.get("lieu")
        while parent in monde.objets and parent not in vus:
            vus.add(parent)
            if monde.objets[parent]["type"] == "personnage":
                parents[id] = parent
                break
            parent = monde.objets[parent].get("lieu")
    return parents


def reference(monde, id):
    if monde.objets.get(id, {}).get("type") == "personnage" and not connait(monde, "joueur", id):
        from .voix import designation as voix
        ref=voix(monde,id)
        return ref if ref!=id else designation(monde,id)
    parent = _elements(monde).get(id)
    if parent and not connait(monde, "joueur", parent):
        return "element_" + str(monde.data.get("references_personnes", {}).get(id) or
                                max(monde.data.get("references_personnes", {}).values(), default=0) +
                                sorted(i for i in monde.objets if i not in monde.data.get("references_personnes", {})).index(id) + 1)
    return id


def public(monde, valeur, citations=False):
    """Projection des références et descriptions ; seules les paroles enregistrées gardent leurs mots."""
    if isinstance(valeur, list):
        return [public(monde, v, citations) for v in valeur]
    if isinstance(valeur, dict):
        evenement = "locuteur" in valeur and "auditeurs" in valeur and "revision" in valeur
        inconnue = valeur.get("type") == "personnage" and not connait(monde,"joueur",valeur.get("id"))
        if inconnue and "aliases" in valeur:
            valeur = {**valeur,"aliases": []}
        return {public(monde, k): (v if k in ("noms_pour_repliques", "noms_entendus") else
                public(monde, v, citations or evenement and k == "texte" or valeur.get("voix_inconnue") is True and k == "nom" or
                       k in ("conversation_validee", "paroles_entendues", "evenements_recents", "resultat_resolu", "attestations")))
                for k, v in valeur.items()}
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
    publiques=set()
    def collecter(v):
        if isinstance(v,str): publiques.add(v)
        elif isinstance(v,list):
            for x in v: collecter(x)
        elif isinstance(v,dict):
            for k,x in v.items(): publiques.add(k); collecter(x)
    collecter(faits)
    def verifier(v,champ):
        if not isinstance(v,str): return
        id_=reel(monde,v)
        opaque=bool(re.fullmatch(r'(?:personne|element|voix|voix_reconnue)_\d+',v))
        prive=id_ in monde.objets and reference(monde,id_)!=id_
        if prive and v==id_ or opaque and v not in publiques:
            acceptes=sorted(x for x in publiques if reel(monde,x) in monde.objets)
            raise RefusDeForme("Cette référence de personne n'a pas été fournie au MJ.",
                              f"{champ} : reçu « {v} » ; une référence publique fournie, parmi {', '.join(acceptes)}, ou vide si le champ ne s'applique pas.")
    def parcourir(v,chemin='proposition'):
        if isinstance(v,list):
            for i,x in enumerate(v): parcourir(x,f'{chemin}[{i}]')
        elif isinstance(v,dict):
            for k,x in v.items():
                champ=f'{chemin}.{k}'
                if k=='sujet' and v.get('type')=='nom': continue
                if k in CHAMPS_REFERENCES: verifier(x,champ)
                elif k in LISTES_REFERENCES and isinstance(x,list):
                    for i,r in enumerate(x): verifier(r,f'{champ}[{i}]')
                parcourir(x,champ)
    parcourir(valeur)


def references(monde, valeur):
    """Décode seulement les champs de référence, jamais la prose ou les mots du joueur."""
    from .voix import reel
    if isinstance(valeur, list):
        return [references(monde, v) for v in valeur]
    if isinstance(valeur, dict):
        return {k: ([reel(monde,x) for x in v] if k in LISTES_REFERENCES and isinstance(v,list) and all(isinstance(x,str) for x in v) else
                    reel(monde, v) if k in CHAMPS_REFERENCES and isinstance(v, str) and not (k == "ancrage" and valeur.get("type") == "parole") else references(monde, v))
                for k, v in valeur.items()}
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
    if not isinstance(presentation,str) or not presentation.strip() or not re.search(
            r'(?<!\w)'+re.escape(presentation)+r'(?!\w)',mots):
        raise ErreurMonde("La présentation ne correspond pas aux mots prononcés.",
                          "presentation : le nom littéral contenu dans la citation du locuteur.")
    from .paroles import _nom_dit
    from .voix import se_nommer
    nom_ = _nom_dit(monde,presentation)
    if nom_:
        se_nommer(monde,qui,auteur,nom_)


def verifier(monde):
    noms = monde.data.get("noms_connus", [])
    assert isinstance(noms,list) and all(isinstance(x,str) for x in noms) and len(set(noms)) == len(noms), "Noms appris invalides"
    personnes = monde.data.get("personnes", {})
    assert isinstance(personnes,dict) and all(isinstance(id,str) and isinstance(e,dict)
        and set(e)=={"n","nom"} and type(e["n"]) is int and e["n"]>0
        and isinstance(e["nom"],str) and 1<=len(e["nom"])<=100 for id,e in personnes.items()), "Désignations invalides"
    assert len({e["n"] for e in personnes.values()}) == len(personnes), "Pseudonymes ambigus"
    refs = monde.data.get("references_personnes", {})
    assert isinstance(refs,dict) and all(isinstance(id,str) and type(n) is int and n>0 for id,n in refs.items()), "Références publiques invalides"
    assert len(set(refs.values())) == len(refs), "Références publiques ambiguës"
