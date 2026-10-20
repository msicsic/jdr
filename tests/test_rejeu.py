"""Le rejeu du banc : il observe la nuit sans la changer, et rejoue à chaque instant ce qui a été."""
import hashlib
import json
import re
import unittest

from donjon.banc_pnj import creer, executer
from donjon.esprits import lire
from donjon.geometrie import position_entree
from donjon.rejeu import Enregistreur, page


def nuit(minutes, enregistrer):
    m = creer("relais", 7)
    m.joueur.update(salle="chambre_cloche", position=list(position_entree(m, "chambre_cloche")))
    enregistreur = Enregistreur(m) if enregistrer else None
    if enregistreur:
        with enregistreur.observer():
            chronique, mesures = executer(m, minutes)
    else:
        chronique, mesures = executer(m, minutes)
    empreinte = hashlib.sha1(json.dumps([chronique, mesures, m.data], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return m, chronique, enregistreur, empreinte


def rejouer(piste, jusqua):
    etat = {}
    for instant, changes in piste:
        if instant > jusqua:
            break
        for k, v in changes.items():
            if v is None:
                etat.pop(k, None)
            else:
                etat[k] = v
    return etat


class RejeuTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.monde, cls.chronique, cls.enregistreur, cls.empreinte = nuit(90, True)

    def test_la_nuit_est_la_meme_avec_ou_sans_enregistreur(self):
        self.assertEqual(nuit(90, False)[3], self.empreinte)

    def test_la_fin_du_rejeu_est_l_etat_final(self):
        m, d = self.monde, self.enregistreur.donnees(self.monde, self.chronique)
        etats, esprits = rejouer(d["etats"], d["fin"]), rejouer(d["esprits"], d["fin"])
        for id in d["personnages"]:
            o = m.objets[id]
            self.assertEqual(etats[id], [o["lieu"], o.get("position"), o.get("orientation")], id)
            croit = {objet: [c["lieu"].get("valeur"), c["lieu"].get("salle"), c["lieu"].get("case")]
                     for objet, c in lire(m, id)["croyances"].items() if c.get("lieu")}
            self.assertEqual({k.split("|", 1)[1]: v for k, v in esprits.items()
                              if k.startswith(id + "|") and not k.split("|", 1)[1].startswith(":")}, croit, id)

    def test_chaque_instant_garde_ce_qui_a_ete(self):
        d = self.enregistreur.donnees(self.monde, self.chronique)
        instants = [i for i, _ in d["etats"]]
        self.assertEqual(instants, sorted(set(instants)))  # Un instant, une entrée, dans l'ordre.
        bouges = {id for _, changes in d["etats"][1:] for id in changes if id in d["personnages"]}
        self.assertTrue(bouges)  # Ils ont bougé ou tourné pendant la nuit, et c'est noté.
        for id, vus in rejouer(d["vues"], d["fin"]).items():
            self.assertTrue(all(0 <= i < len(d["cases"]) for i in vus), id)

    def test_la_page_porte_ses_donnees(self):
        d = self.enregistreur.donnees(self.monde, self.chronique, "essai")
        d["chronique"].append({"minute": 1, "pnj": None, "texte": "</script><b>"})
        html = page(d)
        self.assertNotIn("/*DONNEES*/", html)
        self.assertEqual(html.count("</script>"), 1)  # Une chronique ne ferme pas le script.
        donnees = json.loads(re.search(r"const D = (.*?);\nconst CS", html, re.S).group(1))
        self.assertEqual(donnees["titre"], "essai")


if __name__ == "__main__":
    unittest.main()
