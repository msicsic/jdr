"""Récapitulatif public d'un plan admis, sans interprétation de la saisie.

Les verbes et expansions viennent des compilateurs (titres et sous-plans).
Les paramètres typés complètent ces titres : ils ne sont jamais résumés ni
remplacés par la justification ou les récits proposés par le MJ.
"""
from .francais import designer
from .noms import reference, texte


def champs_types_revue(proposition, chemin=""):
    """Tous les paramètres mécaniques du candidat ; les trois proses sont distinctes.

    Le candidat est déjà contrôlé par sa grammaire. Contrairement à l'empreinte
    conservatrice A5, cette table couvre aussi nombres, quantités et clauses.
    Elle ne lit jamais la saisie et ne décide pas des valeurs qu'elle demande.
    """
    import copy
    resultat = {}
    for cle, v in proposition.items():
        if cle in {"justification", "intention", "recit"}:
            continue
        nom = chemin + cle
        if isinstance(v, dict) and v:
            resultat.update(champs_types_revue(v, nom + "."))
        elif isinstance(v, list) and v and all(isinstance(e, dict) for e in v):
            for i, e in enumerate(v):
                resultat.update(champs_types_revue(e, f"{nom}.{i}."))
        else:
            resultat[nom] = copy.deepcopy(v)
    return resultat


def parametres_types(proposition, chemin=""):
    """Empreinte de sens d'un candidat, même non préparé. Aucune prose ne fait foi."""
    import copy
    resultat = {}
    if not isinstance(proposition, dict):
        return resultat
    for cle, valeur_ in proposition.items():
        nom = chemin + cle
        if cle in {"action", "operation", "methode", "outil", "approche", "cible", "cibles", "destination"}:
            resultat[nom] = copy.deepcopy(valeur_)
        if cle == "texte" and proposition.get("operation") == "son":
            resultat[nom] = valeur_
        if isinstance(valeur_, dict):
            resultat.update(parametres_types(valeur_, nom + "."))
        elif isinstance(valeur_, list) and cle in {"etapes", "effets"}:
            for i, v in enumerate(valeur_):
                resultat.update(parametres_types(v, f"{nom}.{i}."))
    return resultat


def verifier_reprise(proposition, invariants, monde=None):
    """Seuls les champs explicitement mis en cause peuvent remplacer le candidat refusé."""
    from .refus import RefusDeForme
    recus = parametres_types(proposition)
    for chemin, accepte in invariants.items():
        identique = chemin in recus and recus[chemin] == accepte
        if not identique and monde is not None and chemin in recus:
            from .noms import CHAMPS_REFERENCES, LISTES_REFERENCES
            from .voix import reel
            champ = chemin.rsplit('.', 1)[-1]

            def meme_entite(a, b):
                if not isinstance(a, str) or not isinstance(b, str):
                    return False
                id_ = reel(monde, a)
                return id_ in monde.objets and id_ == reel(monde, b)

            # Une référence publique et son identifiant désignent le même corps.
            # Leur équivalence ne vaut pas admission : les gardes de références
            # fournies et de perception restent appliquées au candidat corrigé.
            if champ in CHAMPS_REFERENCES:
                identique = meme_entite(recus[chemin], accepte)
            elif champ in LISTES_REFERENCES:
                a, b = recus[chemin], accepte
                identique = (isinstance(a, list) and isinstance(b, list) and len(a) == len(b)
                             and all(x == y or meme_entite(x, y) for x, y in zip(a, b)))
        if not identique:
            raise RefusDeForme("La correction remplace une partie du geste qui n'était pas en cause.",
                f"proposition.{chemin} : reçu {recus.get(chemin)!r} ; accepté : {accepte!r}. "
                "Reprendre la saisie entière et le refus ; le candidat précédent reste non admis.")


def invariants_reprise(proposition, exc):
    if proposition.get("action") in {"impossible", "clarifier"}:
        return {}
    libres = getattr(exc, "champs_corrigeables", ())
    return {k: v for k, v in parametres_types(proposition).items()
            if not any(c == "" or k == c or k.startswith(c + ".") for c in libres)}


def _precisions(plan, parametres):
    """Même sens calculé pour le joueur et la revue, sans lire la prose proposée."""
    from .contrats_sequence import precision_publique as sequence
    from .contrats_son import precision_publique as son
    from .contrats_passage import precision_publique as passage
    from .contrats_lots import precision_publique as lot
    return [p for p in (sequence(parametres), son(plan, parametres), passage(parametres),
                       lot(plan.quantite_transfert)) if p]


