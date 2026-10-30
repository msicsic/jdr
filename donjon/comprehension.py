"""Récapitulatif public d'un plan admis, sans interprétation de la saisie.

Les verbes et expansions viennent des compilateurs (titres et sous-plans).
Les paramètres typés complètent ces titres : ils ne sont jamais résumés ni
remplacés par la justification ou les récits proposés par le MJ.
"""
from .francais import designer
from .noms import reference, texte


def repere(monde, identifiant):
    if identifiant == "joueur":
        return "toi"
    from .voix import reel, nom_pour_joueur
    id = reel(monde, identifiant)
    if id in monde.objets:
        o = monde.objets[id]
        nom = (nom_pour_joueur(monde, id) if o["type"] in ("personnage", "depouille")
               else texte(monde, designer(o)))
        return f"{nom} [{reference(monde, id)}]"
    if id in monde.data["salles"]:
        return f"{monde.data['salles'][id]['nom']} [{id}]"
    return identifiant


REFERENCES = {"cible", "cibles", "destination", "outil", "objet", "lieu", "servir",
              "montants", "traverses", "barreaux", "lien", "vendeur", "destinataire"}
LIBELLES = {"methode": "méthode", "reussite": "en cas de réussite", "echec": "en cas d'échec",
            "longueur_cm": "longueur (cm)", "largeur_cm": "largeur (cm)"}


def valeur(monde, v, est_reference=False):
    """Paramètres du contrat admis, y compris les branches conditionnelles."""
    if isinstance(v, dict):
        return "; ".join(f"{LIBELLES.get(k, k.replace('_', ' '))} : {valeur(monde, x, k in REFERENCES)}" for k, x in v.items()
                         if k not in ("recit", "justification", "intention") and x != "")
    if isinstance(v, list):
        return " ; ".join(valeur(monde, x, est_reference) for x in v) or "aucun"
    if isinstance(v, bool):
        return "oui" if v else "non"
    return (repere(monde, v) if est_reference else texte(monde, v)) if isinstance(v, str) else str(v)


def _geste(monde, plan, parametres):
    # Le titre est le sens écrit par le compilateur, aussi utilisé par la fiche
    # et le récit des gestes accomplis. Les champs empêchent les pertes de
    # cible/partie, destination, méthode, quantité ou condition dans ce titre.
    details = {k: v for k, v in parametres.items()
               if k not in ("action", "operation", "justification", "intention", "difficulte", "stat")
               and v != "" and not (k == "methode" and v == "simple")}
    # Le prix et les parties d'un achat sont fixés à la compilation, ils ne
    # figurent pas dans la commande simple. Lire l'effet admis, jamais le prix
    # recalculé après le paiement.
    for op, cible, termes in plan.effets:
        if op == "payer":
            details["paiement"] = termes
        elif op == "remettre":
            from .dialogues import offre_mission
            offre = offre_mission(monde, cible)
            if offre:
                from .propositions import offre_en_mots
                details["accord"] = offre_en_mots(monde, offre)
    return plan.titre + (" (" + valeur(monde, details) + ")" if details else "")


def plan_admis(monde, plan):
    if plan.etapes:
        lignes = [f"{i}. {_geste(monde, sous_plan, e)}"
                  for i, (sous_plan, e) in enumerate(zip(plan.plans, plan.etapes), 1)]
        if len(lignes) > 1:
            lignes.append("Arrêt au premier échec ; les étapes déjà réussies restent acquises.")
        return "Compris :\n" + "\n".join(lignes)
    return "Compris : " + _geste(monde, plan, plan.proposition)


def contenu(monde, c):
    """Contenu typé d'une parole, distinct de la vérité de ce qu'elle affirme."""
    from .propositions import en_mots
    from .paroles import RESSOURCES_DEMANDEES, resoudre
    t = c["type"]
    if t == 'mandat':
        from .agendas import phrase_charge
        from .paroles import _typer
        return 'confier la charge de ' + phrase_charge(monde, c['sorte'], _typer(monde, c)['parametres'])
    if t == 'reponse_mandat':
        return ('accepter' if c['accepter'] else 'refuser') + ' le mandat ' + c['offre']
    if t == 'bilan_mandat':
        return 'déclarer ' + c['issue'] + ' pour le mandat ' + c['agenda']
    if t == "proposition":
        from .propositions import cites_terme
        def terme(t):
            refs = [repere(monde, ref) for ref in cites_terme(t)]
            return texte(monde, en_mots(monde, t)) + (" (" + "; ".join(refs) + ")" if refs else "")
        return f"offrir {terme(c['contrepartie'])} contre {terme(c['demande'])}"
    s, v = c.get("sujet", ""), c.get("valeur", "")
    sujet = repere(monde, resoudre(monde, s) or s) if s else ""
    if t == "propos":
        return "propos sans effet mécanique typé"
    if t == "avis":
        return f"annoncer une prévision : {sujet}, {'menace' if v == 'oui' else 'absence de menace'} de l'eau"
    if t == "affirmation":
        return f"affirmer : {sujet}, {c['attribut']} = {valeur(monde, v)}"
    if t in ("demande", "passage"):
        acte = f"demander {sujet}" if t == "demande" else f"demander le passage à {sujet}"
        return acte + (f" contre {v} pièces" if v else " sans prix offert")
    if t == "aveu":
        return f"avouer : {v} sur {sujet}"
    if t == "nom":
        nom = monde.joueur["nom"] if s == "joueur" else sujet
        return f"se présenter sous le nom {nom}"
    if t == "qui":
        return "demander l'identité de l'interlocuteur"
    if t == "reclamer":
        return f"réclamer le dû : {sujet or 'pièces'}"
    if t == "ressource":
        # Un nom recherché est du texte, pas l'identifiant d'un bien caché.
        return "demander si l'interlocuteur possède " + RESSOURCES_DEMANDEES.get(s, s)
    if t == "localisation":
        return "demander où se trouve " + sujet
    raise ValueError(f"Contenu sans rendu public : {t}")


def transactions_admises(monde, transactions, rapports):
    lignes = []
    from .paroles import annonce
    for transaction, rapport in zip(transactions, rapports):
        p = transaction["proposition"]
        if transaction["type"] == "parole":
            lignes.append(annonce(monde, rapport) + " (" + rapport["maniere"] + ")")
            lignes.extend(contenu(monde, c) for c in p["contenu"])
        elif transaction["type"] == "conversation_pnj":
            operations = {"discuter": "discuter", "proposer": "demander une offre", "negocier": "négocier",
                          "accepter": "accepter l'offre", "refuser": "refuser l'offre"}
            lignes.append(f"{operations[p['operation']]} avec {repere(monde, p['personnage'])} ; sujet : {p['sujet']}"
                          + (f" ; mission : {p['mission']} ; montant demandé : {p['montant_demande']} pièces"
                             if p["mission"] else ""))
            if p["mission"]:
                from .dialogues import offre_mission
                from .propositions import offre_en_mots
                offre = offre_mission(monde, p["mission"])
                if offre:
                    lignes.append(texte(monde, offre_en_mots(monde, offre)))
        # Les admissions de connaissances/détails ne sont pas des actes du
        # joueur : leur dossier peut comporter des savoirs privés de PNJ.
        # Leur rendu public existant reste sur sa voie, sans publier ce dossier.
    return "Compris : " + "\n".join(lignes) if lignes else ""
