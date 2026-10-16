"""Rejoue un corpus de descriptions avec le contre-lecteur Luna et des parties temporaires.

Le premier fait proposé est fixé par le corpus pour isoler le contrôle de portée.
Si Luna le refuse, une description locale fixée par le harnais sert de correction.
Le moteur, l'affichage console et la sauvegarde suivent ensuite leur parcours normal.
"""

import argparse
import contextlib
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import sys
import tempfile
import time
from unittest.mock import patch

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

import jeu
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, nouveau_monde
from donjon.portee_narrative import controler, descriptions
from donjon.rendu import decrire


CORPUS = RACINE / "tests" / "data" / "corpus_portee_narrative.json"
RAPPORT = RACINE / "artifacts" / "evaluations" / "portee_narrative.json"
CORRECTION = {"nom": "trace d'enduit", "genre": "f",
              "texte": "Une trace d'enduit pâle marque la pierre."}
CORRECTION_PORTRAIT = "Ses yeux sont gris clair."


def charger_corpus(chemin=CORPUS):
    cas = json.loads(chemin.read_text(encoding="utf-8"))
    if not isinstance(cas, list) or not cas or any(not isinstance(c, dict) for c in cas):
        raise ValueError("Corpus de portée invalide.")
    ids = [c.get("id") for c in cas]
    if (len(ids) != len(set(ids))
            or any((set(c) != ({"id", "mode", "attendu", "facette", "texte"}
                                if c.get("mode") == "portrait" else
                                {"id", "attendu", "nom", "genre", "texte"})
                    or c.get("attendu") not in ("accepter", "refuser")
                    or (c.get("facette") != "yeux" if c.get("mode") == "portrait"
                        else c.get("genre") not in ("m", "f"))
                    or any(not isinstance(c.get(k), str) or not c[k].strip()
                           for k in (("id", "texte") if c.get("mode") == "portrait"
                                     else ("id", "nom", "texte")))) for c in cas)):
        raise ValueError("Corpus de portée invalide.")
    return cas


def proposition(cas, correction=False):
    if cas.get("mode") == "portrait":
        return {"mode": "enrichir", "texte": "", "faits": ["descriptions_a_completer"],
                "proposition": {"ajouts": [{"personnage": "marchand", "facette": cas["facette"],
                                           "description": (CORRECTION_PORTRAIT if correction
                                                           else cas["texte"])}]}}
    donnees = CORRECTION if correction else cas
    nom, genre, texte = (donnees[k] for k in ("nom", "genre", "texte"))
    return {"mode": "etablir_faits", "texte": "",
            "faits": ["faits_narratifs_proposables"],
            "proposition": {"ajouts": [{"type": "detail", "ancrage": "antichambre_murs",
                                       "nom": nom, "genre": genre, "texte": texte}]}}


