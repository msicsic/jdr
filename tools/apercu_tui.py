"""Exporte des captures SVG de la TUI hors ligne, sans toucher à la partie utilisateur."""
import asyncio
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon.tui import SeuilApp
from textual.widgets import Input


async def pret(app, minutes=0):
    for _ in range(250):
        if not app.occupe and app.derniere_vue.get("minutes") == minutes:
            return
        await asyncio.sleep(.02)
    raise RuntimeError("La TUI n'est pas prête")


async def main():
    dossier = Path(__file__).resolve().parents[1] / "artifacts" / "tui"
    dossier.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory() as tmp:
        app = SeuilApp(["--offline", "--save", str(Path(tmp) / "partie.json")])
        async with app.run_test(size=(120, 40)) as pilot:
            await pret(app)
            await pilot.pause()
            (dossier / "avant.svg").write_text(app.export_screenshot(), encoding="utf-8")
            app.query_one("#commande", Input).value = "prendre clé"
            await pilot.press("enter")
            await pret(app, 1)
            await pilot.pause()
            (dossier / "apres.svg").write_text(app.export_screenshot(), encoding="utf-8")
            await pilot.resize_terminal(80, 25)
            await pilot.pause()
            (dossier / "terminal_80.svg").write_text(app.export_screenshot(), encoding="utf-8")
            await pilot.resize_terminal(60, 28)
            await pilot.pause()
            (dossier / "terminal_60.svg").write_text(app.export_screenshot(), encoding="utf-8")
            app.action_quitter()
            for _ in range(250):
                if not app.is_running:
                    break
                await asyncio.sleep(.02)
    print(dossier)


if __name__ == "__main__":
    asyncio.run(main())
