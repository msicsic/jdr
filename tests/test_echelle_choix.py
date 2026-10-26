"""A0 : oracle historique, scènes et nuits sans modèle, sauvegarde et rendu."""
import unittest
from unittest.mock import patch

from donjon import banc_pnj, deliberation as d
from donjon.esprits import croire, lire, memoriser, pnjs
from donjon.moteur import Moteur, proposition
from donjon.rendu import decrire_perception, fiche
from tests.support import calme
from tests.test_tensions import recharger

from donjon.deliberation import (
    ARGENT, ENQUETES, GESTE_PROGRES, PROGRES, RECOURS, alarme, bruit_a_voir,
    esprit, periodique, profil, retabli_par_son_plan, satisfaite, urgents,
)
from donjon.deliberation import (
    _plan_faim, _plan_enquete, _delegue, _pulsion_a_soi, _plan_garder,
    _plan_prevenir, _plan_attendre, _plan_abri, _plan_creance, _plan_argent,
    _continuer_progres,
)


def anciens_candidats(monde, id):
    """(besoin, méthode, routine, recours) : les buts de ``candidats``, avec leur rang (la routine
    après le reste) et s'ils sont un recours de leur besoin (ce qui l'apaise ou le rétablit) ; une
    parole due, prévenir, attendre l'appelant, une alarme, sortir de l'eau, un bruit à voir et l'argent
    n'en sont pas : ils passent devant un recours en cours (``choisir``).

    Un besoin qui vient à peine de franchir son seuil laisse finir le plan en cours d'un autre
    motif, et un besoin apaisé ne presse de nouveau que nettement au-dessus (``urgents``)."""
    p, e = profil(monde, id), esprit(monde, id)
    buts = []
    # Ceux qui laissent finir le plan en cours n'y ajoutent rien, mais restent pressants : ni
    # routine ni pulsion rompue de leur fait ne passe devant ce plan.
    pressants = urgents(monde, id)
    for besoin in urgents(monde, id, inertie=True):
        if besoin == "faim":
            buts.append((besoin, _plan_faim, False))
            # Rien de ce qu'il connaît ne le nourrit : il demande à qui pourrait en avoir.
            buts.append((besoin, lambda m, i: _plan_enquete(m, i, "faim"), False))
            continue
        buts += [(besoin, methode, False) for methode in RECOURS.get(besoin, ())]
        if besoin in PROGRES:
            # Le geste qui apaise d'abord ; les pulsions du même besoin (les rondes) restent des recours.
            buts.append((besoin, PROGRES[besoin][0], False))
        if besoin in ENQUETES:
            buts.append((besoin, lambda m, i, b=besoin: _plan_enquete(m, i, b), False))
        pulsions = [x for x in p["pulsions"] if x["besoin"] == besoin]
        for x in pulsions:
            if (not satisfaite(monde, id, x["condition"]) and not _delegue(monde, id, x)
                    and not retabli_par_son_plan(monde, id, x["condition"])):
                # Une ronde peut attendre qu'il ait tenu parole ; un feu à voir ou à recharger, non.
                buts.append((besoin, lambda m, i, c=x["condition"]: _pulsion_a_soi(m, i, c),
                             periodique(x["condition"])))
                if "allume" in x["condition"]:
                    # Un feu sans bois qu'il connaisse : il demande à qui pourrait en avoir.
                    buts.append((besoin, lambda m, i: _plan_enquete(m, i, "chaleur"), False))
        if besoin == "biens":
            for x in pulsions:
                if periodique(x["condition"]):
                    continue
                buts.append((besoin, lambda m, i, c=x["condition"]: _plan_garder(m, i, c), True))
    # Toute parole de service suit le devis qui l'a fait accepter, jusqu'à son abandon annoncé.
    from donjon.planification import planifier_engagement
    buts += [("engagement", lambda m, i, x=x: planifier_engagement(m, i, x), False, False)
             for x in e["engagements"]]
    # Un corps à terre connu : recours au même graphe de gestes, sans accès à ses PV ni son réveil.
    for protege in p.get("protege", ()):
        c = e["croyances"].get(protege, {}).get("etat", {})
        if c.get("valeur", {}).get("conscient") is False and not c["valeur"].get("mort"):
            from donjon.planification import ranimer
            buts.insert(0, ("devoir", lambda m, i, x=protege: ranimer(m, i, x), False, False))
    # Un protégé atteint sous ses yeux : il va le prévenir, comme une parole due.
    if any(s["type"] == "a_prevenir" for s in e["memoire"]):
        buts.append(("devoir", _plan_prevenir, False, False))
    # « J'arrive ! » à un appel : une parole due, comme une autre (``appel.plan_venir``).
    if e["rejoindre"]:
        from donjon.appel import plan_venir
        buts.append(("engagement", plan_venir, False, False))
    # Il a convenu d'attendre qui l'a hélé ou qu'il a hélé (``appel``), après ce qui presse et la
    # parole due ; un bruit, ce qui ne presse pas et la routine attendent.
    if e["rejoint"]:
        buts.append(("rejoint", _plan_attendre, False, False))
    # Un bruit inconnu qu'il doit, ou ose, aller voir : après ce qui presse, avant la routine ; une
    # alarme (l'appel d'un protégé, un bruit à son seuil d'alerte), avant tout le reste.
    from donjon.planification import voir
    a_voir, alarme_ = bruit_a_voir(monde, id), alarme(monde, id)
    if alarme_:
        buts.insert(0, (alarme_[1], lambda m, i, s=alarme_[0]: voir(m, i, s), False, False))
    # Là où il se tient, il attend l'eau trop haute pour s'y mouvoir : en sortir passe avant tout.
    from donjon.eau import en_peril
    if "securite" in p["besoins"] and en_peril(monde, id):
        buts.insert(0, ("securite", _plan_abri, False, False))
    if a_voir and a_voir != alarme_:
        buts.append((a_voir[1], lambda m, i, s=a_voir[0]: voir(m, i, s), False, False))
    # Ce dont il a la charge et qu'il voit rompu, il le rétablit sans attendre que son besoin
    # presse : un feu qui baisse, un protégé qui a faim, ce qu'il garde sous clé et a lui-même
    # ouvert. Les rondes ont leur routine ; un désir jamais satisfait attend son besoin.
    for i, x in enumerate(p["pulsions"]):
        c = x["condition"]
        if (e["pulsions"][i] is False and x["besoin"] not in pressants and not periodique(c)
                and not _delegue(monde, id, x) and not satisfaite(monde, id, c)
                and not retabli_par_son_plan(monde, id, c)):
            buts.append((x["besoin"], lambda m, i, c=c: _pulsion_a_soi(m, i, c), False))
            if "allume" in c:
                buts.append((x["besoin"], lambda m, i: _plan_enquete(m, i, "chaleur"), False))
    # Assis pour se reposer, ou près du feu, il ne s'en va qu'une fois remis, ou pour plus pressant.
    # Seulement si son plan comporte bien ce geste : une ronde a le même motif que l'abri.
    for besoin, (methode, fin) in PROGRES.items():
        if (e["intention"] and e["intention"]["motif"] == besoin and e["besoins"].get(besoin, 0) > fin
                and any(x["operation"] == GESTE_PROGRES[besoin] for x in e["intention"]["plan"])):
            # Lot 90 : le rang historique est inchangé ; la reprise retrouve
            # maintenant le recours qui porte le progrès, puis ses replis.
            buts.append((besoin, lambda m, i, b=besoin: _continuer_progres(m, i, b), False))
    # La routine : ses rondes, même quand le besoin qu'elles servent ne presse pas.
    for x in p["pulsions"]:
        if (periodique(x["condition"]) and x["besoin"] not in pressants
                and not satisfaite(monde, id, x["condition"]) and not _delegue(monde, id, x)):
            buts.append((x["besoin"], lambda m, i, c=x["condition"]: _pulsion_a_soi(m, i, c), True))
    # L'argent : un poids permanent, qui ne presse jamais ; il ne passe qu'après tout le reste.
    # Ce qu'on lui doit d'abord, puis des pièces à prendre.
    buts.append((ARGENT, _plan_creance, True, False))
    buts.append((ARGENT, _plan_argent, True, False))
    # Ce qui presse vraiment, la parole donnée et ce qu'on finit, puis la routine, par urgence.
    for besoin, methode, routine, *recours in sorted(buts, key=lambda x: x[2]):
        yield besoin, methode, routine, recours[0] if recours else True


