# Tâche Codex 399 : rembourser une dette en pièces depuis le menu et le terminal

Suite d'interface du lot 388 (remboursement volontaire d'une dette en pièces, mécanique décidée par l'utilisateur le 2026-10-31, fusionné). Les raccourcis de comptes du menu web (lot 380) et la commande `comptes` du terminal (lot 396) ne proposent pas encore ce remboursement ; seuls la saisie libre et la parole typée y mènent.

Lis `AGENTS.md`, `docs/etat-dev.md` (court) et les rapports 380, 388 et 396. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
**Pour chaque dette en pièces que Corvus croit devoir (comptes publics, `biens.comptes_joueur`), le menu web et le terminal proposent « rembourser » avec le montant dû par défaut et un montant partiel possible ; le choix soumet au moteur exactement l'acte du 388, par le même descripteur U-D et le consentement U-C, sans appel au modèle.** Refus distincts (montant trop fort, créancier absent, bourse insuffisante) avec leurs messages, parité web/console/TUI, recharge : dette soldée ou réduite, bourses justes.

Luna : aucune passe (aucun chemin du modèle).

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : `donjon/web/page.html`, `donjon/web/pont.py`, `donjon/dialogues.py`, `donjon/comptes_terminal.py`, `jeu.py`, `donjon/tui.py`, tests. Lots en cours : 381 (A2 passage, `commandes.py`/`paroles.py`), 397 (S1f) ; pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite, calculs longs détachés : vérifie qu'ils vivent avant de rendre la main. La poussée de ta branche vers origin est autorisée par l'utilisateur.

## Vérification
Les méthodes ciblées vertes sans changer leurs assertions de sécurité (une adaptation seulement si le changement est
voulu et documenté, preuve citée) ; le cas réel et un autre de même nature après recharge et laps découpé ; tests
voisins verts. Empreintes 2 h, quatre graines, scénarios touchés et Relais, si le code du jeu change. Pas de suite
complète (le superviseur la relance), ni Luna.

## Livraison
Branche `codex-rembourser-public`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ;
poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-399-rembourser-public.md` ; entrée « non fusionnée » de
8 lignes au plus dans `docs/etat-dev.md` (puce commençant par « - » qui nomme la branche entre accents graves). Bruts
dans `C:\Users\msics\donjon\artifacts\rembourser-public-399\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
