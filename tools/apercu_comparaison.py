"""Captures de la vue debug avec des résultats simulés ; aucun appel réseau."""
import asyncio
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon.tui import SeuilApp


def fiche():
    resultats = {}
    for role, modele, couleur in (("principal", "gpt-6.1-sol", "gris clair"), ("secondaire", "gpt-6-luna", "bruns")):
        resultats[role] = {"modele": modele, "effort": "medium", "statut": "Terminé", "secondes": 3.45,
            "validation": "Compléments descriptifs validés sur une copie.",
            "appels": [
                {"etape": "interprétation", "usage": {"input_tokens": 4000, "output_tokens": 150},
                 "reponse": {"mode": "enrichir", "texte": "", "faits": ["descriptions_a_completer"],
                    "proposition": {"ajouts": [{"personnage": "marchand", "facette": "yeux", "description": "Ses yeux sont " + couleur + "."}]}}},
                {"etape": "narration après enrichissement", "usage": {"input_tokens": 4200, "output_tokens": 90},
                 "reponse": {"mode": "dialogue", "texte": "Tu te souviens des yeux " + couleur + " de Gorm.", "faits": ["souvenirs_personnages"], "proposition": None}},
            ]}
    return {"numero": 1, "revision": 4, "question": "De quelle couleur sont les yeux de Gorm ?", **resultats}


async def main():
    dossier = Path(__file__).resolve().parents[1] / "artifacts" / "tui"
    dossier.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory() as tmp:
        app = SeuilApp(["--offline", "--save", str(Path(tmp) / "partie.json")])
        async with app.run_test(size=(120, 40)) as pilot:
            for _ in range(250):
                if not app.occupe:
                    break
                await asyncio.sleep(.02)
            app.recevoir_comparaison(fiche())
            app.action_debug()
            for largeur, hauteur in ((120, 40), (80, 25), (60, 28)):
                await pilot.resize_terminal(largeur, hauteur)
                await pilot.pause()
                (dossier / f"comparaison_{largeur}.svg").write_text(app.export_screenshot(), encoding="utf-8")
            app.action_quitter()
            for _ in range(250):
                if not app.is_running:
                    break
                await asyncio.sleep(.02)
    print(dossier)


if __name__ == "__main__":
    asyncio.run(main())