def identite(methode):
    """Fonction partagée, ou corps et arguments liés d'une méthode anonyme.

    Les numéros de ligne et le nom de la fonction englobante changent à la copie,
    mais ni le code exécuté, ni ses constantes, ni ses cibles ne doivent changer.
    """
    if methode.__name__ != "<lambda>":
        return methode
    c = methode.__code__
    return (c.co_code, c.co_consts, c.co_names, methode.__defaults__,
            tuple(x.cell_contents for x in methode.__closure__ or ()))


def signature(liste):
    return [(c[0], c[2], c[3], identite(c[1])) for c in liste]


def scene():
    m = banc_pnj.creer("relais", 1985, "fixe")
    calme(m, *pnjs(m))
    return m


def appel(e):
    e["rejoindre"] = {"qui": "ilse", "salle": "antichambre", "depuis": 0, "jusqu_a": 10}
    e["rejoint"] = {"qui": "aubin", "depuis": 0, "jusqu_a": 10, "vient": True}


def bruit(m, niveau):
    # Une salle qu'il n'a pas revue depuis ce bruit : il reste à résoudre.
    lire(m, "marchand")["visites"].pop("crypte", None)
    memoriser(m, "marchand", {"type": "bruit", "salle": "crypte", "nature": "fracas",
                             "niveau": niveau, "direction": "est"})


