# Tâche Codex 396 : U-T social comptes, le terminal garde les termes du raccourci comptable

Lot d'interface de la refonte du MJ (`docs/plan-refonte-mj.md`, ligne U-T social comptes), après U-M social comptes (lot 380, raccourcis web : réclamer, restituer un prêt, régler un échange convenu ; fusionné), le remboursement volontaire en pièces (lot 388, fusionné) et U-T social avis (389), dont tu reprends la structure (rapport 389). Le don et la restitution sont des actes lourds selon U-C (lot 394) : ils passent par « Compris » puis « tenter ».

Lis `AGENTS.md`, `docs/etat-dev.md` (court) et les documents cités. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
**La console et la TUI soumettent au moteur exactement les mêmes termes comptables que les raccourcis web du 380 (montants, objets, débiteur, créancier), par le même descripteur U-D, sans accord anticipé ni appel au modèle : transfert seulement après le verdict du moteur et le consentement U-C ; seuls les comptes publics de Corvus (`biens.comptes_joueur`) sont proposés.** Le remboursement en pièces du 388 y figure s'il est déjà exposé comme geste public ; sinon, signale-le sans l'ajouter. Parité web/console/TUI, refus distincts, recharge.

Luna : aucune passe (aucun chemin du modèle).

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : `jeu.py`, `donjon/tui.py`, `donjon/dialogues.py` seulement si un paramètre public manque, tests. Lots en cours : 374 (position crue), 381 (A2 passage), 392 (scènes connues), 395 (avis redits crue) ; pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite, calculs longs détachés : vérifie qu'ils vivent avant de rendre la main. La poussée de ta branche vers origin est autorisée par l'utilisateur.

## Vérification
Les méthodes ciblées vertes sans changer leurs assertions de sécurité (une adaptation seulement si le changement est
voulu et documenté, preuve citée) ; le cas réel et un autre de même nature après recharge et laps découpé ; tests
voisins verts. Empreintes 2 h, quatre graines, scénarios touchés et Relais, si le code du jeu change. Pas de suite
complète (le superviseur la relance), ni Luna.

## Livraison
Branche `codex-ut-social-comptes`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ;
poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-396-ut-social-comptes.md` ; entrée « non fusionnée » de
8 lignes au plus dans `docs/etat-dev.md` (puce commençant par « - » qui nomme la branche entre accents graves). Bruts
dans `C:\Users\msics\donjon\artifacts\ut-social-comptes-396\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
