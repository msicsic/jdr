"""Dialogues situés, offres et engagements persistants ; aucune écriture directe du LLM."""
from .emissions import pnj as emissions_pnj, publiques as emissions_publiques
from .francais import quantite
from . import agendas
import copy

from .refus import cibles
from .monde import ErreurMonde, normaliser
from .francais import designer, groupe_nominal
from .esprits import dernier_son


OPERATIONS = ("discuter", "proposer", "negocier", "accepter", "refuser")
GESTE_INFORMATION = "information"
AIDE_INFORMATION = "information. Demander ou transmettre une information."
AIDE_AVIS = "avis. Donner un avis sur la menace d'eau."


def formulaires_information():
    """Actes déjà portés par le moteur ; aucune aptitude sociale présumée."""
    return [
        {"acte": "qui", "libelle": "Demander qui parle", "champs": []},
        {"acte": "localisation", "libelle": "Demander où est une personne…",
         "champs": [{"champ": "sujet", "libelle": "Personne", "choix": "personnes"}]},
        {"acte": "affirmation", "libelle": "Dire où se trouve…",
         "champs": [{"champ": "sujet", "libelle": "Sujet", "choix": "sujets"},
                    {"champ": "valeur", "libelle": "Lieu annoncé", "choix": "lieux"}]},
        {"acte": "ressource", "libelle": "Demander si l'autre possède…",
         "champs": [{"champ": "sujet", "libelle": "Ressource recherchée", "choix": "ressources"}]},
    ]


def information_publique(monde):
    """Identités et désignations connues, sans position ni croyance d'autrui.

    Les lieux sont des choix d'assertion : ils ne préremplissent jamais la
    position du sujet. Le joueur peut aussi annoncer une localisation fausse.
    """
    from .paroles import _connu_du_joueur, contexte_fige, RESSOURCES_DEMANDEES
    from .noms import public, reference, PERSONNES
    from .voix import nom_pour_joueur
    sujets, personnes, ressources = [], [], []
    with contexte_fige():
        for id, o in monde.objets.items():
            if not _connu_du_joueur(monde, id):
                continue
            entree = {"id": reference(monde, id), "nom": (nom_pour_joueur(monde, id)
                      if o["type"] == "personnage" else public(monde, designer(o)))}
            sujets.append(entree)
            if o["type"] == "personnage":
                personnes.append(entree)
            elif o["type"] not in (*PERSONNES, "partie_corps"):
                ressources.append(entree)
        lieux = [{"id": id, "nom": s["nom"]} for id, s in monde.data["salles"].items()
                 if _connu_du_joueur(monde, id)]
    return {"destinataires": [{"id": id, "nom": x["nom"]} for id, x in interlocuteurs(monde).items()],
            "sujets": [{"id": "joueur", "nom": monde.joueur["nom"]}, *sujets],
            "personnes": [{"id": "joueur", "nom": monde.joueur["nom"]}, *personnes],
            "lieux": lieux,
            "ressources": [*ressources, *({"id": b, "nom": n} for b, n in RESSOURCES_DEMANDEES.items())]}


def formulaires_avis():
    """Le prédicat d'avis déjà évaluable par le moteur, sans vérité préremplie."""
    return [{"acte": "avis", "libelle": "Donner un avis sur la menace d'eau",
             "champs": [{"champ": "sujet", "libelle": "Lieu de l'avis", "choix": "lieux"},
                        {"champ": "valeur", "libelle": "Prévision", "choix": "valeurs"}]}]


def avis_publics(monde):
    """Seuls des noms publics connus ; ni prévision calculée ni croyance privée."""
    from .paroles import _connu_du_joueur, contexte_fige
    with contexte_fige():
        lieux = [{"id": id, "nom": s["nom"]} for id, s in monde.data["salles"].items()
                 if _connu_du_joueur(monde, id)]
    return {"destinataires": [{"id": id, "nom": x["nom"]} for id, x in interlocuteurs(monde).items()],
            "lieux": lieux,
            "valeurs": [{"id": "oui", "nom": "L'eau menace ce lieu, selon moi"},
                        {"id": "non", "nom": "L'eau épargne ce lieu, selon moi"}]}


