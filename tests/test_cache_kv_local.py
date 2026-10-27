"""Stabilité du préfixe KV (instructions, faits, schéma) et fournisseur LLM local (--connexion local)."""
import io
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.atelier import nouveau_atelier
from donjon.defi import nouveau_defi
from donjon.fournisseurs import creer
from donjon.fournisseurs.contrat import Demande
from donjon.fournisseurs.openai import OpenAI
from donjon.fournisseurs.local import Local, extraire_json, normaliser_url
from donjon.mj import INSTRUCTIONS_RESULTAT, MJ
from donjon.monde import Monde, nouveau_monde
from donjon.sources import ordonner_entree, ordonner_faits, slot_cache, voie_cache
from donjon.spatial import installer
from tests.test_fournisseurs_jeu import arguments
from tests.test_repli_et_appel import NEUTRE, dialogue, verdicts
from tools.verifier_websocket_jeu import CAS, parcours


def prefixe_commun(a, b):
    limite = min(len(a), len(b))
    i = 0
    while i < limite and a[i] == b[i]:
        i += 1
    return i


def empreinte(valeur):
    return hashlib.sha256(json.dumps(valeur, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def requetes_et_recharge(type_mj, cas):
    """Rejoue deux scènes par la console réelle, sans réseau, avec état et rendu rechargés."""
    traces, etats = [], []
    cible = CAS[cas][1]
    sauver = Monde.sauver

    def enregistrer(monde, chemin):
        sauver(monde, chemin)
        etats.append(copy.deepcopy(monde.data))

    def brut(instructions, entree, intention, fonction, schema):
        traces.append({"fonction": fonction, "instructions": empreinte(instructions),
                       "entree": empreinte(entree), "schema": empreinte(schema)})
        return arguments(cible, fonction, entree)

    with (patch("jeu.MJ", type_mj), patch.object(type_mj, "_appeler_brut", side_effect=brut),
          patch.object(Monde, "sauver", enregistrer)):
        resultat = parcours(cas)
    return {"requetes": traces, "etat": empreinte(etats[-1]), "rendu": empreinte(resultat)}


class ContenuConserveTests(unittest.TestCase):
    def test_requetes_et_recharge_identiques_a_l_ordre_pres_sur_deux_scenes(self):
        # Le même code, avec et sans l'ordre des sources : mêmes requêtes au contenu près
        # (empreintes à clés triées), même état et même rendu après rechargement. Comparer au code
        # courant plutôt qu'à une empreinte figée : les lots suivants changent légitimement le contenu.
        for cas in CAS:
            with self.subTest(cas=cas):
                ordonne = requetes_et_recharge(MJ, cas)
                with patch("donjon.mj.ordonner_entree", side_effect=lambda entree: entree):
                    brut = requetes_et_recharge(MJ, cas)
                self.assertEqual(ordonne, brut)

    def test_ordre_idempotent_sans_perte_et_revision_toujours_en_fin(self):
        entree = {"consigne_revision": "corrige", "inconnu": [1],
                  "faits": {"revision": 2, "objet:z": {}, "salle": {}, "objet:a": {}},
                  "controle_narratif": [], "message": "bonjour"}
        avant = copy.deepcopy(entree)
        ordre = ordonner_entree(entree)
        self.assertEqual(ordre, avant)
        self.assertEqual(entree, avant)
        self.assertEqual(list(ordre)[-2:], ["controle_narratif", "consigne_revision"])
        self.assertEqual(list(ordre["faits"]), ["salle", "objet:a", "objet:z", "revision"])
        self.assertEqual(json.dumps(ordre), json.dumps(ordonner_entree(ordre)))

    def test_audits_portee_et_capacites_commencent_par_le_contexte(self):
        for entree, debut in (({"qualifications": [{"cible": "test"}], "scenario": {}}, "scenario"),
                              ({"descriptions": [], "monde": {}, "attestations": [], "demande": "test"}, "monde"),
                              ({"demande": "test", "plan": {}, "designations": []}, "designations")):
            with self.subTest(debut=debut):
                ordre = ordonner_entree(entree)
                self.assertEqual(ordre, entree)
                self.assertEqual(next(iter(ordre)), debut)


class PrefixeKVTests(unittest.TestCase):
    def _capter_appel(self, monde, intention, enrichir=True, **kwargs):
        recus = []
        instance = MJ("local", "none", connexion="local")

        def faux_brut(instructions, entree, intention_, fonction, schema):
            recus.append((instructions, entree, fonction, schema))
            raise RuntimeError("stop")

        instance._appeler_brut = faux_brut
        with self.assertRaises(RuntimeError):
            instance._echanger(monde, intention, None, enrichir=enrichir, **kwargs)
        return recus[0]

    def test_instructions_stables_dans_la_salle_sans_revision_au_premier_appel_et_ordre_schema_conserve(self):
        m_base = nouveau_monde()
        m_defi = nouveau_defi(depart="fixe")
        installer(m_defi)

        i_base, _, _, _ = self._capter_appel(m_base, "je regarde autour de moi", enrichir=True)
        i1, e1, _, s1 = self._capter_appel(m_defi, "je regarde autour de moi", enrichir=True)
        i2, e2, _, s2 = self._capter_appel(m_defi, "« Ilse, ouvre la porte ! »", enrichir=True,
                                           retour_moteur={"obstacle": "Test", "consigne": "Corrige."})

        self.assertEqual(i_base, i1)
        self.assertEqual(i1, i2)
        self.assertIn("Le retour_moteur est un contrôle fiable", e2["consigne_retour_moteur"])
        self.assertNotIn("consigne_retour_moteur", e1)
        self.assertIn("action faufiler", i_base)
        self.assertNotIn("rupture du contrat narratif", i1)
        # L'ordre causal du schéma (mode -> texte -> faits -> proposition) est intégralement préservé.
        self.assertEqual(list(s1["properties"]), ["mode", "texte", "faits", "proposition"])
        self.assertEqual(list(e1)[0], "faits")
        self.assertEqual(list(e2)[0], "faits")

        n_conv, e_conv, _, _ = self._capter_appel(
            m_defi, "Gorm ?", enrichir=False,
            conversation_validee={"personnage": "marchand", "sujet": "Gorm ?", "operation": "discuter",
                                  "faits": [], "repondent": ["marchand"], "temoins": []})
        n_res, e_res, _, _ = self._capter_appel(
            m_defi, "Raconte.", enrichir=False,
            resultat_resolu={"gestes": ["Geste."], "faits": ["Tu avances."], "intention": "j'avance"})
        # La narration de résultat garde sa consigne dédiée et sa propre voie de cache.
        self.assertIn(INSTRUCTIONS_RESULTAT.strip(), n_res)
        self.assertNotIn("conversation_validee", n_res)
        self.assertNotIn("rupture du contrat narratif", n_conv)
        self.assertNotIn("rupture du contrat narratif", n_res)
        self.assertEqual(voie_cache("repondre_au_joueur", e_conv, False), "raconter")
        self.assertEqual(voie_cache("repondre_au_joueur", e_res, False), "raconter_resultat")

    def test_partage_du_prefixe_entree_entre_tours_relances_et_audit(self):
        m = nouveau_defi(depart="fixe")
        installer(m)
        _, entree_t1, _, _ = self._capter_appel(m, "j'examine la table", enrichir=True)
        # Le tour suivant incrémente la révision et change l'intention sans muter la salle ni les objets.
        m.data["revision"] += 1
        _, entree_t2, _, _ = self._capter_appel(m, "« Ilse, que vois-tu d'ici ? »", enrichir=True)
        _, entree_retry, _, _ = self._capter_appel(
            m, "« Ilse, que vois-tu d'ici ? »", enrichir=True,
            retour_moteur={"obstacle": "Rien n'est fait.", "consigne": "Corrige."})

        j_t1 = json.dumps(entree_t1, ensure_ascii=False)
        j_t2 = json.dumps(entree_t2, ensure_ascii=False)
        j_retry = json.dumps(entree_retry, ensure_ascii=False)

        # La révision et l'intention étant en fin de faits/entrée, plus de 85 % du JSON est partagé.
        ratio_tours = prefixe_commun(j_t1, j_t2) / min(len(j_t1), len(j_t2))
        ratio_retry = prefixe_commun(j_t2, j_retry) / min(len(j_t2), len(j_retry))
        self.assertGreater(ratio_tours, 0.85)
        self.assertGreater(ratio_retry, 0.92)

    def test_relance_controle_narratif_garde_instructions_et_prefixe_entree_intacts(self):
        m = nouveau_defi(depart="fixe")
        installer(m)
        traces = []

        def appel(instructions, entree, intention, fonction, schema):
            traces.append((instructions, entree, json.dumps(entree, ensure_ascii=False), fonction))
            if fonction == "auditer_narration":
                if len(traces) == 2:
                    return verdicts(("invention_protegee", (), "Invention."))
                return verdicts(NEUTRE)
            if len(traces) == 1:
                return dialogue("Une trappe secrète brille sous la table.")
            return dialogue("La table est posée devant toi.")

        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJ, "_appeler_brut", side_effect=appel),
                  patch("builtins.input", side_effect=["mj que vois-je ?", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--connexion", "api", "--save", str(chemin)]), 0)
            reprise = Monde.charger(chemin)

        self.assertIn("La table est posée devant toi.", sortie.getvalue())
        self.assertEqual(reprise.data["narrations_mj"][-1]["texte"], "La table est posée devant toi.")
        appels_mj = [(i, d, e) for i, d, e, f in traces if f == "repondre_au_joueur"]
        appels_audit = [(i, d, e) for i, d, e, f in traces if f == "auditer_narration"]
        self.assertEqual(len(appels_mj), 2)
        # Les instructions ne changent pas lors de la relance controle_narratif ; la consigne est en fin d'entrée.
        self.assertEqual(appels_mj[0][0], appels_mj[1][0])
        self.assertNotIn("consigne_revision", appels_mj[0][1])
        self.assertIn("consigne_revision", appels_mj[1][1])
        self.assertEqual(list(appels_mj[1][1])[-2:], ["controle_narratif", "consigne_revision"])
        # Le préfixe d'entrée avant controle_narratif est conservé à plus de 95 %.
        self.assertGreater(prefixe_commun(appels_mj[0][2], appels_mj[1][2]) / len(appels_mj[0][2]), 0.95)
        # L'audit partage le préfixe de faits avec l'appel du MJ.
        self.assertGreater(prefixe_commun(appels_mj[0][2], appels_audit[0][2]) / len(appels_audit[0][2]), 0.80)


class FournisseurLocalTests(unittest.TestCase):
    def test_fabrique_et_normalisation_url_et_extraction_think(self):
        self.assertIsInstance(creer("local"), Local)
        self.assertEqual(normaliser_url("http://127.0.0.1:8080"),
                         "http://127.0.0.1:8080/v1/chat/completions")
        self.assertEqual(normaliser_url("http://localhost:11434/v1"),
                         "http://localhost:11434/v1/chat/completions")
        self.assertEqual(extraire_json("<think>\nRéflexion interne...\n</think>\n{\"ok\": true}"),
                         {"ok": True})
        self.assertEqual(
            [slot_cache(voie_cache(f, e)) for f, e in (
                ("repondre_au_joueur", {"faits": {}}),
                ("repondre_au_joueur", {"faits": {"resultat_resolu": {}}}),
                ("auditer_narration", {"faits": {}}),
                ("auditer_action", {}),
            )],
            [0, 1, 2, 3],
        )

    def test_cles_distinctes_par_voie_sur_les_deux_fournisseurs(self):
        cas = [("repondre_au_joueur", {}, ["dialogue", "action"], "interpreter"),
               ("repondre_au_joueur", {}, ["dialogue"], "raconter"),
               ("repondre_au_joueur", {"resultat_resolu": {}}, ["dialogue"], "raconter_resultat")]
        cas += [(f, {}, [], f) for f in ("auditer_narration", "auditer_action", "auditer_portee", "auditer_capacites")]
        for fournisseur in (OpenAI(), Local()):
            requetes = []
            def http(requete, timeout):
                payload = json.loads(requete.data)
                requetes.append(payload)
                if "tools" in payload:
                    resultat = {"status": "completed", "output": [{"type": "function_call",
                        "name": payload["tools"][0]["name"], "arguments": "{}"}]}
                else:
                    resultat = {"choices": [{"message": {"content": "{}"}, "finish_reason": "stop"}]}
                return io.BytesIO(json.dumps(resultat).encode())
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test"}), patch("urllib.request.urlopen", side_effect=http):
                for fonction, faits, modes, voie in cas:
                    with self.subTest(fournisseur=type(fournisseur).__name__, voie=voie):
                        schema = {"type": "object", "properties": {"mode": {"type": "string", "enum": modes}}}
                        fournisseur.appeler(Demande("consigne", {"faits": faits}, "test", fonction,
                                                   schema, "local", cle_cache="partie"))
                        self.assertEqual(requetes[-1]["prompt_cache_key"], "partie:" + voie)
            self.assertEqual(len({p["prompt_cache_key"] for p in requetes}), len(cas))

    def test_parcours_local_deux_scenes_avec_sauvegarde_et_reprise(self):
        for cas in CAS:
            with self.subTest(cas=cas):
                cible = CAS[cas][1]
                requetes = []
                traces = []

                def http(requete, timeout):
                    p = json.loads(requete.data)
                    requetes.append(p)
                    fonction = p["response_format"]["json_schema"]["name"]
                    entree = json.loads(p["messages"][1]["content"])
                    a = arguments(cible, fonction, entree)
                    corps = {
                        "choices": [{
                            "message": {"role": "assistant", "content": "<think>ok</think>" + json.dumps(a)},
                            "finish_reason": "stop",
                        }],
                        "usage": {"prompt_tokens": 1200, "completion_tokens": 25, "total_tokens": 1225},
                        "timings": {"cache_n": 1050, "prompt_n": 150},
                    }
                    return io.BytesIO(json.dumps(corps).encode("utf-8"))

                def construire(*a, **kw):
                    kw.update(connexion="local")
                    instance = MJ(*a, **kw)
                    instance.journal_complet, instance.observateur = True, traces.append
                    return instance

                with (patch("jeu.MJ", side_effect=construire),
                      patch("urllib.request.urlopen", side_effect=http)):
                    r = parcours(cas)

                self.assertTrue(r["recit_sauve_avant_affichage"])
                self.assertTrue(r["etat_identique_apres_reprise"])
                self.assertEqual(r["executions_action"], 1)
                self.assertGreaterEqual(len(requetes), 3)
                # Le fournisseur local active cache_prompt, route id_slot par voie et remonte cache_n.
                self.assertTrue(all(req["cache_prompt"] is True for req in requetes))
                slots_vus = [req["id_slot"] for req in requetes]
                self.assertEqual(slots_vus[:3], [0, 3, 1])
                self.assertEqual(traces[0]["usage"]["prompt_tokens_details"]["cached_tokens"], 1050)


if __name__ == "__main__":
    unittest.main()
