"""Offres conditionnelles : vraie boucle console/MJ simulé et monde rechargé."""
import copy
import unittest

from donjon.biens import compte, offres_joueur
from donjon.dialogues import preparer_conversation
from donjon.monde import nouveau_monde
from donjon.propositions import offre
from donjon.narration import controler, consigner
from donjon.rendu import decrire_accords, fiche
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_dialogues import conversation, reponse
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import placer, recharger


def scene():
    m = nouveau_monde()
    m.joueur.update(salle="echoppe", position=[3, 1], orientation="est")
    placer(m, "marchand", "echoppe", [4, 1])
    return recharger(m)


def audit(citation, comptes, locuteur="marchand", verdict="parole"):
    l = ligne(verdict, sources=["comptes"], locuteur=locuteur, citation=citation)
    l.update(comptes=comptes, portee_mecanique="etablie")
    return rapport(l)


class PrimeOffreTests(unittest.TestCase):
    def test_prime_reelle_offre_et_discussion_sans_dette_ni_repli(self):
        for typed in (False, True):
            m = scene()
            mots = "Gorm, combien me donnes-tu pour l'anneau ?"
            citation = "Je te donnerai 20 pièces si tu me rapportes l'anneau."
            o = offre("marchand", "joueur", {"type": "objet", "objet": "anneau"},
                      {"type": "pieces", "montant": 20})
            avant = m.joueur["or"]
            premier = reponse(conversation(sujet=mots)) if typed else parole(mots, personnage="marchand")
            r, sortie, appels = jouer(m, mots, [premier, dialogue(f'Gorm : « {citation} »')],
                                     [audit(citation, [o])])
            self.assertIn(citation, sortie)
            self.assertIn(citation, str(r.data["conversation"]))
            self.assertEqual(r.data["paroles_pnj"][-1]["texte"], citation)
            self.assertEqual(r.joueur["or"], avant)
            self.assertFalse(r.data.get("dettes"))
            self.assertNotIn("te doit 20", fiche(r))
            self.assertFalse(any("controle_narratif" in e for _, e in appels))
            self.assertEqual(len(appels), 3)
            self.assertEqual(r.data["engagements"].get("anneau_veilleur", {}).get("statut"),
                             "propose" if typed else None)

    def test_offre_fausse_dette_montant_condition_et_sens_refuses(self):
        m = scene()
        o = offres_joueur(m)[0]
        for faux in (compte("marchand", "joueur", montant=20),
                     {**o, "contrepartie": {"type": "pieces", "montant": 10}},
                     {**o, "condition": {"type": "objet", "objet": "couteau"}},
                     {**o, "debiteur": "joueur", "creancier": "marchand"}):
            citation = "Je te donnerai 20 pièces si tu me rapportes l'anneau."
            faits = {"comptes": {"etat": [], "offres": [o]}, "interlocuteurs": {"marchand": {}}}
            controle = controler(f'« {citation} »', audit(citation, [faux]), faits)
            self.assertTrue(controle["obstacles"])
            self.assertIn("attendu", controle["obstacles"][0])

    def test_remise_paie_dans_le_bon_sens_sans_solde_apres_recharge(self):
        m = scene()
        m, _ = preparer_conversation(m, conversation())
        m, _ = preparer_conversation(m, conversation("accepter"))
        m.objets["anneau"].update(lieu="joueur", proprietaire="joueur")
        m = recharger(m)
        self.assertFalse(m.data.get("dettes"))
        self.assertEqual(offres_joueur(m)[0]["contrepartie"]["montant"], 20)
        or_avant = m.joueur["or"]
        r, sortie, _ = jouer(m, "remettre anneau à Gorm", [], [])
        self.assertIn("20 pièces convenues", sortie)
        self.assertEqual(r.joueur["or"], or_avant + 20)
        self.assertEqual(r.data["finances_pnj"]["marchand"], 30)
        self.assertEqual(r.objets["anneau"]["lieu"], "marchand")
        self.assertEqual(r.data["engagements"]["anneau_veilleur"]["statut"], "paye")
        self.assertEqual(offres_joueur(r), [])
        self.assertFalse(r.data.get("dettes"))
        self.assertIn("récompense payée", decrire_accords(r))
        # Le récit du résultat dispose lui aussi du règlement typé, après le vrai geste.
        from unittest.mock import patch
        from donjon.mj import MJOpenAI
        texte = "Tu reçois les 20 pièces convenues."
        c = compte("marchand", "joueur", montant=20, etat="rendu")
        with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
              patch.object(MJOpenAI, "_appeler_brut", side_effect=[dialogue(texte),
                  audit(texte, [c], locuteur="", verdict="mecanique")])):
            recit = MJOpenAI().raconter_resultat(r, {
                "intention": "remettre l'anneau", "gestes": [], "faits": [texte]})
        self.assertEqual(recit["texte"], texte)
        self.assertEqual(recit["_audit"]["faits"]["comptes"]["issue"], [c])
        consigner(r, recit)
        r = recharger(r)
        self.assertEqual(r.data["narrations_mj"][-1]["texte"], texte)
        self.assertEqual(r.joueur["or"], or_avant + 20)

    def test_autre_offre_du_joueur_contre_promesse_differee(self):
        from tests.test_propositions import scene as marche, PART, TACHE
        from donjon.agendas import en_cours
        m = marche()
        m.objets["brasero"]["allume"] = False
        mots = "Gorm, une part de vivres contre ma promesse d'allumer le brasero."
        premier = parole(mots, personnage="marchand")
        premier["proposition"]["contenu"] = [{"type": "proposition", "demande": PART, "contrepartie": TACHE}]
        citation = "J'accepte une part de vivres contre ta promesse d'allumer le brasero."
        o = offre("joueur", "marchand", PART, TACHE)
        avant = m.objets["vivres"]["portions"]
        r, sortie, appels = jouer(m, mots, [premier, dialogue(f'Gorm : « {citation} »')],
                                 [audit(citation, [o])])
        self.assertIn(citation, sortie)
        self.assertIn(citation, str(r.data["conversation"]))
        self.assertFalse(any("controle_narratif" in e for _, e in appels))
        self.assertEqual(r.objets["vivres"]["portions"], avant - 1)
        self.assertEqual(en_cours(r, "joueur")[0]["condition"], TACHE["condition"])
        self.assertFalse(r.objets["brasero"]["allume"])
        self.assertFalse(r.data.get("dettes"))

    def test_garde_refait_a_l_enregistrement(self):
        m = scene()
        o = offres_joueur(m)[0]
        citation = "Je te donnerai 20 pièces si tu me rapportes l'anneau."
        texte = f'Gorm : « {citation} »'
        faits = {"comptes": {"etat": [], "offres": [o]}, "interlocuteurs": {"marchand": {}}}
        a = controler(texte, audit(citation, [o]), faits)
        a.update(faits=faits, texte_initial=texte, fondement=texte, fondement_paroles="")
        a["segments"][0]["comptes"][0] = {**o, "condition": {"type": "objet", "objet": "couteau"}}
        avant = copy.deepcopy(m.data)
        from donjon.monde import ErreurMonde
        with self.assertRaises(ErreurMonde):
            consigner(m, {**dialogue(texte), "_audit": a})
        self.assertEqual(m.data, avant)