class InformationTerminal:
    """Formulaire numéroté sur les mêmes paramètres publics que le web."""

    catalogue = staticmethod(formulaires_information)
    titre = "Information"
    indications = ("Le dernier choix transmet la parole ; une affirmation demande confirmation.",
                   "Demander où est un objet reste indisponible.")

    def __init__(self, public):
        self.public = copy.deepcopy(public)
        self.formulaires = self.catalogue()
        self.destinataire = None
        self.formulaire = None
        self.valeurs = []
        self.terminee = False

    @property
    def champ(self):
        return self.formulaire["champs"][len(self.valeurs)]

    def choix(self):
        if self.destinataire is None:
            return [(x["id"], x["nom"] + " [" + x["id"] + "]")
                    for x in self.public["destinataires"]]
        if self.formulaire is None:
            return [(f, f["libelle"]) for f in self.formulaires]
        return [(x["id"], x["nom"] + " [" + x["id"] + "]")
                for x in self.public[self.champ["choix"]]]

    def rendre(self):
        lignes = [self.titre + " — numéro puis Entrée ; annuler pour fermer.", *self.indications]
        if self.destinataire:
            lignes.append("À qui parler : " + self.destinataire[1])
        if self.formulaire:
            lignes.append(self.formulaire["libelle"])
            lignes.extend(c["libelle"] + " : " + v[1]
                          for c, v in zip(self.formulaire["champs"], self.valeurs))
        lignes.append("À qui parler :" if self.destinataire is None else
                      "Acte d'information :" if self.formulaire is None else self.champ["libelle"] + " :")
        choix = self.choix()
        lignes.extend(f"{i}. {libelle}" for i, (_, libelle) in enumerate(choix, 1))
        if not choix:
            lignes.append("Aucun choix connu à portée. Annule pour revenir au jeu.")
        return "\n".join(lignes)

    def saisir(self, texte):
        from .commandes import DescripteurPublic
        if self.terminee:
            raise ValueError("Ce formulaire est fermé.")
        texte = texte.strip()
        if texte.casefold() == "annuler":
            self.terminee = True
            return None
        selection = next(((v, l) for i, (v, l) in enumerate(self.choix(), 1)
                          if texte.lstrip("0") == str(i)), None)
        if selection is None:
            raise ValueError("Choisis un seul numéro du formulaire affiché.")
        if self.destinataire is None:
            self.destinataire = selection
        elif self.formulaire is None:
            self.formulaire = selection[0]
        else:
            self.valeurs.append(selection)
        if self.formulaire is None or len(self.valeurs) < len(self.formulaire["champs"]):
            return None
        self.terminee = True
        return DescripteurPublic({"geste": GESTE_INFORMATION, "cible": self.destinataire[0],
            "parametres": {"acte": self.formulaire["acte"],
                           **{c["champ"]: v[0] for c, v in zip(self.formulaire["champs"], self.valeurs)}}})


class AvisTerminal(InformationTerminal):
    """Même sélecteur public ; le catalogue d'avis fixe les champs disponibles."""

    catalogue = staticmethod(formulaires_avis)
    titre = "Avis"
    indications = ("Le dernier choix prépare l'avis ; tenter le confirme, annuler l'abandonne.",)


def parole_information(monde, d):
    """Descripteur U-D → contenu canonique, sans analyse de texte.

    Rejoué à chaque préparation de transaction, aussi après un aperçu U-C.
    Seuls les choix publics actuels peuvent devenir une parole.
    """
    if (not isinstance(d, dict) or set(d) != {"geste", "cible", "parametres"}
            or d["geste"] != GESTE_INFORMATION or not isinstance(d["cible"], str)):
        raise ErreurMonde("Ce choix d'information est mal formé.",
                          f"descripteur : reçu {d!r} ; attendu geste=information, cible publique, parametres.")
    p = d["parametres"]
    if not isinstance(p, dict) or not all(isinstance(v, str) and len(v) <= 1000 for v in p.values()):
        raise ErreurMonde("Les paramètres de cette parole sont mal formés.",
                          f"descripteur.parametres : reçu {p!r} ; attendu dictionnaire de chaînes.")
    formulaires = [*formulaires_information(), *formulaires_avis()]
    f = next((f for f in formulaires if f["acte"] == p.get("acte")), None)
    if not f:
        raise ErreurMonde("Cet acte d'information n'est pas proposé.",
                          f"parametres.acte : reçu {p.get('acte')!r} ; attendu {[f['acte'] for f in formulaires]}.")
    champs = {"acte", *(c["champ"] for c in f["champs"])}
    if set(p) != champs:
        raise ErreurMonde("Ce choix d'information est incomplet ou comporte un paramètre inconnu.",
                          f"descripteur.parametres : reçu {sorted(p)} ; attendu {sorted(champs)}.")
    choix = avis_publics(monde) if p["acte"] == "avis" else information_publique(monde)
    if d["cible"] not in {x["id"] for x in choix["destinataires"]}:
        raise ErreurMonde("Tu ne perçois plus cet interlocuteur pour lui parler.",
                          f"descripteur.cible : reçu {d['cible']!r} ; attendu {[x['id'] for x in choix['destinataires']]}.")
    noms = {}
    for c in f["champs"]:
        candidats = {x["id"]: x["nom"] for x in choix[c["choix"]]}
        if p[c["champ"]] not in candidats:
            raise ErreurMonde("Ce choix ne désigne plus un sujet ou un lieu connu de Corvus.",
                              f"parametres.{c['champ']} : reçu {p[c['champ']]!r} ; attendu {sorted(candidats)}.")
        noms[c["champ"]] = candidats[p[c["champ"]]]
    acte = p["acte"]
    replique = ("Qui es-tu ?" if acte == "qui" else
                f"Où se trouve {noms['sujet']} ?" if acte == "localisation" else
                f"Possèdes-tu ceci : {noms['sujet']} ?" if acte == "ressource" else
                f"Selon moi, l'eau {'menace' if p['valeur'] == 'oui' else 'ne menace pas'} ce lieu : {noms['sujet']}." if acte == "avis" else
                f"La localisation que je t'annonce pour {noms['sujet']} : {noms['valeur']}.")
    from .voix import reel
    sujet = reel(monde, p.get("sujet", "")) if acte == "ressource" else p.get("sujet", "")
    from .commandes import consultation_locale
    from .contrats_consultation import CONSULTATIONS
    contenu = (consultation_locale(acte, sujet) if acte in CONSULTATIONS else
               {"type": acte, "sujet": sujet,
                "attribut": "lieu" if acte == "affirmation" else "menace",
                "valeur": p.get("valeur", "")})
    return {"personnage": d["cible"], "replique": replique,
            "contenu": [contenu]}


def preparer_information(monde, descripteur):
    return preparer_direct(monde, descripteur)


