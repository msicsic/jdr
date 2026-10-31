"""Sélecteur terminal des raccourcis comptables publics du web."""
import copy

from .commandes import DescripteurPublic


AIDE_COMPTES = "comptes. Consulter mes comptes et choisir un geste comptable."


class ComptesTerminal:
    """Fige la projection publique, sans recalculer ni compléter ses termes."""

    def __init__(self, public):
        self.public = copy.deepcopy(public)
        self.terminee = False
        self.remboursement = None

    @property
    def accepte_vide(self):
        return self.remboursement is not None

    def rendre(self):
        if self.remboursement is not None:
            return (self.remboursement['nom'] + '\nMontant à rembourser en pièces '
                    f"[Entrée : {self.remboursement['descripteur']['parametres']['montant']}] ; "
                    'montant partiel possible ; annuler pour fermer.')
        lignes = ["Mes comptes — numéro puis Entrée ; annuler pour fermer.",
                  "Le choix est soumis au moteur ; tenter confirme les actes lourds.",
                  *self.public['lignes']]
        for i, choix in enumerate(self.public['choix'], 1):
            d = choix['descripteur']
            references = [d['cible']]
            destinataire = d['parametres'].get('destinataire')
            if destinataire:
                references.append(destinataire)
            lignes.append(f"{i}. {choix['nom']} [{', '.join(references)}]")
        if not self.public['choix']:
            lignes.append("Aucun geste comptable à portée. Annule pour revenir au jeu.")
        return '\n'.join(lignes)

    def saisir(self, texte):
        if self.terminee:
            raise ValueError("Ce formulaire est fermé.")
        texte = texte.strip()
        if texte.casefold() == 'annuler':
            self.terminee = True
            return None
        if self.remboursement is not None:
            if texte and (not texte.isascii() or not texte.isdecimal() or len(texte) > 16
                          or not 0 < int(texte) <= 9007199254740991):
                raise ValueError('Saisis un nombre entier positif de pièces, ou Entrée pour le montant proposé.')
            d = copy.deepcopy(self.remboursement['descripteur'])
            if texte:
                d['parametres']['montant'] = int(texte)
            self.terminee = True
            return DescripteurPublic(d)
        choix = next((x for i, x in enumerate(self.public['choix'], 1)
                      if texte.lstrip('0') == str(i)), None)
        if choix is None:
            raise ValueError("Choisis un seul numéro du formulaire affiché.")
        if choix['descripteur']['parametres'].get('operation') == 'rembourser':
            self.remboursement = choix
            return None
        self.terminee = True
        return DescripteurPublic(copy.deepcopy(choix['descripteur']))