def sens_propose(plan, parametres=None):
    """Dossier de sens, distinct du verdict d'admission et du rendu public.

    Le texte libre reste une proposition de manière, jamais une preuve d'effet.
    Les étapes développées peuvent porter une opération absente du raccourci.
    Aucun mot de la saisie ne choisit ici un contrat ou une conséquence.
    """
    import copy
    from . import contrats_sequence, contrats_son, contrats_passage, contrats_lots
    p = plan.proposition if parametres is None else parametres
    contrats = [s for famille in (contrats_sequence, contrats_son, contrats_passage, contrats_lots)
                if (s := famille.sens_propose(p))]
    maniere = {k: copy.deepcopy(p[k]) for k in ("methode", "outil", "intention", "approche") if k in p}
    for branche in ("reussite", "echec"):
        if isinstance(p.get(branche), dict) and "recit" in p[branche]:
            maniere[branche] = p[branche]["recit"]
    quantite = plan.quantite_transfert
    return {"operation": p.get("operation", p.get("action", "")),
            **({"quantite_transfert": copy.deepcopy(quantite)} if quantite is not None else {}),
            "parametres": copy.deepcopy({k: v for k, v in p.items()
                                         if k not in ("justification", "etapes")}),
            "contrats": contrats, "maniere_proposee": maniere,
            "precisions_moteur": _precisions(plan, p)}


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
    if parametres.get("action") == "attendre":
        # La cible transporte les secondes ; le titre donne déjà leur durée.
        details.pop("cible", None)
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
    precision = " ".join(_precisions(plan, parametres))
    return (plan.titre + (" (" + valeur(monde, details) + ")" if details else "")
            + (" " + precision if precision else ""))


def plan_admis(monde, plan):
    if plan.etapes:
        lignes = [f"{i}. {_geste(monde, sous_plan, e)}"
                  for i, (sous_plan, e) in enumerate(zip(plan.plans, plan.etapes), 1)]
        if len(lignes) > 1:
            from .contrats_sequence import COMPOSITION
            lignes.append(COMPOSITION["arret"])
        return "Compris :\n" + "\n".join(lignes)
    return "Compris : " + _geste(monde, plan, plan.proposition)


def contenu(monde, c, interlocuteur="", *, reference_ressource=False, destinataire=None):
    """Contenu typé d'une parole, distinct de la vérité de ce qu'elle affirme."""
    from .propositions import en_mots
    from .paroles import resoudre
    from .contrats_consultation import CONSULTATIONS, public as consultation_publique
    t = c["type"]
    if t in CONSULTATIONS:
        return consultation_publique(monde, c, reference_ressource=reference_ressource)
    if t == 'mandat':
        from .agendas import phrase_charge
        from .paroles import _typer
        return 'confier la charge de ' + phrase_charge(monde, c['sorte'], _typer(monde, c)['parametres'])
    if t == 'rembourser':
        from .biens import dues
        montant = c['montant'] or sum(d['montant'] for d in dues(monde, 'joueur', destinataire))
        return (f"rembourser {montant} pièces à {interlocuteur}"
                + (" (tout le dû)" if not c['montant'] else ""))
    if t == 'reponse_mandat':
        return ('accepter' if c['accepter'] else 'refuser') + ' le mandat ' + c['offre']
    if t == 'bilan_mandat':
        return 'déclarer ' + c['issue'] + ' pour le mandat ' + c['agenda']
    if t == "proposition":
        from .propositions import cites_terme
        def terme(t):
            refs = [repere(monde, ref) for ref in cites_terme(t)]
            return texte(monde, en_mots(monde, t)) + (" (" + "; ".join(refs) + ")" if refs else "")
        return (f"offrir {terme(c['contrepartie'])}"
                + (" payées maintenant" if c['contrepartie']['type'] == 'pieces' and 'limite' in c['demande'] else "")
                + f" contre {terme(c['demande'])}")
    s, v = c.get("sujet", ""), c.get("valeur", "")
    sujet = repere(monde, resoudre(monde, s) or s) if s else ""
    if t == "propos":
        return "propos sans effet mécanique typé"
    if t == "avis":
        return f"annoncer une prévision : {sujet}, {'menace' if v == 'oui' else 'absence de menace'} de l'eau"
    if t == "affirmation":
        return f"affirmer : {sujet}, {c['attribut']} = {valeur(monde, v)}"
    if t in ("demande", "passage"):
        # Le passage se demande à qui l'on parle : son contenu n'a pas de sujet.
        a = sujet or interlocuteur
        acte = f"demander {sujet}" if t == "demande" else "demander le passage" + (f" à {a}" if a else "")
        from .contrats_passage import DEMANDE
        return (acte + (f" contre {v} pièces" if v else " sans prix offert")
                + (". " + DEMANDE["public"] if t == "passage" else ""))
    if t == "aveu":
        return f"avouer : {v} sur {sujet}"
    if t == "nom":
        nom = monde.joueur["nom"] if s == "joueur" else sujet
        return f"se présenter sous le nom {nom}"
    raise ValueError(f"Contenu sans rendu public : {t}")


def transactions_admises(monde, transactions, rapports):
    lignes = []
    from .paroles import annonce
    for transaction, rapport in zip(transactions, rapports):
        p = transaction["proposition"]
        if transaction["type"] == "parole":
            lignes.append(annonce(monde, rapport) + " (" + rapport["maniere"] + ")")
            qui = rapport["personnage"]
            a = "" if qui in ("personne", "tous") else rapport.get("a_qui") or repere(monde, qui)
            lignes.extend(contenu(monde, c, a, reference_ressource="_adresse" in p, destinataire=qui)
                          for c in p["contenu"])
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
