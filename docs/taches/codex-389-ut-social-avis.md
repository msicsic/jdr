# Tâche Codex 389 : U-T social avis, le terminal conserve l'avis structuré

Lot d'interface de la refonte du MJ (`docs/plan-refonte-mj.md`, ligne U-T social avis), après U-M social avis (lot 386, formulaire web, fusionné) et U-T social information (lot 369, fusionné), dont tu reprends la structure (rapport 369, et le correctif de prémisses 387 : une scène de test déclare explicitement ce que Corvus connaît).

Lis `AGENTS.md`, `docs/etat-dev.md` (court) et les documents cités. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
**La console et la TUI soumettent au moteur exactement le même avis structuré que le formulaire web du 386 (lieu public connu de Corvus, menace oui ou non), par le même descripteur U-D, sans réinterprétation ni appel au modèle ; réception et dispute identiques à la parole typée (G18).** Parité web/console/TUI sur deux lieux et un avis contraire, touches et réponse, recharge.

Luna : aucune passe (aucun chemin du modèle).

## Contraintes
**Poste : le laptop.** Fichiers attendus : `donjon/jeu.py`, `donjon/tui.py`, `donjon/paroles.py` seulement si un paramètre public manque, tests. Lots en cours : 374 (position crue), 375 (rouges de la suite), 380 (U-M social comptes, web), 381 (A2 passage) ; pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite, calculs longs détachés. La poussée de ta branche vers origin est autorisée par l'utilisateur.

## Vérification
Les méthodes ciblées vertes sans changer leurs assertions de sécurité (une adaptation seulement si le changement est
voulu et documenté, preuve citée) ; le cas réel et un autre de même nature après recharge et laps découpé ; tests
voisins verts. Empreintes 2 h, quatre graines, scénarios touchés et Relais, si le code du jeu change. Pas de suite
complète (le superviseur la relance), ni Luna.

## Livraison
Branche `codex-ut-social-avis`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ;
poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-389-ut-social-avis.md` ; entrée « non fusionnée » de
8 lignes au plus dans `docs/etat-dev.md` (puce commençant par « - » qui nomme la branche entre accents graves). Bruts
dans `C:\Users\msics\donjon\artifacts\ut-social-avis-389\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