def preparer_direct(monde, descripteur):
    """Une seule entrée commune vers les transactions de parole et U-C."""
    from .consentement import preparer
    from .paroles import annonce
    d = copy.deepcopy(descripteur.contenu)
    if (isinstance(d, dict) and isinstance(d.get('parametres'), dict)
            and d['parametres'].get('acte') == 'compte'
            and d['parametres'].get('operation') == 'payer'):
        p = conversation_compte(monde, d)
        r = {'mode': 'dialogue', 'texte': 'Offre soumise au moteur.', 'faits': [], 'proposition': None,
             '_texte_moteur': True, '_transactions': [{'type': 'conversation_pnj',
                 'revision': monde.data['revision'], 'proposition': {**p, '_adresse': d}}]}
        dossier = preparer(monde, r, 'Geste direct')
        compte = dossier.compte_parle()
        if compte:
            dossier.reponse.update(compte)
        return dossier
    p = {**parole_directe(monde, d), "_adresse": d}
    r = {"mode": "dialogue", "texte": "Parole enregistrée.", "faits": [], "proposition": None,
         "_texte_moteur": True,
         "_transactions": [{"type": "parole", "revision": monde.data["revision"], "proposition": p}]}
    dossier = preparer(monde, r, "Geste direct")
    compte = dossier.compte_parle()
    if compte:
        dossier.reponse.update(compte)
    dossier.reponse["_prefixe_moteur"] = annonce(monde, dossier.rapports[0])
    return dossier


def parole_directe(monde, d):
    if (isinstance(d, dict) and d.get('geste') == GESTE_INFORMATION
            and isinstance(d.get('parametres'), dict) and d['parametres'].get('acte') == 'compte'):
        return parole_compte(monde, d)
    if isinstance(d, dict) and d.get('geste') == 'accord':
        from .accords_publics import parole_accord
        return parole_accord(monde, d)
    return parole_information(monde, d)


def candidats_contrat(monde, projection):
    """Référence K0 : achats de parts et tâches publiques, sans état mental privé.

    Le formulaire E5 paie en pièces : pas de troc ni de clause supplémentaire.
    Une tâche découle d'un état actuellement vu ; aucune faim ou pulsion cachée
    n'est consultée pour choisir les termes ou leur prix de départ.
    """
    from .echanges import candidat_proposition, PRIX_SANS_PRIX
    from .biens import prix, proprietaire
    from .voix import reel
    from .noms import public
    from .perception import faible
    from .esprits import preuve_possession
    from . import memoire
    import json
    candidats, visibilite = [], {}
    for qui in sorted(projection['destinataires'], key=lambda x: x['id']):
        for prestation in sorted(projection['prestations'], key=lambda x: json.dumps(x['terme'], sort_keys=True)):
            terme = prestation['terme']
            if terme['type'] not in ('part', 'tache'):
                continue  # K0 reste la référence prestation contre pièces.
            id = reel(monde, terme.get('objet') or terme['condition']['objet'])
            # Connaître un nom ne révèle pas la possession ou l'état courant.
            if id not in visibilite:
                visibilite[id] = monde.visible(id)
            if not visibilite[id]:
                continue
            if terme['type'] == 'tache':
                c, o = terme['condition'], monde.objets[id]
                manque = (c.get('allume') and (not o.get('allume') or faible(o))
                          or c.get('verrouillee') and o.get('verrouillee') is False)
                if not manque:
                    continue
                montant = PRIX_SANS_PRIX
            else:
                # Une ressource vue au sol n'en révèle pas le propriétaire.
                # Utiliser le même constat de possession que la perception,
                # ou la preuve déjà retenue par Corvus, sans créer de registre.
                possession = (preuve_possession(monde, id) or
                              (memoire.fait_brut(monde, 'joueur', id, 'lieu') or {}).get('possession', {}))
                if possession.get('proprietaire') != reel(monde, qui['id']):
                    continue
                # Préfiltre identique au contrôle des droits sur copie ; il
                # évite un devis jetable pour chaque propriétaire impossible.
                if proprietaire(monde, id) != reel(monde, qui['id']):
                    continue
                montant = prix(monde, id, part=True) or PRIX_SANS_PRIX
            if montant > projection['or']:
                continue
            demande = copy.deepcopy(terme)
            if 'objet' in demande:
                demande['objet'] = id
            else:
                demande['condition'] = {k: reel(monde, v) if isinstance(v, str) else v
                                        for k, v in demande['condition'].items()}
            if not candidat_proposition(monde, reel(monde, qui['id']), demande, montant):
                continue
            initial = {'destinataire': qui['id'], 'prestation': copy.deepcopy(terme),
                       'prix': montant, 'sans_limite': True}
            if any(x['initial'] == initial for x in candidats):
                continue
            candidats.append({'nom': f"{qui['nom']} — {prestation['nom']} ; "
                               f"{quantite(montant, 'pièce')} à payer maintenant ; sans limite négociée",
                              'initial': initial})
    return public(monde, candidats)


