"""Adaptateurs de fournisseurs ; aucune règle du jeu dans cette couche."""
from .contrat import Demande, Reponse, Fournisseur, ErreurFournisseur


def creer(connexion):
    if connexion in ('api', 'chatgpt'):
        from .openai import OpenAI
        return OpenAI(chatgpt=connexion == 'chatgpt')
    if connexion == 'anthropic':
        from .anthropic import Anthropic
        return Anthropic()
    if connexion == 'mimo':
        from .mimo import MiMo
        return MiMo()
    if connexion == 'local':
        from .local import Local
        return Local()
    raise ValueError('Connexion fournisseur inconnue : ' + str(connexion))
