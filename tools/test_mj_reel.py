"""Test réel volontaire : quatre appels au MJ (forfait ChatGPT ou clé API selon le mode choisi)."""
import argparse
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon.mj import MJOpenAI
from donjon.config import charger_env
from donjon.connexion import Coffre
from donjon.monde import ErreurMonde, nouveau_monde
from donjon.moteur import Moteur


def main():
    charger_env()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--model")
    parser.add_argument("--connexion", choices=["auto", "api", "chatgpt"], default="auto")
    args = parser.parse_args()
    mode = args.connexion
    if mode == "auto":
        mode = "chatgpt" if Coffre().compte() else "api"
    mj = MJOpenAI(args.model, connexion=mode)
    scenarios = [
        ("mais comment je suis arrivé ici ?", "observer", "contexte"),
        ("comment je peux voir s'il n'y a pas de fenetres ?", "observer", "lumiere"),
        ("Je glisse la pointe de mon couteau sous la tête de l'axe supérieur et fais doucement levier pour l'extraire.", "detacher", "axe_haut"),
        ("Je soulève directement les 80 kg du battant avec la lame de mon couteau pour dégonder toute la porte d'un coup.", "impossible", ""),
    ]
    for intention, attendu, cible in scenarios:
        m = nouveau_monde()
        debut = time.monotonic()
        try:
            p = mj.proposer(m, intention)
            print(json.dumps({"modele": mj.modele, "intention": intention, "proposition": p,
                              "secondes": round(time.monotonic() - debut, 2),
                              "usage": {k: (mj.derniere_utilisation or {}).get(k)
                                        for k in ("input_tokens", "output_tokens", "total_tokens")}}, ensure_ascii=False, indent=2), flush=True)
            if p.get("action") != attendu:
                raise ErreurMonde(f"Attendu {attendu}, reçu {p.get('action')}")
            if p.get("cible") != cible:
                raise ErreurMonde(f"Cible attendue {cible}, reçue {p.get('cible')}")
            if attendu == "observer":
                moteur = Moteur(m)
                print(moteur.executer(moteur.preparer(p, "LLM")), flush=True)
            if attendu == "detacher":
                if p.get("cible") != "axe_haut" or p.get("outil") != "couteau":
                    raise ErreurMonde("Mauvaise cible ou mauvais outil")
                plan = Moteur(m).preparer(p, "LLM")
                print(plan.resume(m), flush=True)
                assert 17 <= plan.dd <= 22
            assert m.data["revision"] == 0, "Une proposition ne doit pas modifier le monde"
        except ErreurMonde as exc:
            if mj.derniere_sortie:
                print("Types de sortie : " + json.dumps(mj.derniere_sortie, ensure_ascii=False), flush=True)
            print(str(exc), file=sys.stderr)
            return 1
    print("Quatre échanges réels vérifiés ; aucun monde modifié.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
