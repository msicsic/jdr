"""Aptitudes matérielles communes à l'arbitrage et aux offres d'interface.

Ces prédicats purs ne jugent ni l'accès, ni le consentement, ni la réussite.
Ils ne qualifient jamais une propriété inconnue.
"""
from .force import adapte
from .perception import brule, combustible, recharge


def outil_manipulable(outil):
    return bool(outil) and bool(outil.get("mobile")) and outil.get("integrite", 0) > 0


def cle_adaptee(cible, outil):
    return outil_manipulable(outil) and cible.get("id") in outil.get("ouvre", ())


def outil_crochetage(cible, outil):
    return outil_manipulable(outil) and "crochetage" in outil.get("usages", ())


def impact_objet(cible, outil):
    return (cible.get("type") not in ("personnage", "partie_corps", "motif", "tresor")
            and cible.get("integrite", 0) > 0 and outil_manipulable(outil) and adapte(cible, outil))


def charge_compatible(source, reserve):
    return bool(reserve) and combustible(reserve) and recharge(source, reserve)


def contenant_ouvert(objet):
    return objet.get("type") == "contenant" and bool(objet.get("ouverte"))


def depot_possible(objet, destination):
    # La même conversion que l'opération deplacer : une source se recharge,
    # tandis qu'un contenant ouvert reçoit un objet mobile.
    return (bool(objet.get("mobile"))
            and (charge_compatible(destination, objet) if brule(destination)
                 else contenant_ouvert(destination)))


# Les formulaires nomment une aptitude du moteur, pas une règle par verbe
# recopiée dans chaque interface. Les références admises sont projetées après
# filtrage des seules entités connues du joueur.
APTITUDES = {"cle": cle_adaptee, "crochetage": outil_crochetage,
             "impact": impact_objet, "recharge": charge_compatible, "depot": depot_possible}
