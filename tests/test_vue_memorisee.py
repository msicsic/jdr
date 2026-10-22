"""La mémoire de la vue ne change rien à ce que chacun perçoit.

Pendant la vie des PNJ, positions, champs de vision et perceptions sont gardés tant que l'état dont
ils dépendent n'a pas changé (``spatial.etat_vue``), lignes de vue et champs d'une étape à l'autre
tant que les salles et la signature de la vue sont les mêmes. Ces tests comparent la perception
mémorisée à un calcul de zéro, fait comme avant la mémoire, à des instants tirés au hasard d'une
nuit au Relais.
"""
import json
import random
import unittest

from donjon import pnj, spatial
from donjon.banc_pnj import creer, executer
from donjon.esprits import _pertinent, percevoir, percus, pnjs
from donjon.geometrie import cases, distance, position_entree
from donjon.monde import Monde
from donjon.perception import CarteLumiere, eclairage


def ligne_reference(a, b, terrain, opaques):
    """La ligne de vue d'avant : le tracé complet, puis chaque case."""
    points = spatial._ligne(a, b)
    for i, p in enumerate(points[1:], 1):
        if p not in terrain or i < len(points) - 1 and p in opaques:
            return False
        avant = points[i - 1]
        if p[0] != avant[0] and p[1] != avant[1]:
            c1, c2 = (p[0], avant[1]), (avant[0], p[1])
            if (c1 not in terrain or c1 in opaques) and (c2 not in terrain or c2 in opaques):
                return False
    return True


def champ_reference(m, acteur):
    """Le champ de vision case par case, sans rien garder."""
    salle, position = spatial.position_acteur(m, acteur)
    lumiere = CarteLumiere(m, salle)
    origine = spatial._global(m.data["salles"][salle], position)
    orientation = spatial.orientation_acteur(m, acteur)
    vus = set()
    for s in lumiere.salles:
        piece = m.data["salles"][s]
        for x, y in cases(piece):
            cible = spatial._global(piece, (x, y))
            if not spatial.dans_le_cone(origine, orientation, cible):
                continue
            niveau = lumiere.niveau(cible)
            portee = spatial.PORTEE_VUE[2 if niveau == 2 or lumiere.directe(cible) else 1] if niveau else -1
            if distance(cible, origine) > portee:
                continue
            if (ligne_reference(origine, cible, lumiere.terrain, lumiere.opaques)
                    and ligne_reference(cible, origine, lumiere.terrain, lumiere.opaques)):
                vus.add((s, x, y))
    return vus


def visible_reference(m, id, acteur, champ):
    """Toutes les salles, toutes les places de l'objet, le mur qui porte un objet accroché."""
    if id not in m.objets or id == acteur:
        return False
    o = m.objets[id]
    salle_acteur = m.joueur["salle"] if acteur == "joueur" else m.objets[acteur]["lieu"]
    if o["type"] == "surface" and o.get("lieu") == salle_acteur:
        return any(c[0] == o["lieu"] for c in champ)
    for salle in m.data["salles"]:
        p = spatial.position_cible(m, id, salle)
        if p is not None and (salle, p[0], p[1]) in champ:
            ancrage = o.get("ancrage_carte")
            if ancrage and tuple(ancrage) not in spatial.murs_visibles(m, champ, acteur).get(salle, set()):
                continue
            return True
    return False


def percus_reference(m, acteur):
    salle = m.objets[acteur]["lieu"]
    vus = {id: (None, None) for id, o in m.objets.items()
           if spatial.porte_par(m, id, acteur) and _pertinent(m, acteur, o)}
    if salle not in m.data["salles"]:
        return vus, set()
    champ = champ_reference(m, acteur)
    for id, o in m.objets.items():
        if id in vus or not _pertinent(m, acteur, o) or not visible_reference(m, id, acteur, champ):
            continue
        vus[id] = next((s, list(p)) for s in m.data["salles"] for p in [spatial.position_cible(m, id, s)]
                       if p is not None and (s, p[0], p[1]) in champ)
    j = m.joueur
    if (j["salle"], *j["position"]) in champ:
        vus["joueur"] = (j["salle"], list(j["position"]))
    return vus, champ


def nuit(graine):
    m = creer("relais", graine, "fixe")
    m.joueur.update(salle="chambre_cloche", position=list(position_entree(m, "chambre_cloche")))
    return m


