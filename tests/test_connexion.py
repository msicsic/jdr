import io
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from threading import Event

from donjon.connexion import (Coffre, ISSUER, _fusionner_jetons, deconnecter, jeton,
                              lire_callback, verifier_identite)
from donjon.mj import MJOpenAI, lire_flux
from donjon.monde import ErreurMonde, nouveau_monde
from donjon.moteur import proposition
from tests.faux_websocket import FauxWebSocket


class SessionTests(unittest.TestCase):
    def test_callback_verifie_state_et_client(self):
        bon = {"state": ["attendu"], "code": ["code"], "client_id": ["oaiapp_jeu"]}
        self.assertEqual(lire_callback(bon, "attendu", "dynamic_agent_client"), ("oaiapp_jeu", "code"))
        self.assertEqual(lire_callback({"state": ["attendu"], "code": ["code"]}, "attendu", "oaiapp_jeu"), ("oaiapp_jeu", "code"))
        for mauvais in ({**bon, "state": ["autre"]}, {**bon, "code": []},
                        {**bon, "error": ["access_denied"]}, {**bon, "state": ["attendu", "attendu"]}):
            with self.assertRaises(ErreurMonde):
                lire_callback(mauvais, "attendu", "dynamic_agent_client")
        with self.assertRaises(ErreurMonde):
            lire_callback(bon, "attendu", "oaiapp_autre")

    def test_autorisation_identite_seule_insuffisante(self):
        with self.assertRaises(ErreurMonde):
            _fusionner_jetons({}, {"scope": "openid profile email", "access_token": "test", "expires_in": 3600})

    def test_coffre_protege_jetons_et_ne_contient_pas_texte_clair(self):
        with tempfile.TemporaryDirectory() as tmp:
            coffre = Coffre(tmp)
            data = {"host": "urn:uuid:test", "actif": "a", "comptes": {"a": {"access_token": "secret-test-unique"}}}
            with coffre.verrou():
                coffre.ecrire(data)
                # Tenu par ailleurs, le verrou finit par refuser (attente raccourcie ici).
                with patch("donjon.connexion.ATTENTE_VERROU", 0.2), self.assertRaises(ErreurMonde):
                    with coffre.verrou():
                        pass
            self.assertEqual(coffre.lire(), data)
            if os.name == "nt":
                self.assertNotIn(b"secret-test-unique", coffre.fichier.read_bytes())
            else:
                self.assertEqual(coffre.fichier.stat().st_mode & 0o777, 0o600)

    def test_refresh_atomique_reutilise_client_et_rotation(self):
        with tempfile.TemporaryDirectory() as tmp:
            coffre = Coffre(tmp)
            data = {"host": "urn:uuid:test", "actif": "a", "comptes": {"a": {
                "client_id": "oaiapp_jeu", "access_token": "expire", "refresh_token": "ancien",
                "expires_at": 0, "scopes": ["resource.invoke", "chatgpt.tokens.use.direct"]}}}
            coffre.ecrire(data)
            tokens = {"access_token": "nouveau", "refresh_token": "rotation", "expires_in": 3600, "token_type": "Bearer"}
            with patch("donjon.connexion.appeler_json", return_value=tokens) as api:
                self.assertEqual(jeton(coffre), "nouveau")
                self.assertEqual(api.call_args.args[1]["client_id"], "oaiapp_jeu")
                self.assertNotIn("scope", api.call_args.args[1])
            self.assertEqual(coffre.compte()["refresh_token"], "rotation")
            self.assertEqual(coffre.lire()["host"], "urn:uuid:test")

    def test_deconnexion_efface_jetons_conserve_inscription(self):
        with tempfile.TemporaryDirectory() as tmp:
            coffre = Coffre(tmp)
            coffre.ecrire({"host": "urn:uuid:test", "actif": "a", "comptes": {"a": {
                "client_id": "oaiapp_jeu", "subject": "s", "access_token": "secret", "refresh_token": "refresh", "id_token": "id"}}})
            with patch("donjon.connexion.appeler_json", side_effect=ErreurMonde("réseau")), patch("sys.stdout", io.StringIO()) as out:
                deconnecter(coffre)
            self.assertIn("non confirmée", out.getvalue())
            self.assertNotIn("access_token", coffre.compte())
            self.assertNotIn("id_token", coffre.compte())
            self.assertEqual(coffre.compte()["client_id"], "oaiapp_jeu")

    def test_deux_mj_partagent_un_seul_refresh_sans_conflit(self):
        with tempfile.TemporaryDirectory() as tmp:
            coffre = Coffre(tmp)
            coffre.ecrire({"host": "urn:uuid:test", "actif": "a", "comptes": {"a": {
                "client_id": "oaiapp_jeu", "access_token": "expire", "refresh_token": "ancien",
                "expires_at": 0, "scopes": ["resource.invoke", "chatgpt.tokens.use.direct"]}}})
            debut, second, liberer = Event(), Event(), Event()
            def refresh(*args, **kwargs):
                debut.set()
                liberer.wait(3)
                return {"access_token": "nouveau", "refresh_token": "rotation", "expires_in": 3600, "token_type": "Bearer"}
            def lire_second():
                second.set()
                return jeton(Coffre(tmp))
            with patch("donjon.connexion.appeler_json", side_effect=refresh) as api, ThreadPoolExecutor(max_workers=2) as pool:
                premier = pool.submit(jeton, coffre)
                self.assertTrue(debut.wait(2))
                autre = pool.submit(lire_second)
                self.assertTrue(second.wait(2))
                liberer.set()
                self.assertEqual(premier.result(timeout=2), "nouveau")
                self.assertEqual(autre.result(timeout=2), "nouveau")
                self.assertEqual(api.call_count, 1)


