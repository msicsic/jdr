"""Lancer : python jeu.py. Python 3.11+, Textual pour la TUI, mode --console disponible."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from donjon.commandes import AIDE, PERCEPTIONS, analyser, cri, est_question
from donjon.config import charger_env, MODELE_CLAUDE, MODELE_PAR_DEFAUT
from donjon.connexion import Coffre, connecter
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, normaliser, nouveau_monde
from donjon.moteur import Moteur, QualificationRequise, gestes_accomplis
from donjon.narration import (consigner as consigner_narration, rendre_resultat,
                              chiffres_sans_fondement)
from donjon.dialogues import preparer_conversation, commande_sociale
from donjon.transactions import appliquer as appliquer_transactions
from donjon.comparaison import Comparateur, texte_comparaison
from donjon.rendu import carte, fiche, regarder, decrire_accords


BASE = Path(__file__).resolve().parent


def demo():
    from donjon.scenario_crypte import demo as demo_crypte
    return demo_crypte()


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


def lancer_web(argv, port):
    """La partie dans le navigateur : un serveur local (127.0.0.1) et la boucle de jeu branchée sur
    la page par un PontWeb, comme le terminal par son pont."""
    import threading
    import webbrowser
    from donjon.web.pont import PontWeb
    from donjon.web.serveur import Serveur
    pont = PontWeb()
    try:
        serveur = Serveur(pont, port)
    except OSError:
        serveur = Serveur(pont, 0)  # Le port demandé est pris : un autre, libre.
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    print("Le Seuil se joue dans le navigateur : " + serveur.adresse + "  (Ctrl+C ou « quitter » pour finir)")
    webbrowser.open(serveur.adresse)
    try:
        return main([a for a in argv if a != "--web"], interface=pont)
    finally:
        pont.termine = True
        serveur.arreter()


def main(argv=None, interface=None):
    charger_env()
    parser = argparse.ArgumentParser(description="Le Seuil — donjon ASCII et maître du jeu IA")
    parser.add_argument("--offline", action="store_true", help="aucun appel au LLM")
    parser.add_argument("--connexion", choices=["auto", "api", "chatgpt", "anthropic"], default="auto",
                        help="auto privilégie le compte ChatGPT enregistré, sinon la clé API")
    parser.add_argument("--new", action="store_true", help="nouvelle partie ; conserve une copie .bak de la sauvegarde existante")
    parser.add_argument("--atelier", action="store_true", help="scène de fabrication, sauvegarde séparée atelier.json")
    parser.add_argument("--defi", action="store_true", help="Le Relais des crues, défi d'exploration avec sauvegarde séparée")
    parser.add_argument("--mine", action="store_true", help="La mine de Cendrefer, camp coupé du monde, avec sauvegarde séparée")
    parser.add_argument("--auberge", action="store_true",
                        help="L'auberge du Col-Pendu, une nuit de tempête avec huit personnages ; sauvegarde séparée auberge.json")
    parser.add_argument("--crue", action="store_true",
                        help="la crue du Relais : l'eau monte selon la graine, sauvegarde séparée crue.json")
    parser.add_argument("--cases", action="store_true", help="déplacements case par case, proximité et ligne de vue")
    parser.add_argument("--seed", type=int, default=1985, help="graine d'une nouvelle partie")
    parser.add_argument("--save", type=Path, default=BASE / "sauvegardes" / "partie.json")
    parser.add_argument("--model", default=os.environ.get("OPENAI_MODEL", MODELE_PAR_DEFAUT))
    parser.add_argument("--effort", choices=["low", "medium", "high"], default="medium")
    parser.add_argument("--reflexion", choices=["libre", "imposee"], default="libre",
                        help="anthropic : réflexion adaptative (défaut), ou outil imposé sans réflexion, plus rapide")
    parser.add_argument("--stratege", action="store_true",
                        help="Luna conseille les PNJ quand le moteur n'a pas de plan (appels plafonnés par heure de jeu)")
    parser.add_argument("--debug", action="store_true", help="autorise etat <objet> pour inspecter le monde")
    parser.add_argument("--compare-model", nargs="?", const="gpt-6-luna", metavar="MODELE",
                        help="compare en arrière-plan avec ce modèle (gpt-6-luna si omis)")
    parser.add_argument("--compare-effort", choices=["low", "medium", "high"],
                        help="effort du second modèle ; identique au principal par défaut")
    parser.add_argument("--demo", action="store_true", help="joue une démonstration sans API et sans sauvegarde")
    parser.add_argument("--console", action="store_true", help="ancien affichage ligne par ligne")
    parser.add_argument("--tui", action="store_true", help="interface plein écran dans le terminal")
    parser.add_argument("--web", action="store_true",
                        help="jouer dans le navigateur (serveur local 127.0.0.1) ; le défaut dans un terminal")
    parser.add_argument("--port", type=int, default=8765, help="port local de --web")
    parser.add_argument("--recit-moteur", action="store_true",
                        help="affiche les résultats d'action rédigés par le moteur, sans récit de Luna")
    args = parser.parse_args(argv)
    if args.atelier + args.defi + args.mine + args.auberge + args.crue > 1:
        parser.error("Choisis --atelier, --defi, --mine, --auberge ou --crue.")
    for scenario in ("mine", "auberge", "crue"):
        if getattr(args, scenario) and args.save == BASE / "sauvegardes" / "partie.json":
            args.save = BASE / "sauvegardes" / f"{scenario}.json"
    if args.defi and args.save == BASE / "sauvegardes" / "partie.json":
        args.save = BASE / "sauvegardes" / "defi.json"
    if args.crue and args.save == BASE / "sauvegardes" / "partie.json":
        args.save = BASE / "sauvegardes" / "crue.json"
    if args.atelier and args.save == BASE / "sauvegardes" / "partie.json":
        args.save = BASE / "sauvegardes" / "atelier.json"
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if args.demo:
        return demo()
    if interface is None and not args.console:
        # Dans un terminal, on joue dans le navigateur, sauf --tui ; sans terminal (entrée
        # redirigée, scripts), l'affichage ligne par ligne.
        interactif = sys.stdin.isatty() and sys.stdout.isatty()
        if args.tui:
            return lancer_tui(list(argv) if argv is not None else sys.argv[1:])
        if args.web or interactif:
            return lancer_web(list(argv) if argv is not None else sys.argv[1:], args.port)
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
            elif args.mine:
                from donjon.mine import nouveau_mine
                m = nouveau_mine(args.seed)
            elif args.crue:
                from donjon.crue import nouvelle_crue
                m = nouvelle_crue(args.seed)
            elif args.atelier:
                from donjon.atelier import nouveau_atelier
                m = nouveau_atelier(args.seed)
            elif args.auberge:
                from donjon.auberge import nouveau_auberge
                m = nouveau_auberge(args.seed)
            else:
                m = nouveau_monde(args.seed)
        if args.cases or args.defi or args.mine or args.auberge or args.crue or m.data.get("mode_cases"):
            from donjon.spatial import installer as installer_cases
            installer_cases(m)
        moteur = Moteur(m)
        connexion = args.connexion
        if connexion == "auto" and not args.offline:
            connexion = "chatgpt" if Coffre().compte() else "api"
        if connexion == "anthropic" and args.model == MODELE_PAR_DEFAUT:
            args.model = MODELE_CLAUDE  # essai de Claude : jamais choisi par défaut
        cle = "ANTHROPIC_API_KEY" if connexion == "anthropic" else "OPENAI_API_KEY"
        actif = not args.offline and (connexion == "chatgpt" or bool(os.environ.get(cle)))
        mj = MJOpenAI(args.model, args.effort, connexion=connexion) if actif else None
        if mj:
            mj.reflexion = args.reflexion
        from donjon import stratege
        # Le stratège passe par la connexion du MJ principal, jamais par le modèle comparé.
        stratege.activer(mj._appeler_brut if mj and args.stratege else None)
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
                imprimer("Les phrases libres utilisent " + ("votre forfait ChatGPT et ses limites." if connexion == "chatgpt" else
                                                      "la clé API Anthropic, à titre d'essai." if connexion == "anthropic" else
                                                      "la clé API OpenAI, avec une facturation séparée."))
        imprimer(m.data["scenario"]["objectif"] + " « aide » : commandes disponibles.")
        if not m.data["journal"]:
            imprimer(m.data["scenario"]["debut"])
        if interface is None:
            afficher("carte")
            afficher("scene")
            afficher("fiche")
        pending = None
        comparaison_pending = 0

        def demande_initiale(intention):
            # « tenter » confirme la dernière proposition : son récit part de la demande d'origine.
            if normaliser(intention) != "tenter":
                return intention
            return next((e["joueur"] for e in reversed(m.data["conversation"])
                         if e.get("nature") == "proposition_non_executee"), intention)

        def raconter(affichage, intention, gestes):
            """Récit de Luna d'un résultat déjà appliqué et sauvegardé ; le moteur reste le repli."""
            if mj is None or args.recit_moteur:
                return None
            try:
                recit = mj.raconter_resultat(m, {"intention": demande_initiale(intention), "gestes": gestes,
                                                 "faits": affichage.splitlines()})
            except ErreurMonde:
                return None
            if (recit.get("mode") != "dialogue" or not recit.get("_audit")
                    or chiffres_sans_fondement(recit["texte"], affichage, m.joueur)):
                return None
            return recit

        def conclure(plan, resultat, intention, numero=0):
            # Le moteur a déjà produit les conséquences ; son journal garde le détail du jet.
            affichage = rendre_resultat(resultat)
            m.sauver(args.save)
            recit = raconter(affichage, intention, gestes_accomplis(plan, m))
            texte_affiche = recit["texte"] if recit else affichage
            m.memoriser(intention, texte_affiche, "resultat_moteur")
            if recit:
                consigner_narration(m, recit)
            m.sauver(args.save)
            if isinstance(mj, Comparateur) and numero:
                mj.noter_resultat(resultat, numero=numero)
            imprimer(texte_affiche)

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
                    fermer = getattr(mj, "fermer", None)
                    if fermer:
                        fermer()
                    principal = MJOpenAI(args.model, args.effort, connexion="chatgpt")
                    stratege.activer(principal._appeler_brut if args.stratege else None)
                    mj = comparer(principal)
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
                # Hors --debug, la phrase reste une saisie ordinaire (« esprit, es-tu là ? »).
                if args.debug and cmd.startswith("esprit "):
                    nom = normaliser(cmd[7:])
                    id = next((i for i, o in m.objets.items() if o["type"] == "personnage"
                               and nom in [i, normaliser(o["nom"]), *map(normaliser, o.get("aliases", []))]), None)
                    if id is None:
                        imprimer("Aucun personnage de ce nom.")
                    else:
                        from donjon.esprits import esprit
                        imprimer(json.dumps(esprit(m, id), ensure_ascii=False, indent=2))
                    continue
                force_mj = cmd.startswith("mj ")
                # Héler par son nom, ou répondre à qui vient de héler Corvus, n'est pas une question au MJ,
                # même avec « ? » (« je crie « Gorm ? » », « « Oui ? » »).
                question = est_question(texte) and not cri(m, texte)
                try:
                    p = None if force_mj or question else analyser(m, texte)
                except ErreurMonde:
                    if mj is None:
                        raise
                    # Une intention libre peut dépasser la syntaxe locale.
                    p = None
                if mj is not None and p and p["action"] == "parler":
                    p = None
                if (mj is not None and p and p["action"] == "examiner"
                        and m.objets.get(p["cible"], {}).get("type") == "personnage"
                        and not m.objets[p["cible"]].get("portrait")
                        and not m.objets[p["cible"]].get("facettes")):
                    p = None
                if mj is not None and p is not None:
                    try:
                        Moteur(m).preparer(p)
                    except QualificationRequise:
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
                    transactions = reponse.get("_transactions", [])
                    if reponse["mode"] == "dialogue":
                        travail, rapports = appliquer_transactions(m, transactions)
                        suite = (Moteur(travail).preparer(pending.proposition, pending.origine)
                                 if pending and transactions else pending)
                        types = [t["type"] for t in transactions]
                        nature = ("conversation_pnj" if "conversation_pnj" in types else
                                  "parole_joueur" if "parole" in types else
                                  "refus_avant_action" if reponse.get("_validation_refusee") else "dialogue")
                        prefixe = reponse.get("_prefixe_moteur")
                        travail.memoriser(texte, "\n".join(filter(None, (prefixe, reponse["texte"]))), nature)
                        consigner_narration(travail, reponse)
                        # Ne montrer la nouvelle fiction qu'après sa sauvegarde réussie.
                        travail.sauver(args.save)
                        m.data, pending = travail.data, suite
                        if prefixe:
                            imprimer(prefixe)
                        imprimer(reponse["texte"])
                        if isinstance(mj, Comparateur):
                            for t, rapport in zip(transactions, rapports):
                                if t["type"] == "conversation_pnj":
                                    mj.noter_resultat(reponse["texte"], rapport)
                                elif t["type"] == "savoirs":
                                    mj.noter_savoirs(reponse["texte"], t["proposition"])
                        continue
                    p = reponse["proposition"]
                    if transactions:
                        travail, _ = appliquer_transactions(m, transactions)
                        travail.sauver(args.save)
                        m.data = travail.data
                    pending = None
                    if p.get("action") in ("clarifier", "impossible"):
                        raise ErreurMonde("L'avis du MJ doit être contrôlé comme un dialogue avant affichage.")
                    pending = moteur.preparer(p, origine="reprise mémorisée" if reponse.get("_reprise_locale") else "LLM : " + mj.modele)
                    comparaison_pending = mj.numero if isinstance(mj, Comparateur) else 0
                    # Une question sur un geste (« puis-je… ? ») le prépare sans l'exécuter : seule une
                    # perception répond tout de suite.
                    essai_a_blanc = question and p.get("action") not in PERCEPTIONS
                    if not essai_a_blanc and not pending.stat and not pending.echec_critique:
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
                    suite_fiche = "" if pending.etapes else "« tenter » pour agir ; « annuler » pour abandonner."
                    if essai_a_blanc or suite_fiche:
                        imprimer(" ".join(filter(None, ("Rien n'est encore tenté." if essai_a_blanc else "",
                                                        suite_fiche))))
                else:
                    if p["action"] != "observer":
                        pending = None
                    plan = moteur.preparer(p)
                    resultat = moteur.executer(plan)
                    mouvement = m.data.get("mode_cases") and p["action"] in ("marcher", "aller")
                    if not mouvement:
                        m.memoriser(texte, resultat, "resultat_moteur")
                    m.sauver(args.save)
                    if not mouvement or interface is None:
                        imprimer(resultat)
                    else:
                        evenements = [ligne for ligne in resultat.splitlines() if ligne != "Tu avances d'un pas."]
                        if evenements:
                            imprimer("\n".join(evenements))
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
        fermer = getattr(mj, "fermer", None)
        if fermer:
            fermer()


if __name__ == "__main__":
    raise SystemExit(main())