class VueMemoriseeTests(unittest.TestCase):
    def setUp(self):
        spatial._MEMOIRE.__dict__.clear()

    def comparer(self, m):
        """La perception mémorisée (dans la vie des PNJ) égale celle calculée de zéro."""
        attendus = {}
        with spatial.sans_memoire(m):
            for id in pnjs(m):
                attendus[id] = percus_reference(m, id)
            champ_joueur = champ_reference(m, "joueur")
            vus_joueur = {id: visible_reference(m, id, "joueur", champ_joueur) for id in m.objets}
            lumieres = {id: eclairage(m, m.objets[id]["lieu"], m.objets[id]["position"]) for id in pnjs(m)}
        for id in pnjs(m):
            self.assertEqual(percus(m, id), attendus[id], id)
            self.assertEqual(eclairage(m, m.objets[id]["lieu"], m.objets[id]["position"]), lumieres[id], id)
        self.assertEqual(spatial.champ_visible(m, "joueur"), champ_joueur)
        self.assertEqual({id: spatial.visible(m, id) for id in m.objets}, vus_joueur)

    def test_instants_tires_au_hasard_d_une_nuit(self):
        """Après des gestes tirés au hasard, toute la nuit : chaque PNJ et le joueur."""
        hasard, comparaisons, agir = random.Random(7), [], pnj.agir

        def agir_et_comparer(monde, id, t, lignes, gestes=None, compter=True):
            duree = agir(monde, id, t, lignes, gestes, compter)
            if hasard.random() < 0.08:
                self.assertIsNotNone(getattr(monde, "_cache_vue", None), "hors de la vie des PNJ")
                self.comparer(monde)
                comparaisons.append(t)
            return duree
        pnj.agir = agir_et_comparer
        try:
            m = nuit(1985)
            executer(m, 480)
        finally:
            pnj.agir = agir
        self.assertGreater(len(comparaisons), 50)

    def test_verification_complete_sur_une_heure(self):
        """Chaque lecture mémorisée recomparée à un calcul de zéro ; un bloc figé ne change rien."""
        spatial.VERIFICATION = 1.0
        try:
            m = nuit(42)
            executer(m, 60)
        finally:
            spatial.VERIFICATION = 0.0

    def test_ligne_de_vue_case_par_case_egale_le_trace_complet(self):
        """Toutes les paires de cases d'une zone avec murs, obstacles et diagonales bouchées."""
        hasard = random.Random(3)
        cases_zone = [(x, y) for x in range(-1, 9) for y in range(-1, 9)]
        for _ in range(20):
            terrain = {c: None for c in cases_zone if hasard.random() < 0.8}
            opaques = {c for c in cases_zone if hasard.random() < 0.15}
            for a in hasard.sample(cases_zone, 15):
                for b in cases_zone:
                    self.assertEqual(spatial._los_global(None, a, b, terrain, opaques),
                                     ligne_reference(a, b, terrain, opaques), (a, b))

    def test_un_changement_d_etat_renouvelle_la_perception(self):
        """Clé sûre : un regard tourné, un objet déplacé, chaque flamme, chaque porte, le joueur qui
        marche, un PNJ qui change de salle : la lecture suivante, dans le même bloc de mémoire, est
        celle d'un calcul de zéro, pour chaque PNJ et pour le joueur."""
        m = nuit(1985)
        executer(m, 30)
        id = pnjs(m)[0]
        o = m.objets[id]
        with spatial.vue_memorisee(m):
            avant = percus(m, id)
            self.assertEqual(percus(m, id), avant)
            for orientation in ("nord", "sud", "est", "ouest", None):
                if orientation is None:
                    o.pop("orientation")
                else:
                    o["orientation"] = orientation
                self.comparer(m)
            objet = next(k for k, x in m.objets.items() if x.get("mobile") and x["lieu"] in m.data["salles"]
                         and k not in percus(m, id)[0])
            m.objets[objet].update(lieu=o["lieu"], position_salle=o["lieu"], position=list(o["position"]))
            self.assertIn(objet, percus(m, id)[0])
            self.comparer(m)
            # Seul son lieu change : pris en main, puis rangé dans un contenant fermé, puis reposé.
            m.objets[objet]["lieu"] = id
            self.assertEqual(percus(m, id)[0][objet], (None, None))
            self.comparer(m)
            contenant = next(k for k, x in m.objets.items() if x["type"] == "contenant")
            ouvert = m.objets[contenant]["ouverte"]
            m.objets[contenant]["ouverte"] = False
            m.objets[objet]["lieu"] = contenant
            self.comparer(m)
            m.objets[contenant]["ouverte"] = ouvert
            m.objets[objet]["lieu"] = o["lieu"]
            self.comparer(m)
            # Seule la salle de sa case change : sa case n'y vaut plus, il revient à l'entrée.
            m.objets[objet]["position_salle"] = next(s for s in m.data["salles"] if s != o["lieu"])
            self.comparer(m)
            for source in [k for k, x in m.objets.items() if "allume" in x]:
                for allume in (not m.objets[source]["allume"], m.objets[source]["allume"]):
                    m.objets[source]["allume"] = allume
                    self.comparer(m)
            for porte in [k for k, x in m.objets.items() if "ouverte" in x]:
                m.objets[porte]["ouverte"] = not m.objets[porte]["ouverte"]
                self.comparer(m)
            j = m.joueur
            for case in sorted(cases(m.data["salles"][j["salle"]]))[:12]:
                j["position"] = list(case)
                self.comparer(m)
            ailleurs = next(s for s in m.data["salles"] if s != o["lieu"])
            o.update(lieu=ailleurs, position_salle=ailleurs, position=list(position_entree(m, ailleurs)))
            self.comparer(m)

    def test_recharger_en_cours_de_nuit_ne_change_rien(self):
        """Une partie rechargée (un autre monde, mêmes salles) reprend la mémoire de la géométrie :
        la suite de la nuit et ce que perçoivent PNJ et joueur sont ceux d'une nuit d'un trait."""
        d_un_trait = nuit(2024)
        chronique, _ = executer(d_un_trait, 120)
        spatial._MEMOIRE.__dict__.clear()
        m = nuit(2024)
        debut, _ = executer(m, 60)
        recharge = Monde(json.loads(json.dumps(m.data)))
        suite, _ = executer(recharge, 120)
        self.assertEqual(debut + suite, chronique)
        self.assertEqual(json.dumps(recharge.data, sort_keys=True), json.dumps(d_un_trait.data, sort_keys=True))
        for id in pnjs(recharge):
            percevoir(recharge, id)
            self.assertEqual(percus(recharge, id), percus_reference(recharge, id))
        self.assertEqual({id: recharge.visible(id) for id in recharge.objets},
                         {id: d_un_trait.visible(id) for id in d_un_trait.objets})


if __name__ == "__main__":
    unittest.main()
