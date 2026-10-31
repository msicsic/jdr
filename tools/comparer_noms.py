"""Prouve l'identité des noms, des requêtes MJ et des rendus, sans modèle.

    python tools/comparer_noms.py --reference ../noms-lisibles-reference

Les deux arbres jouent le même corpus dans des interpréteurs séparés. Les requêtes
sont interceptées avant le fournisseur ; une connexion réseau est interdite.
Les JSON comparés conservent l'ordre des champs et les caractères Unicode.
"""
import argparse
import copy
import gzip
import hashlib
import inspect
import json
import os
from pathlib import Path
import socket
import statistics
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

SCRIPT = Path(__file__).resolve()
CORPUS = SCRIPT.parents[1]


def serialiser(valeur):
    return json.dumps(valeur, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def mondes():
    """Tous les départs de banc, les captures disponibles et les cas nominaux difficiles."""
    from donjon.monde import Monde
    from tools.banc_parties import preparer
    from donjon.banc_pnj import creer
    from donjon.noms import apprendre
    from donjon import memoire

    with tempfile.TemporaryDirectory() as dossier:
        sauvegarde = Path(dossier) / "partie.json"
        for chemin in sorted((CORPUS / "tests/data/bancs").glob("*.json")):
            donnees = json.loads(chemin.read_text(encoding="utf-8"))
            preparer({**donnees, "preparation": donnees.get("preparation", {})}, sauvegarde)
            yield str(chemin.relative_to(CORPUS)), Monde.charger(sauvegarde)
        # La branche 276524c n'a pas de tests/data/scenes : inclure aussi les
        # captures réellement conservées ailleurs dans tests/data.
        for chemin in sorted((CORPUS / "tests/data").rglob("*")):
            if not chemin.name.endswith((".json", ".json.gz")) or "bancs" in chemin.parts:
                continue
            lire = gzip.open if chemin.suffix == ".gz" else open
            with lire(chemin, "rt", encoding="utf-8") as fichier:
                donnees = json.load(fichier)
            if isinstance(donnees, dict) and {"joueur", "objets", "salles"} <= donnees.keys():
                yield str(chemin.relative_to(CORPUS)), Monde(donnees)

        for connu in (False, True):
            donnees = json.loads((CORPUS / "tests/data/bancs/depouille.json").read_text(encoding="utf-8"))
            preparer(donnees, sauvegarde)
            monde = Monde.charger(sauvegarde)
            if connu:
                apprendre(monde, "joueur", "aubin")
            yield f"construit/defunt-{connu}", monde
        for appellation in ("se_dit", "appelee"):
            monde = creer("relais", 1985, "fixe")
            if appellation == 'se_dit':
                memoire.retenir_pretention_vocale(monde, "joueur", "ilse", "aubin")
            else:
                memoire.retenir_appellation_vocale(monde, "joueur", "ilse", "aubin")
            yield f"construit/voix-{appellation}", monde
        monde = creer("relais", 1985, "fixe")
        monde.objets["briquet"]["lieu"] = "aubin"
        yield "construit/element-porte", monde
        monde = creer("relais", 1985, "fixe")
        monde.data["personnes"] = {}
        for identifiant in ("aubin", "marchand"):
            monde.objets[identifiant]["designation_visuelle"] = "un homme trapu"
        from donjon.noms import installer
        installer(monde)
        yield "construit/homonymes", monde
        monde = creer("relais", 1985, "fixe")
        monde.data["conversation"].append({"role": "assistant", "content": "« Aubin parle à Gorm. »"})
        yield "construit/citations", monde


def requete(monde, enrichir):
    """Capture la frontière commune de l'interprétation et de la narration finale."""
    from donjon.mj import MJ

    class Capture(Exception):
        pass

    class MJCapture(MJ):
        def _appeler(self, *arguments):
            self.capture = arguments
            raise Capture

    mj = MJCapture(fournisseur=object())
    try:
        mj._echanger(monde, "Que vois-je ?", None, enrichir)
    except Capture:
        return mj.capture
    raise AssertionError("Aucune requête capturée")


def extraire():
    from donjon import noms
    from donjon.monde import Monde, ErreurMonde
    from donjon.rendu import regarder, decrire_contexte
    from donjon.scene import scene_percue
    from donjon.carte import carte
    from donjon.narration import voix_inconnues, clarification_nominale
    fonctions = ("connait", "apprendre", "designation", "nom", "resoudre", "texte", "reference",
                 "public", "verifier_references", "references", "entendre", "presenter", "verifier")
    corpus = {"contrat_public": {fonction: str(inspect.signature(getattr(noms, fonction)))
                                 for fonction in fonctions}}
    corpus["contrat_public"].update(PERSONNES=noms.PERSONNES,
                                    CHAMPS_REFERENCES=sorted(noms.CHAMPS_REFERENCES),
                                    LISTES_REFERENCES=sorted(noms.LISTES_REFERENCES))
    mesures = []
    with tempfile.TemporaryDirectory() as dossier:
        sauvegarde = Path(dossier) / "recharge.json"
        for titre, monde in mondes():
            etapes = []
            for recharge in (False, True):
                if recharge:
                    monde.sauver(sauvegarde)
                    monde = Monde.charger(sauvegarde)
                contexte = monde.contexte()
                textes = " | ".join(objet["nom"] for objet in monde.objets.values())
                textes += " ; « Aubin parle à Gorm. » ; corps de Aubin ; une voix qui se dit Aubin"
                observateurs = ["joueur", *(identifiant for identifiant, objet in monde.objets.items()
                                            if objet["type"] == "personnage")]
                projection = noms.public(monde, contexte)
                refs = {identifiant: noms.reference(monde, identifiant) for identifiant in monde.objets}
                refus = []
                for valeur in ("aubin", refs.get("aubin"), "personne_99999"):
                    try:
                        noms.verifier_references(monde, {"cible": valeur}, projection)
                        refus.append(None)
                    except ErreurMonde as erreur:
                        refus.append([str(erreur), erreur.attendu])
                personnes = [identifiant for identifiant, objet in monde.objets.items()
                             if objet["type"] == "personnage"]
                paroles = [{"locuteur": refs[identifiant], "texte": textes,
                            "presentation": "", "passage": "« " + textes + " »"}
                           for identifiant in personnes[:2]]
                etapes.append({"contexte": projection, "references": refs,
                               "interpretation": requete(monde, True), "narration": requete(monde, False),
                               "scene": scene_percue(monde), "regarder": regarder(monde),
                               "bilan": decrire_contexte(monde), "carte": carte(monde),
                               "textes": [noms.texte(monde, textes, citations=citations, observateur=observateur)
                                          for citations in (False, True) for observateur in observateurs],
                               "refus": refus,
                               "audit": voix_inconnues(monde, [], projection, textes),
                               "audit_repliques": voix_inconnues(monde, paroles, projection,
                                                                  "« " + textes + " »"),
                               "decodees": noms.references(monde, {"cibles": list(refs.values()),
                                                                    "texte": textes}),
                               "clarification": clarification_nominale(monde, textes, textes, projection),
                               "etat": copy.deepcopy(monde.data)})
                if recharge:
                    mesures.append((monde, contexte, textes))
            corpus[titre] = etapes
    return corpus, mesures


def mesurer(corpus, repetitions):
    """Lots séparés et répétés ; aucun chargement ni rendu dans le temps mesuré."""
    from donjon import noms
    resultats = {"public": [], "texte": []}
    for _ in range(repetitions):
        for fonction in resultats:
            debut = time.process_time()
            for monde, contexte, textes in corpus:
                for _ in range(10):
                    if fonction == "public":
                        noms.public(monde, contexte)
                    else:
                        noms.texte(monde, textes)
                        noms.texte(monde, textes, citations=True)
            resultats[fonction].append(time.process_time() - debut)
    return resultats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--sortie", type=Path, default=CORPUS / "artifacts/noms-lisibles")
    parser.add_argument("--repetitions", type=int, default=9)
    parser.add_argument("--_worker", type=Path)
    args = parser.parse_args()
    args.sortie = args.sortie.resolve()
    if args._worker:
        # Charger exclusivement le moteur de l'arbre choisi et ses outils.
        sys.path.insert(0, str(args._worker.resolve()))
        sys.path.append(str(SCRIPT.parent))
        from priorite import ceder
        ceder()
        with patch.object(socket.socket, "connect", side_effect=AssertionError("Réseau interdit")):
            corpus, mesures = extraire()
            args.sortie.mkdir(parents=True, exist_ok=True)
            (args.sortie / "corpus.json").write_bytes(serialiser(corpus))
            (args.sortie / "temps.json").write_bytes(serialiser(mesurer(mesures, args.repetitions)))
        return 0
    if args.reference is None:
        parser.error("--reference attend le worktree de 276524c")
    args.sortie.mkdir(parents=True, exist_ok=True)
    for cote, arbre in (("avant", args.reference), ("apres", CORPUS)):
        subprocess.run([sys.executable, str(SCRIPT), "--_worker", str(arbre.resolve()),
                        "--sortie", str(args.sortie / cote), "--repetitions", str(args.repetitions)],
                       check=True, cwd=arbre,
                       env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONIOENCODING": "utf-8"})
    avant = (args.sortie / "avant/corpus.json").read_bytes()
    apres = (args.sortie / "apres/corpus.json").read_bytes()
    temps = {cote: json.loads((args.sortie / cote / "temps.json").read_text(encoding="utf-8"))
             for cote in ("avant", "apres")}
    rapport = {"identique": avant == apres, "cas": list(json.loads(avant)),
               "octets": len(avant), "sha256": hashlib.sha256(avant).hexdigest(), "temps": temps,
               "scenes_absentes": not (CORPUS / "tests/data/scenes").exists(),
               "ecarts_temps_pct": {fonction: 100 * (statistics.median(temps["apres"][fonction]) /
                                                    statistics.median(temps["avant"][fonction]) - 1)
                                    for fonction in ("public", "texte")}}
    (args.sortie / "rapport.json").write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({cle: valeur for cle, valeur in rapport.items() if cle not in ("cas", "temps")}, ensure_ascii=False))
    return int(avant != apres or any(ecart > 5 for ecart in rapport["ecarts_temps_pct"].values()))


if __name__ == "__main__":
    raise SystemExit(main())