def comptes_publics(monde):
    """Choix sur les comptes de Corvus ; aucune bourse ni dette entre tiers.

    Les termes transportés sont aussi ceux du libellé. Ils servent de garde de
    péremption, jamais d'autorisation de paiement ou de preuve de possession.
    """
    from .biens import comptes_joueur, dettes, prets, compte
    from .noms import public, reference
    from .voix import reel
    from .propositions import en_mots
    choix = []

    def ajouter(nom, d):
        choix.append({'nom': nom, 'descripteur': d})

    # Une obligation connue reste proposée même si le créancier est absent.
    # Le moteur revalide la présence et les fonds à réception et à confirmation.
    from .voix import personne_pour_joueur
    soldes = {}
    for dette in dettes(monde):
        if dette['de'] == 'joueur' and dette['a'] in monde.objets:
            soldes[dette['a']] = soldes.get(dette['a'], 0) + dette['montant']
    for id, montant in soldes.items():
        ref = reference(monde, id)
        nom = personne_pour_joueur(monde, id, court=True)[0]
        ajouter(f'Rembourser — débiteur : toi ; créancier : {nom} ; solde connu : {quantite(montant, "pièce")}',
                {'geste': GESTE_INFORMATION, 'cible': ref,
                 'parametres': {'acte': 'compte', 'operation': 'rembourser',
                                'compte': compte('joueur', ref, montant=montant), 'montant': montant}})

    for ref, personne in interlocuteurs(monde).items():
        id, nom = reel(monde, ref), personne['nom']
        montant = sum(d['montant'] for d in dettes(monde, connues_de='joueur') if d['de'] == id)
        c = compte(ref, 'joueur', montant=montant, etat='du' if montant else 'absent')
        for op, libelle in (('question', 'Demander ce que cette personne me doit'),
                            *([('reclamer', 'Réclamer le solde dû')] if montant else [])):
            ajouter(f'{libelle} — {nom} ; créancier : toi ; solde connu : {quantite(montant, "pièce")}',
                    {'geste': GESTE_INFORMATION, 'cible': ref,
                     'parametres': {'acte': 'compte', 'operation': op, 'compte': c}})
        for p in prets(monde):
            if p['objet'] not in monde.objets:
                continue
            if p['a'] == 'joueur' and p['de'] == id:
                objet = reference(monde, p['objet'])
                c = compte('joueur', ref, objet, 1)
                ajouter(f'Restituer le prêt — débiteur : toi ; créancier : {nom} ; {public(monde, designer(monde.objets[p["objet"]]))}',
                    {'geste': 'remettre', 'cible': objet,
                     'parametres': {'destinataire': ref, 'compte': c}})
        for identifiant, o in monde.data.get('offres_joueur', {}).items():
            if o['de'] != id or o['statut'] != 'propose' or o['demande']['type'] != 'pieces':
                continue
            termes = public(monde, {'offre': identifiant, 'debiteur': 'joueur', 'creancier': ref,
                                    'demande': o['demande'], 'contrepartie': o['contrepartie']})
            ajouter(public(monde, f'Régler l’offre de {nom} — tu paies {en_mots(monde, o["demande"])} ; '
                           f'tu reçois {en_mots(monde, o["contrepartie"])} ; après accord moteur'),
                    {'geste': GESTE_INFORMATION, 'cible': ref,
                     'parametres': {'acte': 'compte', 'operation': 'payer', 'compte': termes}})
    return {'lignes': comptes_joueur(monde), 'choix': choix}


def valider_choix_compte(monde, d):
    import json
    candidat = d
    if (isinstance(d, dict) and isinstance(d.get('parametres'), dict)
            and d['parametres'].get('operation') == 'rembourser'):
        montant = d['parametres'].get('montant')
        if type(montant) is not int or montant <= 0:
            raise ErreurMonde('Il faut rembourser un nombre entier positif de pièces.',
                              f'parametres.montant={montant!r} ; attendu entier strictement positif.')
        # Seul le versement est éditable ; le compte public reste strictement figé.
        candidat = copy.deepcopy(d)
        c = candidat['parametres'].get('compte')
        if isinstance(c, dict):
            candidat['parametres']['montant'] = c.get('montant')
    try:
        recu = json.dumps(candidat, sort_keys=True, allow_nan=False)
    except (TypeError, ValueError):
        recu = None
    if not any(recu == json.dumps(x['descripteur'], sort_keys=True, allow_nan=False)
               for x in comptes_publics(monde)['choix']):
        raise ErreurMonde('Ce choix de compte a changé ou ne fait plus partie de tes comptes publics.',
                          f'descripteur : reçu {d!r} ; attendu un choix exact de comptes_publics(monde).')
    return d['parametres']['compte']


def parole_compte(monde, d):
    from .voix import reel
    from .biens import dues
    from .noms import public
    c = valider_choix_compte(monde, d)
    op = d['parametres']['operation']
    if op == 'rembourser':
        from .biens import rembourser_dette
        montant = d['parametres']['montant']
        # Même contrat que le 388, y compris ses refus avant les gardes de parole.
        # L'essai sur copie ne publie rien ; U-C rejoue l'acte à la confirmation.
        rembourser_dette(monde.copier(), 'joueur', reel(monde, d['cible']), montant)
        return {'personnage': d['cible'],
                'replique': f'Je te rembourse {quantite(montant, "pièce")} sur ma dette.',
                'contenu': [{'type': 'rembourser', 'montant': str(montant)}]}
    if op == 'payer':
        raise ErreurMonde('Cette offre attend le règlement par le moteur.',
                          'parametres.operation=payer : attendu preparer_direct puis conversation_pnj accepter.')
    if op == 'reclamer' and not c['objet']:
        montant = sum(x['montant'] for x in dues(monde, reel(monde, d['cible']), 'joueur'))
        if montant != c['montant']:
            raise ErreurMonde('Le solde doit être revérifié avant de le réclamer.',
                              f'compte.montant : reçu {c["montant"]} ; attendu solde actuel {montant}.')
    objet = c['objet']
    mots = ('Que me dois-tu en pièces ?' if op == 'question' else
            f'Je te réclame {designer(monde.objets[reel(monde, objet)])} que je t’ai prêté.' if objet else
            f'Je te réclame le solde de {quantite(c["montant"], "pièce")} que tu me dois.')
    from .commandes import consultation_locale
    return {'personnage': d['cible'], 'replique': public(monde, mots),
            'contenu': [consultation_locale('reclamer', objet)]}


