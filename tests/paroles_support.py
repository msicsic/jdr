"""Observer les préparations moteur sans inventer un appel au fournisseur."""
import copy


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
