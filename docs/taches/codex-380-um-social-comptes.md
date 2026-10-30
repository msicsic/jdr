# Tâche Codex 380 : U-M social comptes : les raccourcis de comptes soumettent les termes visibles

Lot d'interface de la refonte du MJ (`docs/plan-refonte-mj.md`, ligne U-M social comptes), après U-D, U-C, G17 (comptes parlés) et les menus U-M (344, 349, 354) et E5 (choix direct d'un accord daté, lot 359), fusionnés. Reprends la structure des rapports 354 et 359.

Lis `AGENTS.md`, `docs/etat-dev.md` (court) et les documents cités. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
**Les raccourcis sociaux de comptes au menu web (réclamer un dû, rembourser, payer un prix convenu, demander ce que l'autre doit) soumettent au moteur exactement les termes affichés (montants, objets, débiteur, créancier), sans accord anticipé : le transfert n'a lieu qu'après l'accord ou le verdict du moteur, et le consentement U-C pour un acte lourd ; le formulaire ne reçoit que les comptes publics de Corvus (`biens.comptes_joueur`), jamais ceux d'autrui.** Parité avec la saisie typée, zéro appel au modèle, recharge.

Luna : aucune passe (aucun chemin du modèle).

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : `donjon/web/page.html`, `donjon/web/pont.py`, `donjon/dialogues.py`, catalogue `donjon/gestes_publics.py` si un paramètre public manque ; pas `jeu.py`/`tui.py` (U-T viendra ensuite). Lots en cours : 374 (position crue), 375 (rouges de la suite), 378 (S1a, porte des épisodes, esprits.py) ; pendant S1, n'ajoute aucun registre d'esprit ; signale tout recouvrement. Deux processus au plus, priorité réduite, calculs longs détachés.

## Vérification
Les méthodes ciblées vertes sans changer leurs assertions de sécurité (une adaptation seulement si le changement est
voulu et documenté, preuve citée) ; le cas réel et un autre de même nature après recharge et laps découpé ; tests
voisins verts. Empreintes 2 h, quatre graines, scénarios touchés et Relais, si le code du jeu change. Pas de suite
complète (le superviseur la relance), ni Luna.

## Livraison
Branche `codex-um-social-comptes`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ;
poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-380-um-social-comptes.md` ; entrée « non fusionnée » de
8 lignes au plus dans `docs/etat-dev.md` (puce commençant par « - » qui nomme la branche entre accents graves). Bruts
dans `C:\Users\msics\donjon\artifacts\um-social-comptes-380\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
