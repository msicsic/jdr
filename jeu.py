"""Lancer : python jeu.py. Python 3.11+, Textual pour la TUI, mode --console disponible."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from donjon.commandes import AIDE, analyser, est_question
from donjon.config import charger_env, MODELE_PAR_DEFAUT
from donjon.connexion import Coffre, connecter
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, normaliser, nouveau_monde
from donjon.moteur import Moteur
from donjon.enrichissement import preparer_complements
from donjon.connaissances import preparer_savoirs
from donjon.dialogues import preparer_conversation, commande_sociale
from donjon.comparaison import Comparateur, texte_comparaison
from donjon.rendu import carte, fiche, regarder, decrire_accords


BASE = Path(__file__).resolve().parent


def demo():
    m = nouveau_monde(1985)
    moteur = Moteur(m)
    print("LE SEUIL — démonstration locale reproductible, aucune sauvegarde modifiée")
    print(carte(m))
    commandes = ["examiner porte", "examiner gravure", "copier gravure avec cire",
                 "prendre clé", "ouest", "acheter pied-de-biche", "est"]
    def jouer(cmd):
        print("\n> " + cmd)
        plan = moteur.preparer(analyser(m, cmd))
        print(moteur.executer(plan))
    for cmd in commandes:
        jouer(cmd)
    for axe in ("supérieur", "inférieur"):
        id = "axe_haut" if axe == "supérieur" else "axe_bas"
        while m.objets[id]["attache"]:
            jouer(f"retirer axe {axe} avec pied-de-biche")
    for cmd in ("nord", "ouvrir coffre avec clé", "prendre anneau", "sud", "examiner porte"):
        jouer(cmd)
    print("\n" + carte(m))
    print(fiche(m))
    return 0


def lancer_tui(argv):
    try:
        from donjon.tui import SeuilApp
    except ModuleNotFoundError as exc:
        if exc.name not in ("textual", "rich", "pyperclip"):
            raise
        executable = BASE / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        if executable.exists() and Path(sys.executable).resolve() != executable.resolve():
            import subprocess
            return subprocess.call([str(executable), str(BASE / "jeu.py"), "--tui", *argv])
        print("La TUI nécessite Textual : python -m pip install -r requirements-tui.txt. "
              "Le mode --console reste disponible.", file=sys.stderr)
        return 1
    return SeuilApp(argv).run() or 0


def main(argv=None, interface=None):
    charger_env()
    parser = argparse.ArgumentParser(description="Le Seuil — donjon ASCII et maître du jeu IA")
    parser.add_argument("--offline", action="store_true", help="aucun appel au LLM")
    parser.add_argument("--connexion", choices=["auto", "api", "chatgpt"], default="auto",
                        help="auto privilégie le compte ChatGPT enregistré, sinon la clé API")
    parser.add_argument("--new", action="store_true", help="nouvelle partie ; conserve une copie .bak de la sauvegarde existante")
    parser.add_argument("--atelier", action="store_true", help="scène de fabrication, sauvegarde séparée atelier.json")
    parser.add_argument("--defi", action="store_true", help="Le Relais des crues, défi d'exploration avec sauvegarde séparée")
    parser.add_argument("--cases", action="store_true", help="déplacements case par case, proximité et ligne de vue")
    parser.add_argument("--seed", type=int, default=1985, help="graine d'une nouvelle partie")
    parser.add_argument("--save", type=Path, default=BASE / "sauvegardes" / "partie.json")
    parser.add_argument("--model", default=os.environ.get("OPENAI_MODEL", MODELE_PAR_DEFAUT))
    parser.add_argument("--effort", choices=["low", "medium", "high"], default="medium")
    parser.add_argument("--debug", action="store_true", help="autorise etat <objet> pour inspecter le monde")
    parser.add_argument("--compare-model", nargs="?", const="gpt-6-luna", metavar="MODELE",
                        help="compare en arrière-plan avec ce modèle (gpt-6-luna si omis)")
    parser.add_argument("--compare-effort", choices=["low", "medium", "high"],
                        help="effort du second modèle ; identique au principal par défaut")
    parser.add_argument("--demo", action="store_true", help="joue une démonstration sans API et sans sauvegarde")
    parser.add_argument("--console", action="store_true", help="ancien affichage ligne par ligne")
    parser.add_argument("--tui", action="store_true", help="interface plein écran")
    args = parser.parse_args(argv)
    if args.atelier and args.defi:
        parser.error("Choisis --atelier ou --defi.")
    if args.defi and args.save == BASE / "sauvegardes" / "partie.json":
        args.save = BASE / "sauvegardes" / "defi.json"
    if args.atelier and args.save == BASE / "sauvegardes" / "partie.json":
        args.save = BASE / "sauvegardes" / "atelier.json"
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if args.demo:
        return demo()
    if interface is None and not args.console and (args.tui or (sys.stdin.isatty() and sys.stdout.isatty())):
        return lancer_tui(list(argv) if argv is not None else sys.argv[1:])
    imprimer = interface.ecrire if interface else print
    lire = interface.lire if interface else input
    def afficher(vue):
        if interface:
            interface.montrer(vue)
        else:
            imprimer({"carte": carte, "scene": regarder, "fiche": fiche}[vue](m))
    def comparer(principal):
        if not args.compare_model:
            if args.debug:
                from donjon.harnais import JournalMJ
                principal.observateur = JournalMJ(BASE / "artifacts" / "mj",
                                                  publier=interface.comparaison if interface else None,
                                                  effort=principal.effort)
            return principal
        secondaire = MJOpenAI(args.compare_model, args.compare_effort or args.effort,
                              connexion=principal.connexion)
        return Comparateur(principal, secondaire,
                           publier=interface.comparaison if interface else None,
                           dossier=BASE / "artifacts" / "comparaisons")
    mj = None
    try:
        if args.save.exists() and not args.new:
            m = Monde.charger(args.save)
        else:
            if args.save.exists():
                # Sauvegarde précédente conservée, avec un nom disponible.
                sauvegarde = args.save.with_suffix(".json.bak")
                indice = 1
                while sauvegarde.exists():
                    sauvegarde = args.save.with_suffix(f".json.{indice}.bak")
                    indice += 1
                sauvegarde.write_bytes(args.save.read_bytes())
            if args.defi:
                from donjon.defi import nouveau_defi
                m = nouveau_defi(args.seed)
            elif args.atelier:
                from donjon.atelier import nouveau_atelier
                m = nouveau_atelier(args.seed)
            else:
                m = nouveau_monde(args.seed)
        if args.cases or args.defi or m.data.get("mode_cases"):
            from donjon.spatial import installer as installer_cases
            installer_cases(m)
        moteur = Moteur(m)
        connexion = args.connexion
        if connexion == "auto" and not args.offline:
            connexion = "chatgpt" if Coffre().compte() else "api"
        actif = not args.offline and (connexion == "chatgpt" or bool(os.environ.get("OPENAI_API_KEY")))
        mj = MJOpenAI(args.model, args.effort, connexion=connexion) if actif else None
        if mj:
            mj = comparer(mj)
        if isinstance(mj, Comparateur):
            imprimer(f"Comparaison active : {args.model} / {args.compare_model}. Le second modèle ne modifie pas la partie. "
                     "Les appels des deux modèles consomment le forfait ou l'API. F5 : vue debug ; « comparaison » : résultats.")
        elif args.compare_model:
            imprimer("Comparaison inactive : MJ hors ligne. Aucun appel au second modèle.")
        if interface is None:
            imprimer("\nLE SEUIL — prototype testvrac | " + str(BASE))
            imprimer("MJ : " + (f"{args.model} / {args.effort} / {connexion}" if actif else "hors ligne (commandes locales)"))
            if actif:
                imprimer("Les phrases libres utilisent " + ("votre forfait ChatGPT et ses limites." if connexion == "chatgpt" else "la clé API OpenAI, avec une facturation séparée."))
        imprimer(m.data["scenario"]["objectif"] + " « aide » : commandes disponibles.")
        if not m.data["journal"]:
            imprimer(m.data["scenario"]["debut"])
        if interface is None:
            afficher("carte")
            afficher("scene")
            afficher("fiche")
        pending = None
        comparaison_pending = 0

        def conclure(plan, resultat, intention, numero=0):
            # Résoudre et sauvegarder une seule fois AVANT toute narration distante.
            m.memoriser(intention, resultat, "resultat_moteur")
            m.sauver(args.save)
            if isinstance(mj, Comparateur) and numero:
                mj.noter_resultat(resultat, numero=numero)
            if plan.proposition["action"] not in ("composer", "fabriquer", "installer", "franchir", "desinstaller") or mj is None:
                imprimer(resultat)
                return
            imprimer("Le MJ raconte le résultat…", flush=True)
            try:
                reponse = mj.raconter_resultat(m, m.data["journal"][-1])
            except ErreurMonde as exc:
                imprimer(resultat)
                imprimer("Récit indisponible ; la manœuvre est déjà résolue et sauvegardée. " + str(exc))
                return
            m.memoriser(intention, reponse["texte"], "narration_resultat")
            m.sauver(args.save)
            jets = [ligne for ligne in resultat.splitlines() if ligne.startswith("1d20(")]
            if jets:
                imprimer("\n".join(jets))
            imprimer(reponse["texte"])

        while True:
            if interface:
                interface.rafraichir(m, pending, mj)
            try:
                texte = lire("\nCorvus > ").strip()
            except (EOFError, KeyboardInterrupt):
                imprimer()
                texte = "quitter"
            cmd = normaliser(texte)
            if not cmd:
                continue
            try:
                if cmd in ("quitter", "q", "exit"):
                    m.sauver(args.save)
                    imprimer("Partie sauvegardée. A bientôt.")
                    return 0
                if cmd == "tenter":
                    if pending is None:
                        imprimer("Aucune proposition en attente.")
                        continue
                    plan = pending
                    resultat = moteur.executer(plan)
                    pending = None
                    conclure(plan, resultat, "tenter", comparaison_pending)
                    if plan.proposition["action"] == "aller":
                        afficher("carte")
                        afficher("scene")
                    continue
                if cmd == "annuler":
                    pending = None
                    m.memoriser(texte, "Proposition abandonnée sans exécution.", "annulation")
                    imprimer("Proposition abandonnée.")
                    continue
                if cmd == "connecter":
                    if args.offline:
                        imprimer("Le mode --offline interdit la connexion. Relancez sans --offline pour connecter le forfait.")
                        continue
                    connecter(afficher=imprimer)
                    connexion, actif = "chatgpt", True
                    if isinstance(mj, Comparateur):
                        mj.fermer()
                    mj = comparer(MJOpenAI(args.model, args.effort, connexion="chatgpt"))
                    pending = None
                    continue
                if cmd in ("comparaison", "debug"):
                    if interface:
                        interface.montrer("debug")
                    elif isinstance(mj, Comparateur) and mj.fiches:
                        with mj.verrou:
                            imprimer(texte_comparaison(mj.fiches[mj.numero]))
                    else:
                        imprimer("Aucune comparaison. Lancez avec --compare-model gpt-6-luna puis adressez une phrase au MJ.")
                    continue
                if cmd == "connexion":
                    imprimer("MJ : " + (mj.connexion if mj else "hors ligne"))
                    if mj and mj.erreur_auth:
                        imprimer(mj.erreur_auth)
                    imprimer("« connecter » ouvre la connexion au forfait ChatGPT. Aucune clé API n'est nécessaire pour ce mode.")
                    continue
                if cmd == "accords":
                    imprimer(decrire_accords(m))
                    continue
                try:
                    social = commande_sociale(m, texte)
                except ErreurMonde:
                    if mj is None:
                        raise
                    social = None
                if social:
                    travail, rapport = preparer_conversation(m, social)
                    resultat = " ".join(rapport["faits"])
                    suite = Moteur(travail).preparer(pending.proposition, pending.origine) if pending else None
                    travail.memoriser(texte, resultat, "conversation_pnj")
                    travail.sauver(args.save)
                    m.data, pending = travail.data, suite
                    imprimer(resultat)
                    continue
                if cmd in ("aide", "?", "regarder", "carte", "fiche", "inventaire", "journal", "sauver"):
                    if cmd in ("aide", "?"):
                        imprimer(AIDE)
                    elif cmd == "regarder":
                        afficher("carte")
                        afficher("scene")
                    elif cmd == "carte":
                        afficher("carte")
                    elif cmd in ("fiche", "inventaire"):
                        afficher("fiche")
                    elif cmd == "journal":
                        for e in m.data["journal"][-12:]:
                            imprimer(f'[{e["minutes"]} min] {e["action"]["action"]} ({e["origine"]}) : ' + " ".join(e["faits"]))
                    else:
                        m.sauver(args.save)
                        imprimer("Partie sauvegardée.")
                    continue
                if cmd.startswith("etat "):
                    if not args.debug:
                        imprimer("Commande réservée au lancement avec --debug.")
                    else:
                        imprimer(json.dumps(m.objets[m.trouver(cmd[5:])], ensure_ascii=False, indent=2))
                    continue
                force_mj = cmd.startswith("mj ")
                question = est_question(texte)
                try:
                    p = None if force_mj or question else analyser(m, texte)
                except ErreurMonde:
                    if mj is None:
                        raise
                    # « Retirer les gonds avec mon petit couteau » peut dépasser la syntaxe locale.
                    p = None
                if mj is not None and p and p["action"] == "parler":
                    p = None
                if (mj is not None and p and p["action"] == "examiner"
                        and m.objets.get(p["cible"], {}).get("type") == "personnage"
                        and not m.objets[p["cible"]].get("portrait")
                        and not m.objets[p["cible"]].get("facettes")):
                    p = None
                if p is None:
                    if mj is None:
                        if question:
                            imprimer("MJ hors ligne : je ne peux pas interpréter cette question. "
                                  "Commandes disponibles : contexte, lumière, regarder, journal.")
                        else:
                            imprimer("Cette phrase nécessite le MJ IA. Tapez « aide » pour les commandes hors ligne.")
                        continue
                    imprimer("Le MJ réfléchit…", flush=True)
                    reponse = mj.echanger(m, texte[3:] if force_mj else texte,
                                         pending.proposition if pending else None)
                    if "_espace" in reponse:
                        from donjon.espace import preparer as preparer_espace
                        ajout = reponse["_espace"]
                        travail = preparer_espace(m, ajout["proposition"], ajout["revision"])
                        suite = Moteur(travail).preparer(pending.proposition, pending.origine) if pending else None
                        travail.sauver(args.save)
                        m.data, pending = travail.data, suite
                    if reponse["mode"] == "dialogue":
                        if "_conversation_pnj" in reponse:
                            ajout = reponse["_conversation_pnj"]
                            travail, rapport = preparer_conversation(m, ajout["proposition"], ajout["revision"])
                            suite = Moteur(travail).preparer(pending.proposition, pending.origine) if pending else None
                            travail.memoriser(texte, reponse["texte"], "conversation_pnj")
                            travail.sauver(args.save)
                            m.data, pending = travail.data, suite
                            imprimer(reponse["texte"])
                            if isinstance(mj, Comparateur):
                                mj.noter_resultat(reponse["texte"], rapport)
                            continue
                        if "_enrichissement" in reponse or "_savoirs" in reponse or "_profil_joueur" in reponse:
                            savoirs = "_savoirs" in reponse
                            profil = "_profil_joueur" in reponse
                            ajout = reponse["_profil_joueur" if profil else "_savoirs" if savoirs else "_enrichissement"]
                            preparer = preparer_savoirs if savoirs else preparer_complements
                            if profil:
                                from donjon.profil_joueur import preparer
                            travail = preparer(m, ajout["proposition"], ajout["revision"])
                            suite = Moteur(travail).preparer(pending.proposition, pending.origine) if pending else None
                            travail.memoriser(texte, reponse["texte"])
                            # Ne montrer la nouvelle fiction qu'après sa sauvegarde réussie.
                            travail.sauver(args.save)
                            m.data, pending = travail.data, suite
                            imprimer(reponse["texte"])
                            if savoirs and isinstance(mj, Comparateur):
                                mj.noter_savoirs(reponse["texte"], ajout["proposition"])
                            continue
                        imprimer(reponse["texte"])
                        m.memoriser(texte, reponse["texte"],
                                   "refus_avant_action" if reponse.get("_validation_refusee") else "dialogue")
                        m.sauver(args.save)
                        continue
                    p = reponse["proposition"]
                    if question and p.get("action") not in ("observer", "examiner", "clarifier", "impossible"):
                        imprimer("Le MJ a proposé une action à une question. Aucune action n'a été appliquée.")
                        imprimer("Précisez une action si vous souhaitez la tenter, ou consultez contexte / regarder.")
                        continue
                    pending = None
                    if p.get("action") in ("clarifier", "impossible"):
                        # Valide les champs par le même chemin que toute proposition.
                        try:
                            moteur.preparer(p, origine="LLM : " + mj.modele)
                        except ErreurMonde as exc:
                            imprimer(str(exc))
                            m.memoriser(texte, str(exc), "avis_sans_action")
                            m.sauver(args.save)
                        continue
                    pending = moteur.preparer(p, origine="reprise mémorisée" if reponse.get("_reprise_locale") else "LLM : " + mj.modele)
                    comparaison_pending = mj.numero if isinstance(mj, Comparateur) else 0
                    if not pending.stat and not pending.echec_critique:
                        plan = pending
                        resultat = moteur.executer(plan)
                        pending = None
                        conclure(plan, resultat, texte, comparaison_pending)
                        if p["action"] == "aller":
                            afficher("carte")
                            afficher("scene")
                        continue
                    imprimer("\n" + pending.resume(m))
                    m.memoriser(texte, pending.resume(m), "proposition_non_executee")
                    m.sauver(args.save)
                    if not pending.etapes:
                        imprimer("« tenter » pour agir ; « annuler » pour abandonner.")
                else:
                    if p["action"] != "observer":
                        pending = None
                    plan = moteur.preparer(p)
                    resultat = moteur.executer(plan)
                    mouvement = m.data.get("mode_cases") and p["action"] in ("marcher", "aller")
                    if not mouvement or interface is None:
                        imprimer(resultat)
                    else:
                        evenements = [ligne for ligne in resultat.splitlines() if ligne != "Tu avances d'un pas."]
                        if evenements:
                            imprimer("\n".join(evenements))
                    if not mouvement:
                        m.memoriser(texte, resultat, "resultat_moteur")
                    m.sauver(args.save)
                    if p["action"] == "aller" and not mouvement:
                        afficher("carte")
                        afficher("scene")
            except ErreurMonde as exc:
                pending = None
                imprimer(str(exc))
            except OSError as exc:
                imprimer(f"Ecriture de sauvegarde impossible : {exc}. La partie reste en mémoire ; réessayez sauver.")
    except (ErreurMonde, OSError) as exc:
        imprimer(str(exc), file=sys.stderr)
        return 1
    finally:
        if isinstance(mj, Comparateur):
            mj.fermer()


if __name__ == "__main__":
    raise SystemExit(main())
