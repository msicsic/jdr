"""Un appel structuré au fournisseur, sans monde, moteur ni accès au MJ."""
from dataclasses import dataclass, field
from typing import Any

from ..monde import ErreurMonde


def lier_modes(schema, charges):
    """Grammaire canonique : chaque mode porte exclusivement sa propre charge.

    Les propriétés communes restent lisibles par les outils de trace/cache.
    Le transport place l'union sous une propriété (OpenAI interdit anyOf à la racine).
    """
    import copy
    resultat = copy.deepcopy(schema)
    branches = []
    for mode in resultat['properties']['mode']['enum']:
        branche = copy.deepcopy(schema)
        branche['properties']['mode'] = {'type': 'string', 'enum': [mode]}
        branche['properties']['texte'] = ({'type': 'string', 'minLength': 1, 'maxLength': 4000}
                                          if mode == 'dialogue' else {'type': 'string', 'enum': ['']})
        branche['properties']['proposition'] = charges[mode]
        branches.append(branche)
    resultat['anyOf'] = branches
    return resultat


@dataclass(frozen=True)
class Demande:
    instructions: str
    entree: dict
    intention: str
    fonction: str
    schema: dict
    modele: str
    effort: str = 'medium'
    timeout: float = 45
    cle_cache: str | None = None
    reflexion: str = 'libre'

    def schema_transport(self):
        from .schema import mutualiser, union_seule
        schema = self.schema
        if 'anyOf' in schema:
            schema = {'type': 'object', 'additionalProperties': False,
                      'properties': {'reponse': union_seule(schema)}, 'required': ['reponse']}
        return mutualiser(schema)

    def decoder(self, arguments):
        # Les autres outils et les voies transitoires gardent leur enveloppe.
        # Une réponse ancienne à plat reste soumise à la même grammaire au MJ.
        if 'anyOf' in self.schema and isinstance(arguments, dict) and set(arguments) == {'reponse'}:
            return arguments['reponse']
        return arguments

    def instructions_transport(self):
        if 'anyOf' not in self.schema:
            return self.instructions
        return self.instructions + ('\nTransport JSON : placer les arguments complets de la fonction '
                                    'dans le champ reponse de l’enveloppe demandée.')


@dataclass(frozen=True)
class Reponse:
    arguments: dict
    brut: Any
    utilisation: dict | None = None
    sortie: list = field(default_factory=list)


class ErreurFournisseur(ErreurMonde):
    """Message affichable et trace technique séparés, y compris sur échec."""
    def __init__(self, message, *, brut=None, utilisation=None, sortie=None, erreur_auth=None):
        super().__init__(message)
        self.brut = brut
        self.utilisation = utilisation
        self.sortie = sortie or []
        self.erreur_auth = erreur_auth


class Fournisseur:
    """État d'une connexion et données de l'appel courant, isolés par instance."""
    def __init__(self):
        self.erreur_auth = None
        self.dernier_brut = None
        self.derniere_utilisation = None
        self.derniere_sortie = []

    def appeler(self, demande: Demande) -> Reponse:
        self.dernier_brut = self.derniere_utilisation = None
        self.derniere_sortie = []
        if self.erreur_auth:
            raise ErreurFournisseur(self.erreur_auth, erreur_auth=self.erreur_auth)
        try:
            return self._appeler(demande)
        except ErreurFournisseur:
            raise
        except ErreurMonde as exc:
            raise ErreurFournisseur(str(exc), brut=self.dernier_brut,
                utilisation=self.derniere_utilisation, sortie=self.derniere_sortie,
                erreur_auth=self.erreur_auth) from None

    def _appeler(self, demande: Demande) -> Reponse:
        raise NotImplementedError

    def fermer(self):
        pass
