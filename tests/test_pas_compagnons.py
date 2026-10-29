"""Attribution des gestes ordinaires : présence crue mobile, jamais position réelle."""
import copy
import gzip
import json
from pathlib import Path
import unittest

from donjon.banc_pnj import creer
from donjon.ecoute import entendus, rendre, ENTENDU
from donjon.esprits import croire, lire
from donjon.ouie import _crus_la, retentir
from donjon.rendu import decrire_contexte
from donjon.temps import ecouler
from tests.support import calme, lier
from tests.test_tensions import placer, recharger


def scene(scenario="relais", auditeur="ilse", auteur="aubin", salle="antichambre"):
    m = creer(scenario, 1, depart="fixe")
    calme(m, *[i for i, o in m.objets.items() if o.get("profil")])
    placer(m, auditeur, salle, (4, 5))
    m.objets[auditeur]["orientation"] = "est"
    placer(m, auteur, salle, (1, 3))
    lier(m, auditeur, auteur, True)
    # La dernière perception était trois cases plus loin, la minute précédente.
    croire(m, auditeur, auteur, "lieu", salle, "vu", salle=salle, case=[1, 6])
    m.data.update(minutes=1, dixiemes=0)
    m.joueur.update(salle=salle, position=[7, 3], orientation="est")
    return recharger(m)


def hameau_1985_service_annonce():
    """Rejouer explicitement l'offre historique par le contrat typé, puis laisser vivre."""
    from unittest.mock import patch
    from donjon.geometrie import position_entree
    from donjon.monde import Monde
    from donjon.pnj_propositions import executer
    from donjon.esprits import percevoir_tous
    from tests.test_tensions import placer
    from tests.support import regarder
    from donjon.deplacement_objet import deplacer
    m = creer('crue_hameau', 1985)
    m.joueur.update(salle='chambre_cloche', position=list(position_entree(m, 'chambre_cloche')))
    placer(m, 'brune', 'antichambre', [2, 3])
    placer(m, 'ilse', 'antichambre', [2, 4])
    # Torche remise à la prestataire pour l'allumage : elle la connaît en main,
    # sans découvrir un objet dans l'ombre par une position réelle cachée.
    deplacer(m, 'torche', 'brune')
    m.objets['torche']['proprietaire'] = 'ilse'
    regarder(m, 'brune', 'ilse')
    regarder(m, 'ilse', 'brune')
    percevoir_tous(m)
    contenu = {'demande': {'type': 'pieces', 'montant': 1},
               'contrepartie': {'type': 'tache', 'condition': {'objet': 'torche', 'allume': True}}}
    lire(m, 'brune')['intention'] = {'but': {'type': 'proposition', 'objet': 'ilse'},
                                    'motif': 'argent', 'depuis': 0, 'attente': 0, 'plan': []}
    with patch.object(Monde, 'd20', return_value=20):
        assert executer(m, 'brune', 'ilse', contenu, [])
    return m


