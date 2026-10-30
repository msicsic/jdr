"""Des refus qui guident : ce qui est refusé, la règle, et ce qui serait accepté.

Un refus du moteur s'adresse à deux publics. Son message, en mots de la fiction, est lu par
le joueur ; ``attendu`` (``ErreurMonde.attendu``) dit au MJ, en champs et identifiants, ce
qu'une proposition corrigée doit contenir. La boucle de correction du MJ transmet les deux.
"""
from .francais import designer
from .monde import ErreurMonde

LISTE_MAX = 12


class ProprieteInconnue(ErreurMonde):
    """Une précondition physique reste à décrire, distincte d'un champ mal choisi.

    Le moteur peut en dire le manque sans inventer un résultat. Une qualification
    automatique est demandée explicitement par le sous-type QualificationRequise.
    """


class RefusDeForme(ErreurMonde):
    """Une proposition du MJ mal formée ou mal dirigée : un champ manquant, une valeur hors de ses
    bornes, la mauvaise action pour ce que demande la saisie. Le monde n'y est pour rien et une autre
    proposition de la même intention pourrait passer : le refus revient au MJ, avec son ``attendu``, et
    ne se montre jamais au joueur comme une impossibilité (``mj``)."""


def liste(ids, vide="aucun"):
    ids = list(ids)
    if not ids:
        return vide
    return ", ".join(ids[:LISTE_MAX]) + (", …" if len(ids) > LISTE_MAX else "")


def cibles(m, ids=None, filtre=None):
    """Références publiques des seules entités désignables, pour tout attendu de cible.

    Les contraintes du geste fournissent les candidats ; la connaissance du joueur
    borne toujours la liste avant projection et avant la limite d'affichage.
    """
    from .noms import reference
    from .voix import reel, designation
    def publique(id):
        # Une appellation connue ne relie pas forcément la voix entendue à son corps.
        voix = designation(m, id) if m.objets[id]["type"] == "personnage" else id
        return voix if voix != id else reference(m, id)
    ids = m.objets if ids is None else ids
    ids = (reel(m, id) for id in ids)
    return liste(sorted({publique(id) for id in ids if isinstance(id, str) and id in m.objets
                         and (filtre is None or filtre(m.objets[id])) and m.designable(id)}),
                 vide="aucune cible de ce nom n'est désignable ici")


def portes_avec_usage(m, usage):
    """Objets en main, intacts, dotés de cet usage : les outils qu'une proposition peut nommer."""
    return sorted(id for id, o in m.objets.items()
                  if o["lieu"] == "joueur" and usage in o.get("usages", []) and o.get("integrite", 1) > 0)


def _contenant_ferme(m, id):
    lieu = m.objets[id]["lieu"]
    while lieu in m.objets:
        parent = m.objets[lieu]
        if parent["type"] == "contenant" and not parent.get("ouverte"):
            return parent
        lieu = parent["lieu"]
    return None


def inaccessible(m, id, champ="cible", filtre=None):
    """Pourquoi ``id`` ne peut pas être visé d'ici : inconnu, absent, enfermé, ou invisible."""
    candidats = cibles(m, filtre=filtre)
    valables = f"{champ} : un identifiant visé d'ici, parmi {candidats}."
    if not id:
        return ErreurMonde("Il manque ce que vise ce geste.", f"{champ} est vide ; {valables}")
    o = m.objets.get(id)
    if o is None:
        return ErreurMonde("Tu ne vois rien de tel ici.",
                           f"« {id} » n'est pas un identifiant connu ; {valables}")
    ferme = _contenant_ferme(m, id)
    if ferme is not None and m.present_physique(ferme["id"]):
        return ErreurMonde(designer(o, debut=True) + " est dans " + designer(ferme) + ", fermé.",
                           f"ouvre d'abord {ferme['id']} (action ouvrir, ou une étape ouvrir dans composer).")
    if not m.present_physique(id):
        return ErreurMonde(designer(o, debut=True) + " n'est pas ici.",
                           f"{id} n'est pas dans la salle du joueur ; {valables}")
    return ErreurMonde("Tu ne distingues pas " + designer(o) + " d'ici.",
                       f"{id} n'est pas perçu (obscurité ou ligne de vue) ; allume une source ou "
                       f"vise ce qui est perçu : {candidats}.")


