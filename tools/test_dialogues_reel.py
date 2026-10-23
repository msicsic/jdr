"""Offre, négociation, acceptation et remise réelles ; sept appels au maximum prévu.

L'anneau est placé dans l'inventaire du monde de test avant la remise pour isoler ce parcours.
Aucune sauvegarde utilisateur n'est chargée ni modifiée.
"""
import copy
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon import agendas
from donjon.config import charger_env
from donjon.dialogues import preparer_conversation
from donjon.mj import MJOpenAI
from donjon.monde import Monde, nouveau_monde
from donjon.moteur import Moteur
from donjon.transactions import du_type


def main():
    charger_env()
    sys.stdout.reconfigure(encoding="utf-8")
    m = nouveau_monde()
    m.joueur["salle"] = "echoppe"
    m.memoriser("je demande a gorn ce que j'y gagne a retrouver cet anneau",
                "Gorm : « Mes prix tiennent déjà compte de votre charisme. Un bon levier ménage la lame. »", "resultat_moteur")
    mj = MJOpenAI(connexion="chatgpt")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "partie.json"
        for message, statut, montant in (
            ("je demande a gorn ce que j'y gagne a retrouver cet anneau", "propose", 20),
            ("Gorm, c'est peu. Je voudrais 40 pièces pour te ramener cet anneau.", "propose", 22),
            ("D'accord Gorm, j'accepte ton offre de 22 pièces.", "accepte", 22),
        ):
            avant = copy.deepcopy(m.data)
            r = mj.echanger(m, message)
            assert m.data == avant
            assert r["mode"] == "dialogue" and du_type(r, "conversation_pnj"), r
            p = du_type(r, "conversation_pnj")
            m, rapport = preparer_conversation(m, p["proposition"], p["revision"])
            assert rapport["engagement"] == {"statut": statut, "montant": montant}, rapport
            assert m.joueur["or"] == 24
            m.memoriser(message, r["texte"], "conversation_pnj")
            m.sauver(path)
            m = Monde.charger(path)
            print("Corvus > " + message + "\n" + r["texte"] + "\n", flush=True)
        m.objets["anneau"]["lieu"] = "joueur"
        message = "Gorm, je te remets l'anneau du veilleur en échange des 22 pièces convenues."
        r = mj.echanger(m, message)
        assert r["mode"] == "action" and r["proposition"]["action"] == "remettre", r
        moteur = Moteur(m)
        resultat = moteur.executer(moteur.preparer(r["proposition"]))
        print("Corvus > " + message + "\n" + resultat, flush=True)
        assert m.joueur["or"] == 46 and m.data["finances_pnj"]["marchand"] == 28
        assert m.objets["anneau"]["lieu"] == "marchand"
        assert agendas.contrats(m)["anneau_veilleur"]["statut"] == "paye"
    print("Parcours vérifié : offre, contre-offre, acceptation persistante et paiement. Aucune partie utilisateur modifiée.")


if __name__ == "__main__":
    main()
