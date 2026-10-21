"""Configuration locale simple : quelques variables connues, jamais exécutée ni journalisée."""
import os
from pathlib import Path

MODELE_PAR_DEFAUT = "gpt-6-luna"
MODELE_CLAUDE = "claude-haiku-5-5"   # essai d'un autre fournisseur (--connexion anthropic)
MODELE_MIMO = "mimo-v2.6-flash"
DEFAUTS_CONNEXION = {"mimo": (MODELE_MIMO, "none")}
VARIABLES = ("OPENAI_API_KEY", "OPENAI_MODEL", "ANTHROPIC_API_KEY", "MIMO_API_KEY", "XIAOMI_API_KEY")


def charger_env(chemin=None):
    chemin = Path(chemin) if chemin else Path(__file__).resolve().parents[1] / ".env"
    if not chemin.is_file():
        return
    for ligne in chemin.read_text(encoding="utf-8-sig").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#") or "=" not in ligne:
            continue
        nom, valeur = ligne.split("=", 1)
        nom, valeur = nom.strip(), valeur.strip()
        if nom not in VARIABLES:
            continue
        if len(valeur) >= 2 and valeur[0] == valeur[-1] and valeur[0] in ("'", '"'):
            valeur = valeur[1:-1]
        if valeur:
            # Une configuration propre au projet remplace celle héritée du terminal.
            os.environ[nom] = valeur