try:
    import jwt
    from cryptography.hazmat.primitives.asymmetric import rsa
    CRYPTO = True
except ImportError:
    CRYPTO = False


@unittest.skipUnless(CRYPTO, "Installer requirements-chatgpt.txt pour vérifier les signatures OAuth")
class IdentiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cle = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        publique = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(cls.cle.public_key()))
        publique["kid"] = "test"
        cls.jwks = {"keys": [publique]}

    def token(self, **changements):
        claims = {"iss": ISSUER, "aud": "oaiapp_jeu", "sub": "joueur", "nonce": "nonce",
                  "iat": int(time.time()), "exp": int(time.time()) + 300, **changements}
        return jwt.encode(claims, self.cle, algorithm="RS256", headers={"kid": "test"})

    def test_identite_signee_valide(self):
        self.assertEqual(verifier_identite(self.token(), "oaiapp_jeu", "nonce", self.jwks)["sub"], "joueur")

    def test_issuer_audience_nonce_et_expiration_rejetes(self):
        for changement in ({"iss": "https://autre"}, {"aud": "autre"}, {"nonce": "autre"}, {"exp": 1}):
            with self.subTest(changement=changement), self.assertRaises(ErreurMonde):
                verifier_identite(self.token(**changement), "oaiapp_jeu", "nonce", self.jwks)

    def test_signature_modifiee_rejetee(self):
        token = self.token().split(".")
        token[2] = ("A" if token[2][0] != "A" else "B") + token[2][1:]
        with self.assertRaises(ErreurMonde):
            verifier_identite(".".join(token), "oaiapp_jeu", "nonce", self.jwks)


class FluxTests(unittest.TestCase):
    def test_succes_terminal_et_pas_simple_fragment(self):
        resultat = {"status": "completed", "output": []}
        flux = io.BytesIO(("data: " + json.dumps({"type": "response.completed", "response": resultat}) + "\n\n").encode())
        self.assertEqual(lire_flux(flux)["output"], resultat["output"])
        with self.assertRaises(ErreurMonde):
            lire_flux(io.BytesIO(b'data: {"type":"response.output_text.delta","delta":"bonjour"}\n\n'))

    def test_elements_deja_emis_non_repetes_dans_terminal(self):
        item = {"type": "function_call", "name": "proposer_action", "arguments": "{}"}
        evenements = [{"type": "response.output_item.done", "output_index": 0, "item": item},
                      {"type": "response.completed", "response": {"status": "completed", "output": []}}]
        flux = io.BytesIO("".join("data: " + json.dumps(e) + "\n\n" for e in evenements).encode())
        self.assertEqual(lire_flux(flux)["output"], [item])

    def test_limite_forfait_apres_debut_flux_est_un_echec(self):
        with self.assertRaises(ErreurMonde):
            lire_flux(io.BytesIO(b'data: {"type":"response.failed","response":{"error":{"code":"subscription_sharing_usage_limit_exceeded"}}}\n\n'))

    def test_contrat_forfait_outils_namespace_sans_champs_interdits(self):
        p = proposition("observer", "contexte")
        resultat = {"status": "completed", "output": [{"type": "function_call", "name": "proposer_action", "arguments": json.dumps(p)}]}
        def repondre(payload):
            self.assertNotIn("stream", payload)
            self.assertFalse(payload["store"])
            self.assertNotIn("max_output_tokens", payload)
            self.assertEqual(payload["tools"][0]["type"], "namespace")
            return resultat
        socket = FauxWebSocket(repondre)
        with patch("donjon.fournisseurs.openai.jeton", return_value="oauth-test"), patch("donjon.fournisseurs.openai.modeles", return_value=[{"slug": "test"}]), patch("donjon.transport_openai.ouvrir_websocket", return_value=socket) as ouvrir:
            mj = MJOpenAI("test", connexion="chatgpt")
            self.assertEqual(mj.proposer(nouveau_monde(), "comment je suis arrivé ici ?"), p)
            self.assertEqual(ouvrir.call_args.args[0], "oauth-test")
            mj.fermer()

    def test_401_coupe_appels_repetes_sans_fallback_facture(self):
        erreur = urllib.error.HTTPError("https://api.openai.com", 401, "unauthorized", {}, io.BytesIO(b'{"error":{"code":"invalid_api_key"}}'))
        mj = MJOpenAI()
        with patch.dict("os.environ", {"OPENAI_API_KEY": "invalide"}), patch("urllib.request.urlopen", side_effect=erreur) as api:
            for _ in range(2):
                with self.assertRaises(ErreurMonde):
                    mj.proposer(nouveau_monde(), "comment suis-je arrivé ici ?")
            self.assertEqual(api.call_count, 1)

    def test_echec_flux_conserve_erreur_de_forfait(self):
        mj = MJOpenAI("test", connexion="chatgpt")
        socket = FauxWebSocket(lambda _: [{"type": "response.failed"}])
        with patch("donjon.fournisseurs.openai.jeton", return_value="oauth-test"), patch("donjon.fournisseurs.openai.modeles", return_value=[{"slug": "test"}]), patch("donjon.transport_openai.ouvrir_websocket", return_value=socket):
            with self.assertRaisesRegex(ErreurMonde, "limites du forfait"):
                mj.proposer(nouveau_monde(), "bonjour")

    def test_modele_absent_du_forfait_ne_declenche_pas_inference(self):
        with patch("donjon.fournisseurs.openai.modeles", return_value=[]), patch("urllib.request.urlopen") as api:
            with self.assertRaisesRegex(ErreurMonde, "pas disponible"):
                MJOpenAI("absent", connexion="chatgpt").proposer(nouveau_monde(), "bonjour")
            api.assert_not_called()


