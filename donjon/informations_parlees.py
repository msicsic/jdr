"""G16 : mots d'information depuis l'issue, sans consulter la vérité cachée."""


def formuler(monde, auteur, contenu, resolution):
    from .francais import designer, lieu
    from .paroles import _nom, _ouidire
    type_ = contenu['type']
    etat = resolution['etat']
    if type_ == 'qui':
        return (f"Je m'appelle {resolution['nom']}." if etat == 'nomme'
                else "Je refuse de te dire mon nom.")
    if type_ == 'nom':
        nom = resolution['nom']
        return {'connu': ("Je sais déjà qui tu es." if contenu['sujet'] == 'joueur'
                          else f"Je sais que tu n'es pas {nom}."),
                'demasque': f"Je sais que tu n'es pas {nom}.",
                'doute': f"Je doute que tu sois {nom}.",
                'crue': f"Je te crois quand tu dis être {nom}."}[etat]
    refus = {'qui_va_la': "Qui va là ?", 'mefiance': "Je refuse de te répondre : je ne te fais pas confiance.",
             'rancune': "Je refuse de te répondre : je t'en veux encore."}
    if etat in refus:
        return refus[etat]
    if type_ == 'ressource':
        if etat == 'rien':
            return "Je n'en ai pas."
        biens = []
        for bien, endroit in resolution['dit']:
            if endroit == auteur:
                ou = ' sur moi'
            elif endroit in monde.data['salles']:
                ou = ' dans ' + lieu(monde.data['salles'][endroit])
            elif endroit in monde.objets:
                ou = ' dans ' + designer(monde.objets[endroit])
            else:
                ou = ''
            biens.append(designer(monde.objets[bien]) + ou)
        return "J'ai " + ' et '.join(biens) + '.'
    if type_ == 'localisation':
        sujet = _nom(monde, contenu['sujet'])
        if etat == 'rien':
            return f"Je ne sais pas où se trouve {sujet}."
        c = resolution['croyance']
        preuve = {'vu': "J'ai vu", 'entendu': "J'ai entendu"}.get(c['source'], "J'ai appris")
        origine = _ouidire(monde, c['source'], moi=True)
        if c.get('origine') and c['origine']['minute'] != c['minute']:
            origine += f" (ce renseignement remonte à la minute {c['origine']['minute']})"
        return (f"{preuve} à la minute {c['minute']} que {sujet} se trouvait dans "
                f"{lieu(monde.data['salles'][resolution['dit'][0][1]])}{origine}.")
    raise AssertionError(f'Information non portée : {type_}')
