"""G18 : réception d'un jugement, sans attester la vérité de sa prévision."""


def formuler(monde, contenu, resolution):
    from .social import phrase
    position = phrase(monde, contenu['evenement'])
    accueil = "Je retiens" if resolution['etat'] == 'crue' else "Je doute de"
    return f"{accueil} ton avis : selon toi, {position}."