class ConnexionConsoleTests(unittest.TestCase):
    def test_connecter_dans_jeu_utilise_forfait_apres_validation(self):
        import jeu
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), patch("jeu.connecter") as connexion, patch.object(MJOpenAI, "echanger", return_value={"mode": "dialogue", "texte": "Gorm t’a conduit ici.", "faits": ["scenario"], "proposition": None, "_texte_moteur": True}), patch("builtins.input", side_effect=["connecter", "connexion", "comment je suis arrivé ici ?", "quitter"]), patch("sys.stdout", io.StringIO()) as sortie:
                jeu.main(["--connexion", "api", "--save", str(Path(tmp) / "partie.json")])
            connexion.assert_called_once()
            self.assertIn("MJ : chatgpt", sortie.getvalue())
            self.assertIn("Gorm t’a conduit ici.", sortie.getvalue())

    def test_offline_interdit_ouverture_navigateur(self):
        import jeu
        with tempfile.TemporaryDirectory() as tmp:
            with patch("jeu.connecter") as connexion, patch("builtins.input", side_effect=["connecter", "quitter"]), patch("sys.stdout", io.StringIO()):
                jeu.main(["--offline", "--save", str(Path(tmp) / "partie.json")])
            connexion.assert_not_called()


if __name__ == "__main__":
    unittest.main()


class VerrouTests(unittest.TestCase):
    """Le coffre se partage entre processus : on attend son tour, un verrou orphelin est repris."""

    def test_un_verrou_libere_pendant_l_attente_laisse_passer(self):
        import threading
        from donjon.connexion import Coffre
        with tempfile.TemporaryDirectory() as dossier:
            coffre = Coffre(dossier)
            pris, relache = threading.Event(), threading.Event()

            def tenir():
                with coffre.verrou():
                    pris.set()
                    relache.wait(2)
            fil = threading.Thread(target=tenir)
            fil.start()
            pris.wait(2)
            threading.Timer(0.2, relache.set).start()
            with coffre.verrou():
                pass
            fil.join()

    def test_un_verrou_tenu_trop_longtemps_echoue_clairement(self):
        from donjon import connexion
        with tempfile.TemporaryDirectory() as dossier, patch.object(connexion, "ATTENTE_VERROU", 0.2):
            coffre = connexion.Coffre(dossier)
            with coffre.verrou():
                with self.assertRaisesRegex(ErreurMonde, "déjà en cours"):
                    with coffre.verrou():
                        pass

    def test_un_verrou_orphelin_est_repris(self):
        import os
        import time
        from donjon.connexion import Coffre, VERROU_ORPHELIN
        with tempfile.TemporaryDirectory() as dossier:
            verrou = Path(dossier) / "connexion.lock"
            verrou.write_text("99999")
            ancien = time.time() - VERROU_ORPHELIN - 10
            os.utime(verrou, (ancien, ancien))
            with Coffre(dossier).verrou():
                pass
            self.assertFalse(verrou.exists())
