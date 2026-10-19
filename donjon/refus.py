"""Des refus qui guident : ce qui est refusé, la règle, et ce qui serait accepté.

Un refus du moteur s'adresse à deux publics. Son message, en mots de la fiction, est lu par
le joueur ; ``attendu`` (``ErreurMonde.attendu``) dit au MJ, en champs et identifiants, ce
qu'une proposition corrigée doit contenir. La boucle de correction du MJ transmet les deux.
"""
from .francais import designer
from .monde import ErreurMonde

LISTE_MAX = 12


def liste(ids, vide="aucun"):
    ids = list(ids)
    if not ids:
        return vide
    return ", ".join(ids[:LISTE_MAX]) + (", …" if len(ids) > LISTE_MAX else "")


def a_portee(m, filtre=None):
    """Identifiants des objets que le joueur peut viser d'ici, triés."""
    return sorted(id for id, o in m.objets.items()
                  if (filtre is None or filtre(o)) and m.accessible(id))


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
    candidats = liste(a_portee(m, filtre))
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