def jouer(cas):
    original = MJOpenAI._appeler_brut
    rapports = []
    appels = 0
    reponses = 0
    debut = time.monotonic()
    sortie = io.StringIO()
    with tempfile.TemporaryDirectory(dir=RACINE) as dossier:
        chemin = Path(dossier) / "partie.json"
        monde = nouveau_monde()
        if cas.get("mode") == "portrait":
            monde.joueur["salle"] = "echoppe"
        monde.sauver(chemin)

        def appeler(self, instructions, entree, intention, fonction, schema):
            nonlocal appels, reponses
            if fonction == "repondre_au_joueur":
                modes = schema.get("properties", {}).get("mode", {}).get("enum", [])
                if cas.get("mode") == "portrait" and modes == ["dialogue"]:
                    phrases = entree["faits"]["attestations"]
                    phrase = next((p for p in phrases if "gris clair" in p), phrases[0])
                    return {"mode": "dialogue", "texte": phrase,
                            "faits": ["attestations"], "proposition": None}
                reponses += 1
                if reponses == 1:
                    return proposition(cas)
                return proposition(cas, correction=True)
            appels += 1
            resultat = original(self, instructions, entree, intention, fonction, schema)
            if fonction == "auditer_portee":
                entrees = descriptions(proposition(cas, correction=reponses > 1))
                try:
                    obstacles = controler(entrees, resultat,
                                         entree.get("attestations", []))
                    probleme = ""
                except ErreurMonde as exc:
                    obstacles, probleme = [], str(exc)
                rapports.append({"entrees": entrees, "rapport": resultat,
                                 "obstacles": obstacles, "erreur_format": probleme})
            return resultat

        with (patch.object(MJOpenAI, "_appeler_brut", appeler),
              patch("builtins.input", side_effect=["mj Décris un détail sur les murs.", "quitter"]),
              contextlib.redirect_stdout(sortie)):
            code = jeu.main(["--console", "--save", str(chemin), "--connexion", "auto",
                             "--model", "gpt-6-luna"])
        reprise = Monde.charger(chemin)
        details = ([reprise.objets["detail_marchand_yeux"]]
                   if cas.get("mode") == "portrait" and "detail_marchand_yeux" in reprise.objets
                   else [o for o in reprise.objets.values() if o.get("detail_local")]
                   if cas.get("mode") != "portrait" else [])
        original_sauve = any(o.get("description_visuelle") == cas["texte"] and
                             (cas.get("mode") == "portrait" or o["nom"] == cas["nom"])
                             for o in details)
        texte_affiche = cas["texte"] in sortie.getvalue()
        rendu_recharge = [decrire(reprise, o["id"], detail=True) for o in details]
        relecture_ok = any(cas["texte"] in r for r in rendu_recharge)
        premier = rapports[0] if rapports else None
        decision = ("erreur" if not premier or premier["erreur_format"] else
                    "refuser" if premier["obstacles"] else "accepter")
        integrite = (original_sauve and texte_affiche and relecture_ok if decision == "accepter"
                     else not original_sauve and not texte_affiche and not relecture_ok)
        return {
            "id": cas["id"], "mode": cas.get("mode", "detail"),
            "attendu": cas["attendu"], "decision": decision,
            "conforme": decision == cas["attendu"] and integrite and code == 0,
            "code": code, "integrite": integrite, "original_sauve": original_sauve,
            "texte_affiche": texte_affiche, "relecture_ok": relecture_ok,
            "details_sauves": [{"nom": o["nom"], "description": o.get("description_visuelle", "")}
                               for o in details],
            "narration_sauvee": [e["texte"] for e in reprise.data.get("narrations_mj", [])],
            "sortie": sortie.getvalue(), "rapports": rapports,
            "appels_luna": appels, "secondes": round(time.monotonic() - debut, 2),
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", action="append", dest="ids", help="Identifiant à rejouer ; répétable")
    parser.add_argument("--limit", type=int, help="Nombre maximal de cas")
    parser.add_argument("--corpus", type=Path, default=CORPUS)
    parser.add_argument("--rapport", type=Path, default=RAPPORT)
    args = parser.parse_args()
    cas = charger_corpus(args.corpus)
    if args.ids:
        inconnus = set(args.ids) - {c["id"] for c in cas}
        if inconnus:
            parser.error("Cas inconnus : " + ", ".join(sorted(inconnus)))
        cas = [c for c in cas if c["id"] in args.ids]
    if args.limit is not None:
        if args.limit < 1:
            parser.error("--limit doit être positif")
        cas = cas[:args.limit]
    rapport = {"date_utc": datetime.now(timezone.utc).isoformat(),
               "modele": "gpt-6-luna", "corpus": str(args.corpus), "cas": []}
    args.rapport.parent.mkdir(parents=True, exist_ok=True)
    for index, item in enumerate(cas, 1):
        try:
            resultat = jouer(item)
        except Exception as exc:
            resultat = {"id": item["id"], "attendu": item["attendu"],
                        "decision": "erreur", "conforme": False, "erreur": str(exc)}
        rapport["cas"].append(resultat)
        args.rapport.write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
        etat = "OK" if resultat["conforme"] else "ÉCART"
        print(f"{index}/{len(cas)} {item['id']}: {resultat['decision']} "
              f"(attendu {item['attendu']}) {etat}", flush=True)
    print("Rapport :", args.rapport, flush=True)
    return 0 if all(c["conforme"] for c in rapport["cas"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
