"""Connexion explicite au forfait ChatGPT. Ne lit pas les identifiants d'autres applications."""
import argparse
import sys

from donjon.connexion import Coffre, connecter, deconnecter, modeles
from donjon.monde import ErreurMonde


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Connexion du jeu Le Seuil au forfait ChatGPT")
    p.add_argument("action", choices=["connecter", "statut", "modeles", "deconnecter"])
    p.add_argument("--nouveau", action="store_true", help="inscrire un autre compte ou espace ChatGPT")
    p.add_argument("--compte", help="identifiant d'une inscription listée par statut")
    args = p.parse_args(argv)
    try:
        coffre = Coffre()
        if args.action == "connecter":
            connecter(coffre, args.nouveau, args.compte)
        elif args.action == "statut":
            data = coffre.lire()
            if not data["comptes"]:
                print("Aucun compte connecté. Lancez : python connexion.py connecter")
            for id, c in data["comptes"].items():
                print(("* " if id == data["actif"] else "  ") + id + " — " + c.get("email", "inscription incomplète")
                      + (" — session enregistrée" if c.get("access_token") else " — reconnexion nécessaire"))
        elif args.action == "modeles":
            for m in modeles(coffre):
                print(m["slug"] + " — " + m["display_name"])
        else:
            deconnecter(coffre)
        return 0
    except (ErreurMonde, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
