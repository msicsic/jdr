"""Observer les préparations moteur sans inventer un appel au fournisseur."""
import copy


def porter_operations_archive(valeur):
    """Anciennes cartes explicites → vocabulaire actuel, sans changer les mots ni les types.

    Les champs introduits depuis l'archive décrivent des actes absents de
    celle-ci (localisation, mandats…). Le protocole courant les exige à false.
    """
    from donjon.paroles import OPERATIONS
    if isinstance(valeur, list):
        return [porter_operations_archive(v) for v in valeur]
    if isinstance(valeur, dict):
        if "operations_demandees" in valeur:
            assert set(valeur["operations_demandees"]) <= set(OPERATIONS)
        return {k: ({op: v.get(op, False) for op in OPERATIONS}
                    if k == "operations_demandees" else porter_operations_archive(v))
                for k, v in valeur.items()}
    return valeur


class AppelsParole(list):
    def __init__(self):
        super().__init__()
        self.rapports = []
        self.contextes = []

    def preparer(self, *args, **kwargs):
        from donjon.paroles import preparer_parole
        monde, rapport = preparer_parole(*args, **kwargs)
        self.rapports.append(copy.deepcopy(rapport))
        self.contextes.append(monde.contexte())
        return monde, rapport