def conversation_compte(monde, d):
    c = valider_choix_compte(monde, d)
    if d['parametres'].get('operation') != 'payer':
        raise ErreurMonde('Ce choix ne règle pas une offre.',
                          f'parametres.operation : reçu {d["parametres"].get("operation")!r} ; attendu payer.')
    nom = next(x['nom'] for x in comptes_publics(monde)['choix'] if x['descripteur'] == d)
    return {'personnage': d['cible'], 'sujet': nom,
            'operation': 'accepter', 'mission': c['offre'], 'montant_demande': 0}


SCHEMA_CONVERSATION = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "personnage": {"type": "string"}, "sujet": {"type": "string"},
        "operation": {"type": "string", "enum": list(OPERATIONS)},
        "mission": {"type": "string"}, "montant_demande": {"type": "integer"},
    },
    "required": ["personnage", "sujet", "operation", "mission", "montant_demande"],
}


def installer(monde):
    d = monde.data
    agendas.installer_contrats(monde)
    d.setdefault("dialogues_pnj", {})
    d.setdefault("finances_pnj", {})
    d.setdefault("missions", {})


def interlocuteurs(monde):
    """Ceux à qui le joueur peut parler, sous le nom qu'il leur connaît (``voix.designation``).

    On parle à qui l'on perçoit : qu'on voit, ou dont on vient d'entendre la voix (une parole nette
    parvenue au joueur pendant son dernier geste : ``ecoute.retenir``), si chacun saisit les mots de
    l'autre (``ouie.s_entendent`` : distance, passages, portes). Qui se tait dans son dos ou dans le
    noir n'est pas là pour lui, ni pour le MJ. Une voix qu'il ne sait à qui prêter est un
    interlocuteur comme un autre, désigné « voix_<n> » : rien de ce qu'il en reçoit ne la trahit,
    seulement ce qu'elle prétend, d'où elle vient et le genre où elle parle d'elle-même (``voix.genre``,
    ce que ses mots font entendre) ; ``reels`` rend les personnages."""
    from .corps import conscient
    from .ouie import s_entendent
    from .voix import designation, genre, nom_pour_joueur
    resultat = {}
    for id, o in monde.objets.items():
        if not (o["type"] == "personnage" and conscient(monde, id) and conscient(monde)):
            continue
        if not (monde.visible(id) or id in monde.data.get("entendus", []) and s_entendent(monde, id, "joueur")):
            continue
        cle = designation(monde, id)
        if cle != id:
            resultat[cle] = {"nom": nom_pour_joueur(monde, id), "voix_inconnue": cle.startswith("voix_"), "personne_inconnue": cle.startswith("personne_"), "entendue": _d_ou(monde, id),
                             "genre": genre(monde, id)}
            continue
        resultat[id] = {"nom": o["nom"], **copy.deepcopy(monde.data["dialogues_pnj"].get(id, {})),
                        "dernier_son_entendu": dernier_son(monde, id),
                        "paroles_entendues": copy.deepcopy([
                            p for p in emissions_publiques(monde, emissions_pnj(monde)) if id in p["auditeurs"]][-4:]),
                        "refuse_ventes_apres_vol": bool(o.get("refuse_ventes_apres_vol")),
                        "signes": []}
    from .voix import reel
    for cle, contenu in resultat.items():
        offres = [{**copy.deepcopy(o), 'de': cle} for o in monde.data.get('offres_joueur', {}).values()
                  if o['de'] == reel(monde, cle) and o['statut'] == 'propose']
        if offres:
            contenu['offres'] = offres
    return resultat


def _d_ou(monde, id):
    """D'où le joueur a entendu cette voix en dernier : « tout près », « au nord »…"""
    from .ecoute import _lieu
    dernier = next((b for b in reversed(monde.data.get("bruits", [])) if b["auteur"] == id), None)
    return _lieu(dernier["par"]) if dernier else "tout près"


def reels(monde):
    """Les personnages derrière ``interlocuteurs`` : leurs identifiants, voix inconnues comprises."""
    from .voix import reel
    return [reel(monde, d) for d in interlocuteurs(monde)]


def contrats_publics(monde):
    return {id: {**copy.deepcopy(e), "donneur": monde.data["missions"][id]["donneur"],
                 "condition": monde.data["missions"][id]["condition"]}
            for id, e in agendas.contrats(monde).items()}


def missions_discutables(monde):
    presents = interlocuteurs(monde)
    return {id: _mission_publique(monde, id)
            for id, m in monde.data["missions"].items() if m["donneur"] in presents}


def _mission_publique(monde, id):
    m = monde.data["missions"][id]
    return {"nom": m["nom"], "donneur": m["donneur"], "condition": m["condition"],
            "lieu_du_donneur": monde.objets[m["donneur"]]["lieu"], "offre": offre_mission(monde, id)}


def offre_mission(monde, id):
    from .propositions import offre
    mission = monde.data["missions"].get(id)
    if mission is None:
        return None  # Un marché public n'est pas une mission à prime.
    accord = agendas.contrats(monde).get(id, {})
    if accord.get("statut") in ("paye", "refuse"):
        return None
    montant = accord.get("montant", mission["prime_base"])
    if disponible(monde, mission["donneur"], sauf=id) < montant:
        return None
    return offre(mission["donneur"], "joueur", {"type": "objet", "objet": mission["objet"]},
                 {"type": "pieces", "montant": montant})