class PasCompagnonsTests(unittest.TestCase):
    def test_alerte_aubin_crue_2024_autre_moyen_apres_refus(self):
        from donjon.deliberation import choisir
        from donjon.monde import Monde
        from donjon.pnj import avancer

        fichier = Path(__file__).parent / 'data/pas-233-aubin-crue-2024-23576.json.gz'
        original = Monde(json.loads(gzip.decompress(fichier.read_bytes())))
        etats = []
        for laps in ([100], [50, 50]):
            m = self.stable(original.copier())
            e = lire(m, 'aubin')
            refus = copy.deepcopy(e['refus'])
            self.assertEqual(e['manque']['etape']['operation'], 'demander')
            choisir(m, 'aubin', m.data['minutes'])
            # Le refus portait sur le lot ; Aubin tient déjà deux parts reçues
            # de ce lot (provenance publiée). Il sert la sienne au lieu de
            # redemander ou d'ouvrir la réserve d'autrui.
            self.assertEqual(e['intention']['but'],
                             {'type': 'pulsion', 'objet': 'vivres_1', 'servir': 'brune'})
            self.assertEqual([x['operation'] for x in e['intention']['plan']], ['servir'])
            self.assertEqual(e['refus'], refus)
            demandes = [c for c in m.data['chronique'] if c['pnj'] == 'aubin' and 'demande une part' in c['texte']]
            for dt in laps:
                ecouler(m, dt)
                avancer(m, 0, [], dixiemes=dt)
                m = self.stable(m)
            # Le témoin empêche toujours le vol : aucun refus oublié ni
            # nourriture attribuée à distance au bénéficiaire.
            self.assertFalse(m.objets['reserve']['ouverte'])
            self.assertEqual(demandes, [c for c in m.data['chronique']
                                       if c['pnj'] == 'aubin' and 'demande une part' in c['texte']])
            etats.append(m.data)
        self.assertEqual(*etats)

    def test_promesse_hameau_1985_annoncee_retrouvee_apres_recharge(self):
        from donjon.banc_pnj import executer
        from donjon.geometrie import position_entree

        def depart():
            return recharger(hameau_1985_service_annonce())

        a, b = depart(), depart()
        # La parole et l'engagement pris sont bien sauvegardés avant le travail.
        self.assertTrue([c for c in a.data["chronique"] if c["pnj"] == "brune"
                         and "propose à Ilse la promesse que la torche soit allumée" in c["texte"]
                         and "(accepte)" in c["texte"]])
        self.assertTrue([s for s in lire(a, "brune")["memoire"]
                         if s["type"] == "engagement_pris" and s.get("pour") == "ilse"])
        executer(a, 2)
        for _ in range(2):
            executer(b, 1)
            b = self.stable(b)
        a = self.stable(a)
        self.assertEqual(a.data, b.data)
        # Le banc peut achever l'attente à cinq minutes ; la chronique (300)
        # et la mémoire (40) sont bornées. Le résultat tenu remplace alors
        # l'ancien engagement pris, sans perdre le service payé.
        self.assertTrue([s for s in lire(a, 'brune')['memoire']
                         if s['type'] == 'engagement_tenu' and s.get('pour') == 'ilse'])
        # 234 : le placement conservait ici Ilse connue à l'antichambre au
        # constat. Le contrat 273 avance d'une minute le constat de la torche :
        # la croyance de Brune sur Ilse est encore vide à ce moment, et
        # l'ancrage enregistre donc un bénéficiaire non localisé.
        self.assertIn(dict(de='brune', pour='ilse', condition={'objet': 'torche', 'allume': True},
                           lieu_beneficiaire=None), a.data['services_rendus'])

    def test_hameau_1985_service_admissible_mais_vente_compensee_prioritaire(self):
        from unittest.mock import patch
        from donjon import banc_pnj, echanges
        from donjon.geometrie import position_entree
        m = creer('crue_hameau', 1985)
        m.joueur.update(salle='chambre_cloche', position=list(position_entree(m, 'chambre_cloche')))
        services, ventes = [], []
        sensee, proposer = echanges.offre_sensee, echanges.proposer

        def juger(monde, de, a, demande, terme, **options):
            r = sensee(monde, de, a, demande, terme, **options)
            if (de == 'brune' and a == 'ilse' and demande == {'type': 'pieces', 'montant': 1}
                    and terme == {'type': 'tache', 'condition': {'objet': 'torche', 'allume': True}}):
                services.append(r)
            return r

        def proposer_vu(monde, de, a, demande, terme, **options):
            if de == 'brune' and terme == {'type': 'objet', 'objet': 'crochets'}:
                bilan = echanges.evaluer_proposition(monde, a, de, terme, demande)
                self.assertIsNone(bilan['cause'])
                self.assertGreaterEqual(bilan['G'], bilan['P'])
                self.assertEqual(demande, {'type': 'pieces', 'montant': 8})
                ventes.append(a)
            return proposer(monde, de, a, demande, terme, **options)

        with patch.object(echanges, 'offre_sensee', juger), patch.object(echanges, 'proposer', proposer_vu):
            banc_pnj.executer(m, 2)
        m = self.stable(m)
        self.assertTrue(services)
        # Au premier choix ce service reste admissible ; des états projetés
        # ultérieurs peuvent changer son intérêt, pas établir une cession.
        self.assertTrue(services[0])
        # Les deux premiers acheteurs restent les mêmes ; l'ordre d'Aubin et
        # de Mael s'inverse depuis le contrat 273 (le monde de la scène change
        # d'une minute), sans changer la vente compensée qui l'emporte.
        self.assertEqual(ventes[:2], ['ilse', 'mael'])
        self.assertEqual(sorted(ventes[2:]), ['aubin', 'marchand'])
        from donjon.biens import proprietaire
        self.assertEqual(proprietaire(m, 'crochets'), 'brune')
        self.assertEqual(m.objets['crochets']['lieu'], 'brune')
        self.assertFalse([s for s in lire(m, 'brune')['memoire']
                          if s['type'] == 'engagement_pris' and s.get('pour') == 'ilse'])

    def test_aubin_saisit_l_occasion_de_demander_a_gorm_hameau_et_relais(self):
        """Reconstitution de la demande de vivres perdue au hameau 1985.

        Aubin attend encore ; Gorm marche dans son dos. Le son, puis la vie
        autonome, doivent mener à une vraie demande et une parole enregistrée.
        """
        from donjon.corps import valeurs
        from donjon.pnj import avancer

        def vivre(scenario, laps):
            m = scene(scenario, "aubin", "marchand", "antichambre")
            m.data["dixiemes"] = 30
            for id, o in m.objets.items():
                if o.get("profil"):
                    lire(m, id).update(libre=1200, veille=None, eveil=None)
            lire(m, "aubin").update(libre=630, veille=1200, eveil=None, intention=None)
            valeurs(m, "aubin")["faim"] = 80
            m = recharger(m)
            orientation = m.objets["aubin"]["orientation"]
            retentir(m, "marchand", "aller")
            self.assertEqual(orientation, m.objets["aubin"]["orientation"])
            for d in laps:
                ecouler(m, d)
                avancer(m, 0, [], dixiemes=d)
                m = self.stable(m)
            return m

        for scenario in ("crue_hameau", "relais"):
            with self.subTest(scenario=scenario):
                a = vivre(scenario, [500])
                b = vivre(scenario, [150, 150, 200])
                self.assertEqual(a.data, b.data)
                self.assertTrue([c for c in a.data["chronique"] if c["pnj"] == "aubin"
                                 and "demande une part" in c["texte"] and "(promis)" in c["texte"]])
                self.assertTrue([s for s in lire(a, "marchand")["memoire"]
                                 if s["type"] == "engagement_pris" and s.get("pour") == "aubin"])
                self.assertEqual({"type": "part", "objet": "vivres", "de": "marchand"},
                                 lire(a, "aubin")["intention"]["but"])

    def test_presence_attribuee_reveille_sans_vue_ni_position_inventee(self):
        from donjon.pnj import pourraient_se_parler, se_parler
        from donjon.temps import instant
        for args in (("crue_hameau", "mael", "aubin", "antichambre"),
                     ("auberge", "odile", "hugues", "salle_commune")):
            with self.subTest(scenario=args[0]):
                m = scene(*args)
                auditeur, auteur = args[1:3]
                e = lire(m, auditeur)
                e["eveil"] = None
                avant = copy.deepcopy(e["croyances"][auteur]["lieu"])
                orientation = m.objets[auditeur]["orientation"]
                libre = e["libre"]
                self.assertNotIn(auditeur, retentir(m, auteur, "aller"))
                m = self.stable(m)
                e = lire(m, auditeur)
                self.assertEqual(instant(m), e["eveil"])
                self.assertEqual(avant, e["croyances"][auteur]["lieu"])
                self.assertEqual(orientation, m.objets[auditeur]["orientation"])
                self.assertEqual(libre, e["libre"])
                self.assertTrue(pourraient_se_parler(m, auditeur, auteur))
                self.assertTrue(se_parler(m, auditeur, auteur))
                self.stable(m)

    def test_attribution_erronee_ne_permet_pas_de_parler_au_compagnon_absent(self):
        from donjon.pnj import pourraient_se_parler, se_parler
        m = scene()
        placer(m, "aubin", "crypte", (1, 3))
        placer(m, "brune", "antichambre", (1, 3))
        lire(m, "ilse")["croyances"].pop("brune", None)
        retentir(m, "brune", "aller")
        m = self.stable(m)
        self.assertFalse(pourraient_se_parler(m, "ilse", "aubin"))
        self.assertFalse(se_parler(m, "ilse", "aubin"))
        self.assertNotIn("brune", lire(m, "ilse")["croyances"])
        self.stable(m)

    def test_bruit_inconnu_ne_devient_pas_presence_identifiee(self):
        m = scene()
        placer(m, "ilse", "echoppe", (8, 3))
        m.objets["ilse"]["orientation"] = "ouest"
        lire(m, "ilse")["croyances"].pop("aubin", None)
        retentir(m, "aubin", "aller")
        m = self.stable(m)
        self.assertNotIn("aubin", lire(m, "ilse")["croyances"])
        self.assertTrue([s for s in lire(m, "ilse")["memoire"] if s["type"] == "bruit"])
        self.assertFalse([s for s in lire(m, "ilse")["memoire"]
                          if s["type"] == "bruit" and s.get("qui")])


    def stable(self, m):
        avant = copy.deepcopy(m.data)
        rendu = (decrire_contexte(m), rendre(m, entendus(m, -1, ENTENDU)))
        recharge = recharger(m)
        self.assertEqual(avant, recharge.data)
        self.assertEqual(rendu, (decrire_contexte(recharge), rendre(recharge, entendus(recharge, -1, ENTENDU))))
        return recharge

    def test_voisins_hors_du_cone_relais_et_autre_cas_auberge(self):
        for args in (("relais", "ilse", "aubin", "antichambre"),
                     ("auberge", "odile", "hugues", "salle_commune")):
            with self.subTest(scenario=args[0]):
                m = scene(*args)
                orientation = m.objets[args[1]]["orientation"]
                presence = copy.deepcopy(lire(m, args[1])["croyances"][args[2]]["lieu"])
                for geste in ("aller", "prendre", "aller"):
                    self.assertNotIn(args[1], retentir(m, args[2], geste))
                    m = self.stable(m)
                self.assertEqual(orientation, m.objets[args[1]]["orientation"])
                self.assertFalse([s for s in lire(m, args[1])["memoire"] if s["type"] == "bruit"])
                self.assertEqual(presence, lire(m, args[1])["croyances"][args[2]]["lieu"])

    def test_mael_entend_le_refuge_depuis_une_autre_salle(self):
        m = scene("crue_hameau", "mael", "aubin")
        placer(m, "mael", "echoppe", (8, 3))
        m.objets["mael"]["orientation"] = "ouest"
        placer(m, "aubin", "antichambre", (0, 3))
        # Il croit Aubin au refuge ; l'ouïe ne situe pas sa case à travers la cloison.
        retentir(m, "aubin", "aller")
        m = self.stable(m)
        self.assertFalse([s for s in lire(m, "mael")["memoire"] if s["type"] == "bruit"])
        self.assertEqual("entendu", lire(m, "mael")["croyances"]["aubin"]["lieu"]["source"])

    def test_fracas_et_appel_restent_inhabituels(self):
        for nature in ("bruyant", "appel"):
            m = scene()
            placer(m, "ilse", "echoppe", (8, 3))
            m.objets["ilse"]["orientation"] = "ouest"
            retentir(m, "aubin", "forcer", force=nature)
            m = self.stable(m)
            self.assertTrue([s for s in lire(m, "ilse")["memoire"] if s["type"] == "bruit"])

    def test_expiration_absence_et_depart_crus(self):
        for cause in ("expire", "absent", "parti"):
            m = scene()
            if cause == "expire":
                m.data["minutes"] = 31
            elif cause == "absent":
                croire(m, "ilse", "aubin", "lieu", None, "vu", salle="antichambre", case=None)
            else:
                croire(m, "ilse", "aubin", "etat", {"parti": True}, "vu")
            m = recharger(m)
            self.assertNotIn("aubin", _crus_la(m, "ilse", "antichambre", [1, 3]))
            self.assertIn("ilse", retentir(m, "aubin", "aller"))
            self.stable(m)

    def test_distance_incompatible_et_frontiere_du_temps_fin(self):
        m = scene()
        m.data.update(minutes=0, dixiemes=15)
        self.assertNotIn("aubin", _crus_la(m, "ilse", "antichambre", [1, 3]))
        ecouler(m, 15)
        self.assertIn("aubin", _crus_la(m, "ilse", "antichambre", [1, 3]))
        self.stable(m)

    def test_meprise_sans_consulter_la_position_reelle(self):
        m = scene()
        placer(m, "aubin", "crypte", (1, 3))
        placer(m, "brune", "antichambre", (1, 3))
        lire(m, "ilse")["croyances"].pop("brune", None)
        presence = copy.deepcopy(lire(m, "ilse")["croyances"]["aubin"]["lieu"])
        retentir(m, "brune", "aller")
        m = self.stable(m)
        self.assertEqual(presence, lire(m, "ilse")["croyances"]["aubin"]["lieu"])
        self.assertNotIn("brune", lire(m, "ilse")["croyances"])

    def test_la_mefiance_porte_sur_la_meme_personne_que_l_attribution(self):
        from donjon.relations import se_mefie
        m = scene()
        m.data["minutes"] = 0
        croire(m, "ilse", "brune", "lieu", "antichambre", "vu", salle="antichambre", case=[7, 5])
        lier(m, "ilse", "brune", False)
        m.data["minutes"] = 1
        self.assertTrue(se_mefie(m, "ilse", "brune"))
        presence = copy.deepcopy(lire(m, "ilse")["croyances"]["aubin"]["lieu"])
        self.assertNotIn("ilse", retentir(m, "aubin", "aller"))
        m = self.stable(m)
        self.assertEqual(presence, lire(m, "ilse")["croyances"]["aubin"]["lieu"])
        self.assertEqual("vu", lire(m, "ilse")["croyances"]["brune"]["lieu"]["source"])

    def test_joueur_meme_attribution_sans_revelation_au_rendu(self):
        m = scene()
        croire(m, "joueur", "aubin", "lieu", "antichambre", "entendu", salle="antichambre", case=[1, 6])
        retentir(m, "aubin", "aller")
        m = self.stable(m)
        self.assertEqual("entendu", lire(m, "joueur")["croyances"]["aubin"]["lieu"]["source"])
        texte = " ".join(rendre(m, entendus(m, -1, ENTENDU)))
        self.assertIn("pas", texte)
        self.assertNotIn("Aubin", texte)

    def test_une_compatibilite_de_marche_ne_se_confirme_pas_elle_meme(self):
        m = scene()
        presence = copy.deepcopy(lire(m, "ilse")["croyances"]["aubin"]["lieu"])
        for minute in (1, 10, 20, 30):
            m.data["minutes"] = minute
            self.assertNotIn("ilse", retentir(m, "aubin", "aller"))
            m = self.stable(m)
            self.assertEqual(presence, lire(m, "ilse")["croyances"]["aubin"]["lieu"])
        m.data["minutes"] = 31
        self.assertNotIn("aubin", _crus_la(m, "ilse", "antichambre", [1, 3]))

    def test_localisation_acoustique_dans_la_zone_deja_crue(self):
        m = scene()
        croire(m, "ilse", "aubin", "lieu", "antichambre", "vu", salle="antichambre", case=[1, 4])
        self.assertNotIn("ilse", retentir(m, "aubin", "aller"))
        m = self.stable(m)
        c = lire(m, "ilse")["croyances"]["aubin"]["lieu"]
        self.assertEqual((c["source"], c["case"], c["minute"]), ("entendu", [1, 3], 1))

    def test_meme_laps_entier_ou_decoupe_recharge(self):
        a, b = scene(), scene()
        ecouler(a, 45)
        for _ in range(3):
            ecouler(b, 15)
            b = recharger(b)
        retentir(a, "aubin", "aller")
        retentir(b, "aubin", "aller")
        self.assertEqual(self.stable(a).data, self.stable(b).data)

    def test_temoin_illicite_reconnait_la_presence_mobile_crue(self):
        from donjon.pnj import commencer_geste, temoigner_en_cours
        from tests.test_ouie_temoins import odon_au_coffre
        m = odon_au_coffre(True)
        croire(m, "bram", "odon", "lieu", "bureau", "vu", salle="bureau", case=[1, 4])
        m.data.update(minutes=1, dixiemes=0)
        commencer_geste(m, "odon", "crocheter", "coffre_paie", 1200, nature="bruyant")
        temoigner_en_cours(m)
        m = self.stable(m)
        self.assertTrue([s for s in lire(m, "bram")["memoire"]
                         if s["type"] == "vu_agir" and s["auteur"] == "odon" and s.get("par") == "ouie"])

    def test_marche_executee_et_temps_decoupe_dans_la_mine(self):
        from tests.test_ouie import mine_baraquement
        from tests.test_ouie_temoins import etat
        from donjon.pnj import avancer
        def vivre(laps):
            m = mine_baraquement("josse")
            for d in laps:
                ecouler(m, d)
                avancer(m, 0, [], dixiemes=d)
                m = recharger(m)
            return m
        a, b = vivre([600]), vivre([150, 150, 300])
        self.assertEqual(etat(a), etat(b))
        for m in (a, b):
            m = self.stable(m)
            self.assertFalse([c for c in m.data.get("chronique", [])
                              if c["pnj"] == "josse" and "se retourne au bruit" in c["texte"]])
