"""Sonde de réflexion : un modèle réfléchit-il, et peut-on le constater ?

  python tools/sonde_reflexion.py --fournisseur anthropic|chatgpt [--effort medium]

Hors du jeu : ni outil, ni schéma, ni consigne de format. Une question triviale sert de témoin,
une question de raisonnement à réponse vérifiable sert de charge. Pour chaque appel, la sonde
relève tout ce que l'API expose d'une réflexion (jetons, blocs, résumés) et la latence.
"""
import argparse
import json
from pathlib import Path
import sys
import time
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

QUESTIONS = {
    "temoin": ("Quelle est la capitale de la France ? Réponds en un mot.", "paris"),
    "raisonnement": ("Combien d'entiers de 1 à 1000 ne sont divisibles ni par 3, ni par 5, ni par 7 ? "
                     "Donne le nombre, puis une phrase de justification.", "457"),
}


def anthropic(question, effort, modele):
    import anthropic as sdk
    from donjon.config import charger_env
    charger_env()
    debut = time.monotonic()
    r = sdk.Anthropic().messages.create(
        model=modele, max_tokens=16000,
        thinking={"type": "adaptive", "display": "summarized"},
        output_config={"effort": effort},
        messages=[{"role": "user", "content": question}])
    secondes = time.monotonic() - debut
    pensees = [b.thinking for b in r.content if b.type == "thinking"]
    texte = "".join(b.text for b in r.content if b.type == "text")
    return {"secondes": round(secondes, 1), "blocs": [b.type for b in r.content],
            "jetons_sortie": r.usage.output_tokens, "caracteres_visibles": len(texte),
            "jetons_reflexion": "non exposés (inclus dans jetons_sortie)",
            "resume_reflexion": " | ".join(pensees)[:600], "reponse": texte.strip()}


def chatgpt(question, effort, modele):
    from donjon.connexion import jeton
    from donjon.mj import lire_flux
    payload = {"model": modele, "instructions": "Tu réponds en français.",
               "input": [{"role": "user", "content": question}],
               "reasoning": {"effort": effort, "summary": "auto"},
               "store": False, "stream": True}
    requete = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode(), method="POST",
        headers={"Authorization": "Bearer " + jeton(), "Content-Type": "application/json"})
    debut = time.monotonic()
    with urllib.request.urlopen(requete, timeout=180) as flux:
        r = lire_flux(flux)
    secondes = time.monotonic() - debut
    sortie = r.get("output", [])
    resumes = [s.get("text", "") for e in sortie if e.get("type") == "reasoning" for s in e.get("summary", [])]
    texte = "".join(c.get("text", "") for e in sortie if e.get("type") == "message" for c in e.get("content", []))
    usage = r.get("usage") or {}
    return {"secondes": round(secondes, 1), "blocs": [e.get("type") for e in sortie],
            "jetons_sortie": usage.get("output_tokens"), "caracteres_visibles": len(texte),
            "jetons_reflexion": (usage.get("output_tokens_details") or {}).get("reasoning_tokens"),
            "resume_reflexion": " | ".join(resumes)[:600], "reponse": texte.strip(),
            "evenements": r.get("_types_evenements")}


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--fournisseur", choices=("anthropic", "chatgpt"), required=True)
    p.add_argument("--effort", default="medium")
    p.add_argument("--modele")
    args = p.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    modele = args.modele or ("claude-haiku-5-5" if args.fournisseur == "anthropic" else "gpt-6-luna")
    appel = anthropic if args.fournisseur == "anthropic" else chatgpt
    for nom, (question, attendu) in QUESTIONS.items():
        mesure = appel(question, args.effort, modele)
        mesure["juste"] = attendu in mesure["reponse"].lower()
        print(json.dumps({"modele": modele, "effort": args.effort, "question": nom, **mesure},
                         ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