def perception(m, id, champ="cible", acceptes=None, valeurs=()):
    """Une seule cause sensorielle, déterminée par le monde avant tout récit."""
    o = m.objets[id]
    designation = "cette personne" if o["type"] == "personnage" else "cet objet"
    if acceptes is None:
        acceptes = [id for id in m.objets if m.visible(id)]
    valables = f"{champ} : reçu {id!r} hors de vue ; acceptés : {cibles(m, acceptes)}."
    if valeurs:
        valables += f" Ou {liste(map(repr, valeurs))}."
    from .rendu import non_perception
    constat = non_perception(m, id)
    if constat:
        return ErreurMonde(constat, f"{champ}={id!r} : vue requise ; {valables}")
    return ErreurMonde("Tu n'as pas " + designation + " en vue d'ici.",
                       f"{champ}={id!r} : vue requise (champ et ligne de vue) ; {valables}")


# Les refus d'audit : contrôle narratif (contrôles déterministes et verdicts de l'auditeur),
# contre-revue des ajouts et des capacités. Même contrat qu'un refus du moteur : ``motif`` est la
# règle en mots de la fiction ; ``attendu`` dit au MJ où (partie, segment), ce qui a été reçu (la
# phrase ou la valeur fautive, citée exactement) et ce qui serait accepté. Une cause par refus.
# Aucun des deux ne s'affiche au joueur : un texte refusé n'est jamais montré.

CITATION_MAX = 200


def citer(texte, longueur=CITATION_MAX):
    """« texte », abrégé au-delà de ``longueur`` caractères."""
    texte = " ".join(str(texte).split())
    if len(texte) > longueur:
        texte = texte[:longueur - 1].rstrip() + "…"
    return f"« {texte} »"


def lieu_audit(partie="texte", segment=None):
    """Où est la faute : la partie contrôlée (texte, justification, description, qualification) et,
    s'il y a lieu, l'indice du segment, tel que l'auditeur l'a reçu."""
    return partie + (f", segment {segment}" if segment is not None else "")


def attendu_audit(lieu, recu, accepte, verdict=None):
    """``lieu`` : où ; ``recu`` : la phrase ou la valeur fautive ; ``accepte`` : ce qui passerait.
    ``verdict`` : la catégorie d'un auditeur sémantique et son motif, donnés pour ce qu'ils sont, un
    jugement, sans plus de certitude."""
    juge = ""
    if verdict:
        categorie, motif = verdict if isinstance(verdict, tuple) else (verdict, "")
        juge = f" ; selon l'auditeur (verdict {categorie})" + (f" : {citer(motif)}" if motif.strip() else "")
    return f"{lieu}, reçu {citer(recu) if recu else 'un texte vide'}{juge} ; accepté : {accepte}"


def audit(motif, accepte, *, partie="texte", segment=None, texte="", recu=None, verdict=None, lieu=None):
    """Un refus d'audit, tel que la boucle de correction le transmet au MJ (``controle_narratif``) :
    ``texte`` est le passage contrôlé (le segment), ``recu`` ce qui y est fautif s'il n'est qu'une
    partie (un nom, une citation)."""
    return {"partie": partie, "segment": segment, "texte": texte, "motif": motif,
            "attendu": attendu_audit(lieu or lieu_audit(partie, segment),
                                     texte if recu is None else recu, accepte, verdict)}


def audit_illisible(motif, *, partie="texte", texte="", lieu=None):
    """Le contrôle n'a pas pu lire son propre rapport : rien n'est reproché au texte."""
    return {"partie": partie, "segment": None, "texte": texte, "motif": motif,
            "attendu": f"{lieu or partie} : aucune phrase n'est en cause, le contrôle n'a pas pu lire son "
                       f"propre rapport ; accepté : la même réponse, renvoyée telle quelle, ou une autre."}


class RapportIllisible(ErreurMonde):
    """Le rapport d'un auditeur (contrôle narratif, portée, capacités, contre-revue) est mal formé :
    une faute de l'auditeur, pas de la réponse contrôlée."""


def depuis_refus(exc, partie, lieu=None):
    """Un refus du moteur levé pendant un audit (proposition mal formée, ancrage inconnu) : son message
    et son ``attendu``, rattachés à la partie contrôlée. Sans ``attendu``, la règle seule."""
    return {"partie": partie, "segment": None, "texte": "", "motif": str(exc),
            "attendu": f"{lieu or partie} : " + (getattr(exc, "attendu", "") or str(exc))}