def disponible(monde, donneur, sauf=None):
    reserves = sum(e["montant"] for id, e in agendas.contrats(monde).items()
                   if id != sauf and e["statut"] in ("propose", "accepte")
                   and monde.data["missions"][id]["donneur"] == donneur)
    return monde.data["finances_pnj"].get(donneur, 0) - reserves


def preparer_conversation(monde, p, revision=None):
    if isinstance(p, dict) and '_adresse' in p:
        canonique = conversation_compte(monde, p['_adresse'])
        if {k: v for k, v in p.items() if k != '_adresse'} != canonique:
            raise ErreurMonde('Les termes de ce règlement ont changé.',
                              f'conversation : reçu {p!r} ; attendu {canonique!r} avec _adresse inchangée.')
        p = canonique
    if revision is not None and revision != monde.data["revision"]:
        raise ErreurMonde("Le monde a changé avant la fin de la conversation.", "re-propose à partir des faits actuels.")
    champs = SCHEMA_CONVERSATION["required"]
    if not isinstance(p, dict) or set(p) != set(champs):
        recus = sorted(p) if isinstance(p, dict) else type(p).__name__
        raise ErreurMonde("Conversation mal formée.", f"conversation_pnj a exactement les champs {', '.join(champs)} ; reçu : {recus}.")
    if (any(not isinstance(p[k], str) or len(p[k]) > 600 for k in ("personnage", "sujet", "operation", "mission"))
            or type(p["montant_demande"]) is not int or not 0 <= p["montant_demande"] <= 1_000_000):
        raise ErreurMonde("Conversation mal formée.",
                          "personnage, sujet, operation, mission : textes de 600 caractères au plus ; montant_demande : "
                          "entier de 0 à 1 000 000.")
    from .voix import reel
    acteur, op, mission_id = reel(monde, p["personnage"]), p["operation"], p["mission"]
    presents = reels(monde)
    if acteur not in presents:
        raise ErreurMonde("Ce personnage n'est pas ici pour te répondre.",
                          f"{acteur} n'est pas là pour répondre : réponds en mode dialogue qu'il est trop loin ; "
                          "ne mène pas la conversation avec un autre personnage à sa place.")
    if op not in OPERATIONS:
        raise ErreurMonde("Cet engagement n'est pas pris en charge.", f"operation parmi {', '.join(OPERATIONS)} (reçu « {op} »).")
    travail = monde.copier()
    travail.data['_comptes_echange'] = []
    resolution_comptable, termes_comptables = None, None
    rapport = {"personnage": acteur, "sujet": p["sujet"], "operation": op, "faits": []}
    if op == "discuter":
        if mission_id or p["montant_demande"]:
            raise ErreurMonde("Une discussion simple ne modifie pas un accord.",
                              "discuter : mission vide et montant_demande 0 ; pour un accord : proposer, negocier, accepter ou refuser.")
    elif mission_id in travail.data.get('offres_joueur', {}):
        from .echanges import proposer
        from .propositions import en_mots
        offre = travail.data['offres_joueur'][mission_id]
        if offre['de'] != acteur or offre['statut'] != 'propose' or op not in ('accepter', 'refuser') or p['montant_demande']:
            raise ErreurMonde("Cette offre ne peut pas être acceptée ainsi.",
                              f"mission={mission_id}, personnage={offre['de']}, operation=accepter|refuser, montant_demande=0 ; statut=propose.")
        issue = 'refuse'
        if op == 'accepter':
            bilan = proposer(travail, acteur, 'joueur', offre['demande'], offre['contrepartie'], accord_joueur=True)
            issue = bilan['cause'] or 'accepte'
        travail.data['offres_joueur'][mission_id]['statut'] = issue
        rapport['faits'].append(f"Offre {issue} : {en_mots(travail, offre['contrepartie'])} contre {en_mots(travail, offre['demande'])}.")
        from .propositions import offre as typer_offre
        termes_comptables = typer_offre(acteur, 'joueur', offre['demande'], offre['contrepartie'])
        resolution_comptable = {'etat': 'accepte' if issue == 'accepte' else 'refuse',
            **({'cause': issue, 'refus_par': 'joueur' if op == 'refuser' else acteur}
               if issue != 'accepte' else {})}
        rapport['offres'] = [termes_comptables]
    else:
        mission = travail.data["missions"].get(mission_id)
        if not mission or mission["donneur"] != acteur:
            siennes = sorted(id for id, x in travail.data["missions"].items() if x["donneur"] == acteur)
            raise ErreurMonde("Ce personnage ne propose pas cette mission.",
                              f"mission : une mission de {acteur}, parmi {', '.join(siennes) or 'aucune'} "
                              f"(reçu « {mission_id} »)" + ("" if siennes else " ; sans mission : operation discuter") + ".")
        if op != "negocier" and p["montant_demande"]:
            raise ErreurMonde("Un montant demandé appartient à une négociation.",
                              f"{op} : montant_demande 0 ; pour demander un montant : negocier.")
        engagements = agendas.contrats(travail)
        accord = engagements.get(mission_id)
        statut = accord["statut"] if accord else None
        if statut == "paye":
            rapport["faits"].append(f"La récompense de {quantite(accord['montant'], 'pièce')} a déjà été versée. Aucun nouveau paiement.")
        elif statut == "accepte":
            rapport["faits"].append(f"L'accord accepté reste de {quantite(accord['montant'], 'pièce')}, payable{'s' if accord['montant'] > 1 else ''} contre la remise de l'objet. Il ne change pas pendant cette discussion.")
        elif op in ("accepter", "refuser"):
            if statut != "propose":
                raise ErreurMonde("Il n'y a aucune offre en attente à accepter ou refuser.",
                                  f"aucune offre proposée pour {mission_id} : proposer ou negocier d'abord.")
            agendas.repondre_contrat(travail, mission_id, op == "accepter")
            rapport["faits"].append(f"Offre de {quantite(accord['montant'], 'pièce')} " + ("acceptée. Le paiement aura lieu à la remise de l'objet." if op == "accepter" else "refusée. Aucun engagement ni paiement."))
        else:
            fonds = disponible(travail, acteur, sauf=mission_id)
            base = mission["prime_base"]
            plafond = min(mission["prime_plafond"], base + max(0, (travail.joueur["stats"]["CHA"] - 10) // 2) * 2, fonds)
            ancien = accord["montant"] if statut == "propose" else 0
            if fonds < base:
                rapport["faits"].append("Il ne dispose pas actuellement de l'argent nécessaire pour une nouvelle offre.")
            else:
                montant = ancien or base
                if op == "negocier":
                    souhait = p["montant_demande"] or plafond
                    montant = max(montant, min(souhait, plafond))
                agendas.proposer_contrat(travail, mission_id, montant)
                rapport["faits"].append(f"Offre de {quantite(montant, 'pièce')} contre la remise de l'objet. Le joueur ne l'a pas encore acceptée. Aucun paiement immédiat.")
                if op == "negocier" and p["montant_demande"] > montant:
                    rapport["faits"].append(f"Le montant demandé de {quantite(p['montant_demande'], 'pièce')} est refusé ; la contre-offre est de {quantite(montant, 'pièce')}.")
                elif op == "negocier" and ancien == montant:
                    rapport["faits"].append("Il maintient son offre précédente.")
        rapport["mission"] = {"id": mission_id, **_mission_publique(travail, mission_id)}
        rapport["engagement"] = agendas.contrats(travail).get(mission_id)
        rapport["offres"] = [o] if (o := offre_mission(travail, mission_id)) else []
        resolution_comptable = {"mission": mission_id, "operation": op,
            "engagement": copy.deepcopy(rapport["engagement"]), "montant_demande": p["montant_demande"]}
        from .propositions import offre
        termes_comptables = offre(acteur, "joueur", {"type": "objet", "objet": mission["objet"]},
            {"type": "pieces", "montant": (rapport["engagement"] or {}).get("montant", mission["prime_base"])})
    comptes = travail.data.pop('_comptes_echange')
    if comptes:
        rapport['comptes'] = comptes
    travail.data["revision"] += 1
    if resolution_comptable is not None:
        from .repliques_moteur import admettre
        from .emissions import lire, publiques
        debut = len(lire(travail))
        autorisations = [{"locuteur": acteur, "parametres": {"contenu": []},
            "evenement": {"faits": [], "resolutions_comptables": [{"resolution": resolution_comptable,
                "comptes": comptes, "offres": rapport["offres"], "termes": [termes_comptables], "faits": []}]}}]
        admettre(travail, autorisations, {**rapport, "offres": [termes_comptables]})
        rapport["emissions"] = publiques(travail, lire(travail)[debut:])
        # La commande sociale directe publie les faits du rapport sans MJ.
        # Les mots enregistrés doivent donc aussi figurer dans son résultat.
        rapport["faits"].extend(p["rendu"] for p in rapport["emissions"])
    travail.data.setdefault("echanges_pnj", []).append({"revision": travail.data["revision"], **copy.deepcopy(rapport)})
    travail.verifier()
    return travail, rapport


def remise_convenue(monde, objet_id, destinataire=""):
    """La mission dont l'accord accepté attend cet objet, auprès d'un donneur présent ; sinon None."""
    candidats = [id for id, m in monde.data["missions"].items()
                 if m["objet"] == objet_id and (not destinataire or m["donneur"] == destinataire)
                 and m["donneur"] in interlocuteurs(monde)
                 and agendas.contrats(monde).get(id, {}).get("statut") == "accepte"]
    return candidats[0] if len(candidats) == 1 else None


def verifier_don(monde, objet_id, destinataire=""):
    """Donner un objet porté à un personnage présent : le geste ordinaire, sans contrepartie."""
    if objet_id not in monde.objets or monde.objets[objet_id]["lieu"] != "joueur":
        portes = sorted(i for i, o in monde.objets.items() if o["lieu"] == "joueur")
        raise ErreurMonde("Tu dois porter l'objet pour le donner.",
                          f"remettre vise un objet porté, parmi {cibles(monde, portes)} (reçu « {objet_id} »).")
    presents = sorted(interlocuteurs(monde))
    from .voix import designation
    if destinataire in monde.objets and str(designation(monde, destinataire)).startswith("personne_") and designation(monde, destinataire) in presents:
        return destinataire
    if not destinataire and len(presents) == 1:
        destinataire = presents[0]
    from .voix import reel
    if destinataire in presents and reel(monde, destinataire) != destinataire:
        return reel(monde, destinataire)  # Une voix qu'il ne sait à qui prêter, dans le noir.
    if destinataire not in presents:
        # Il ne le sait là que par une voix qui porte ce nom : c'est à elle qu'il le tend (``voix.porteur_du_nom``).
        from .voix import porteur_du_nom
        porteur = porteur_du_nom(monde, destinataire, [reel(monde, d) for d in presents])
        if porteur:
            return porteur
        # Celui qu'il connaît et nomme, il ne le perçoit pas : on le lui dit, qu'il y ait ou non d'autres présents.
        # Ce qu'il en sait, c'est qu'il ne le voit pas, pas qu'il n'est pas là.
        from .paroles import _connu_du_joueur
        nomme = (destinataire in monde.objets and monde.objets[destinataire]["type"] == "personnage"
                 and _connu_du_joueur(monde, destinataire))
        raise ErreurMonde(f"Tu ne vois pas {monde.objets[destinataire]['nom'].split(',')[0]} d'ici : approche-toi "
                          "pour le lui donner."
                          if nomme else "Il n'y a personne ici pour le recevoir." if not presents
                          else "Précise à qui tu le donnes.",
                          f"outil = le personnage qui reçoit, parmi les présents : {cibles(monde, (reel(monde, id) for id in presents))}.")
    return destinataire


def verifier_remise(monde, objet_id, destinataire=""):
    if objet_id not in monde.objets or monde.objets[objet_id]["lieu"] != "joueur":
        portes = sorted(i for i, o in monde.objets.items() if o["lieu"] == "joueur")
        raise ErreurMonde("Tu dois porter l'objet pour le remettre.",
                          f"remettre vise un objet porté, parmi {cibles(monde, portes)} (reçu « {objet_id} »).")
    candidats = [(id, m) for id, m in monde.data["missions"].items() if m["objet"] == objet_id
                  and (not destinataire or m["donneur"] == destinataire)]
    candidats = [(id, m) for id, m in candidats if m["donneur"] in interlocuteurs(monde)]
    if len(candidats) != 1:
        donneurs = sorted({m["donneur"] for m in monde.data["missions"].values() if m["objet"] == objet_id})
        raise ErreurMonde("Le destinataire doit être présent ; précise à qui remettre cet objet.",
                          f"{objet_id} est attendu par {cibles(monde, donneurs)} ; présents : "
                          f"{cibles(monde, reels(monde))}.")
    id, mission = candidats[0]
    from .proximite import exiger
    exiger(monde, mission["donneur"])
    accord = agendas.contrats(monde).get(id)
    if not accord or accord["statut"] != "accepte":
        raise ErreurMonde("Il faut d'abord convenir d'une récompense et accepter l'offre.",
                          f"mission {id} sans offre acceptée : conversation_pnj (proposer ou negocier, puis accepter) avant remettre.")
    if monde.data["finances_pnj"].get(mission["donneur"], 0) < accord["montant"]:
        raise ErreurMonde("Le destinataire n'a pas l'argent promis. Aucun objet n'a été remis.",
                          f"{mission['donneur']} ne peut pas payer {quantite(accord['montant'], 'pièce')} : la remise attendra.")
    return id


def payer_remise(monde, mission_id, lignes):
    mission = monde.data["missions"][mission_id]
    verifier_remise(monde, mission["objet"], mission["donneur"])
    accord = agendas.contrats(monde)[mission_id]
    destinataire = mission["donneur"]
    objet = monde.objets[mission["objet"]]
    objet["lieu"], objet["proprietaire"] = destinataire, destinataire
    objet.pop("vole_par", None)
    objet.pop("position", None)
    objet.pop("position_salle", None)
    monde.data["finances_pnj"][destinataire] -= accord["montant"]
    monde.joueur["or"] += accord["montant"]
    agendas.payer_contrat(monde, mission_id)
    nom = monde.objets[destinataire]["nom"]
    lignes.append(f"Tu remets {designer(objet)} {groupe_nominal(nom, 'à')}. Tu reçois {quantite(accord['montant'], 'pièce', determinant='defini')} convenue{'s' if accord['montant'] > 1 else ''}.")


def commande_sociale(monde, texte):
    """Quelques commandes hors ligne ; les phrases libres restent interprétées par le MJ."""
    texte = normaliser(texte)
    operation, _, cible = texte.partition(" ")
    operations = {"offre": "proposer", "negocier": "negocier", "accepter": "accepter", "refuser": "refuser"}
    if operation not in operations:
        return None
    montant = 0
    if operation == "negocier" and cible.rsplit(" ", 1)[-1].isdigit():
        cible, _, montant_str = cible.rpartition(" ")
        montant = int(montant_str)
    presents = interlocuteurs(monde)
    if cible == "offre" and operation in ("accepter", "refuser"):
        candidats = [(id, mission) for id, mission in monde.data["missions"].items()
                      if mission["donneur"] in presents and agendas.contrats(monde).get(id, {}).get("statut") == "propose"]
        candidats += [(id, {'donneur': o['de']}) for id, o in monde.data.get('offres_joueur', {}).items()
                       if o['de'] in reels(monde) and o['statut'] == 'propose']
    else:
        from .voix import reel
        acteurs = [id for id in presents if cible in [normaliser(n) for n in
                  (id, presents[id]['nom'], *monde.objets.get(id, {}).get('aliases', []))]]
        acteurs = [reel(monde, a) for a in acteurs]
        candidats = [(id, m) for id, m in monde.data["missions"].items() if m["donneur"] in acteurs]
        candidats += [(id, {'donneur': o['de']}) for id, o in monde.data.get('offres_joueur', {}).items()
                       if o['de'] in acteurs and o['statut'] == 'propose' and operation in ('accepter', 'refuser')]
    if len(candidats) != 1:
        raise ErreurMonde("Précise le personnage présent et son offre, ou accepte une offre en attente.")
    id, mission = candidats[0]
    return {"personnage": mission["donneur"], "sujet": texte, "operation": operations[operation],
            "mission": id, "montant_demande": montant}
