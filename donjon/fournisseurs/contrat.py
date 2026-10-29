"""Un appel structuré au fournisseur, sans monde, moteur ni accès au MJ."""
from dataclasses import dataclass, field
from typing import Any

from ..monde import ErreurMonde


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
    """État d'une connexion et données de l'appel courant, isolés par instance.

    ``schema_lu`` dit si le modèle reçoit les descriptions du schéma (outil,
    paramètres) ou seulement sa grammaire. Un prompt qui répète le contrat du
    schéma n'est nécessaire que dans le second cas.
    """
    schema_lu = True

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