class EchelleTests(unittest.TestCase):
    def comparer(self, m, qui):
        avant = list(anciens_candidats(m, qui))
        apres = list(d._candidats(m, qui))
        self.assertEqual(signature(avant), signature(apres), (qui, m.data["minutes"]))
        cles = [c.urgence.cle() for c in apres]
        self.assertEqual(cles, sorted(cles))
        self.assertEqual(len(cles), len(set(cles)))  # aucun ordre implicite à égalité
        self.assertEqual([(b, identite(f)) for b, f in d.candidats(m, qui)],
                         [(c.besoin, identite(c.methode)) for c in apres])
        return apres

    def test_scenes_tous_les_paliers_et_rechargement(self):
        couverts = set()
        for variante in ("priorites", "bruit", "rompue", "progres", "routine"):
            with self.subTest(variante=variante):
                m = scene()
                e, p = lire(m, "marchand"), m.objets["marchand"]["profil"]
                if variante == "priorites":
                    p["alerte"] = 9
                    # Plusieurs besoins exactement au seuil : ordre BESOINS, recours et routines.
                    e["besoins"].update(d.seuils(m, "marchand"))
                    e["visites"].clear()
                    for protege in p["protege"]:
                        croire(m, "marchand", protege, "etat", {"conscient": False}, "vu")
                    for objet in ("brasero", "reserve"):
                        e["engagements"].append({"condition": {"objet": objet, "rendre": "ilse"},
                                                 "pour": "ilse", "minute": 0})
                    memoriser(m, "marchand", {"type": "a_prevenir", "victime": "ilse", "auteur": "brune"})
                    appel(e)
                    bruit(m, 9)
                    # Le péril est une croyance du PNJ dans un monde avec crue active.
                    from donjon.crue import nouvelle_crue
                    m.data["crue"] = nouvelle_crue(1985, "fixe").data["crue"]
                    croire(m, "marchand", m.objets["marchand"]["lieu"], "eau", 150, "vu")
                elif variante == "bruit":
                    bruit(m, -9)
                    appel(e)
                elif variante == "rompue":
                    e["pulsions"][1] = False
                    croire(m, "marchand", "brasero", "etat", {"allume": False}, "vu")
                elif variante == "progres":
                    e["besoins"]["repos"] = 30.0
                    e["intention"] = {"but": {"type": "repos"}, "motif": "repos",
                                      "plan": [{"operation": "reposer", "cible": "", "outil": "",
                                                "lieu": "", "condition": ""}], "depuis": 0, "attente": 0}
                else:
                    e["visites"].clear()
                avant = self.comparer(m, "marchand")
                couverts.update(c.urgence.palier for c in avant)
                reprise = recharger(m)
                self.assertEqual(signature(avant), signature(self.comparer(reprise, "marchand")))
                self.assertEqual(reprise.data, m.data)
                self.assertEqual(fiche(reprise), fiche(m))
                self.assertEqual(decrire_perception(reprise), decrire_perception(m))
        self.assertEqual(couverts, set(d.Palier) - {d.Palier.DESESPOIR})

    def test_ecarts_egalites_et_routines_issues_des_besoins_pressants(self):
        for ecarts in ((0, 0, 0), (10, 10, 5), (5, 10, 10)):
            with self.subTest(ecarts=ecarts):
                m = scene()
                e = lire(m, "marchand")
                e["visites"].clear()
                s = d.seuils(m, "marchand")
                for b, ecart in zip(("devoir", "biens", "securite"), ecarts):
                    e["besoins"][b] = s[b] + ecart
                candidats = self.comparer(m, "marchand")
                for c in candidats:
                    if c.urgence.palier == d.Palier.BESOIN_PRESSANT:
                        self.assertEqual(c.urgence.valeur, e["besoins"][c.besoin] - s[c.besoin])
                self.comparer(recharger(m), "marchand")

    def test_chaque_choix_de_dix_nuits_de_deux_heures(self):
        candidats = d._candidats
        compte = 0

        def comparer(m, qui):
            nonlocal compte
            # L'oracle A0 porte sur le choix historique sans agenda ; A4 a
            # maintenant des déclarations actives dans les données de la crue.
            if d.agendas.depart(m, qui):
                return candidats(m, qui)
            avant = list(anciens_candidats(m, qui))
            apres = list(candidats(m, qui))
            self.assertEqual(signature(avant), signature(apres), (scenario, graine, qui, m.data["minutes"]))
            compte += 1
            return iter(apres)

        joueurs = {"relais": "chambre_cloche", "mine": "galerie", "auberge": "dortoir",
                   "crue": "chambre_cloche", "rixe": "chambre_cloche"}
        with patch.object(d, "_candidats", comparer):
            for scenario, joueur in joueurs.items():
                for graine in (1985, 7):
                    with self.subTest(scenario=scenario, graine=graine):
                        avant = compte
                        banc_pnj.nuit(scenario, graine, 2, joueur)
                        self.assertGreater(compte, avant)

    def test_memes_actions_monde_et_textes_apres_rechargement(self):
        # Deux scènes réelles : la faim de Brune au Relais, les besoins des clients à l'auberge.
        def historique(m, qui):
            return (d.Candidat(*c, d.Urgence(d.Palier.BESOIN_PRESSANT, 0, (rang,)))
                    for rang, c in enumerate(anciens_candidats(m, qui)))

        for scenario in ("relais", "auberge"):
            with self.subTest(scenario=scenario):
                initial = banc_pnj.creer(scenario, 1985, "fixe")
                m, reference = recharger(initial), recharger(initial)
                textes, anciens_textes = [], []
                for _ in range(2):
                    moteur = Moteur(m)
                    textes.append(moteur.executer(moteur.preparer(proposition("attendre"))))
                    with patch.object(d, "_candidats", historique):
                        moteur = Moteur(reference)
                        anciens_textes.append(moteur.executer(moteur.preparer(proposition("attendre"))))
                    m, reference = recharger(m), recharger(reference)
                    for qui in pnjs(m):
                        self.assertEqual(signature(self.comparer(m, qui)),
                                         signature(self.comparer(reference, qui)))
                    self.assertEqual(m.data, reference.data)
                    self.assertEqual(textes, anciens_textes)
                    self.assertEqual(fiche(m), fiche(reference))
                    self.assertEqual(decrire_perception(m), decrire_perception(reference))
