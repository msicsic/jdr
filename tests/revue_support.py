"""Rapports simulés complets : valeurs sémantiques fixées par chaque oracle de test.

Ce portage de fixtures n'est jamais utilisé par le moteur pour compléter une
revue réelle. Une omission ou un classement illisible doit rester explicite
dans les tests négatifs, qui n'utilisent pas cet auxiliaire.
"""
from donjon.comprehension import champs_types_revue
from donjon.couverture_action import valeur_typee


def rapport(source, conforme=True, motif="", perimetre="sens", ecarts=()):
    valeurs = (champs_types_revue(source.proposition) if hasattr(source, "proposition")
               else source["champs_types"])
    champs = {k: {"conforme": True, "demande": valeur_typee(v), "perimetre": "contrat_type"} for k, v in valeurs.items()}
    for ecart in ecarts:
        champs[ecart["champ"]]["demande"] = ecart["demande"]
        champs[ecart["champ"]]["conforme"] = ecart["demande"] == valeur_typee(valeurs[ecart["champ"]])
    return dict(conforme=conforme, motif=motif, perimetre=perimetre, champs_types=champs)


def porter(ancien, dossier):
    return rapport(dossier, ancien["conforme"], ancien["motif"], ancien.get("perimetre", "sens"),
                   ancien.get("ecarts_types", ()))
