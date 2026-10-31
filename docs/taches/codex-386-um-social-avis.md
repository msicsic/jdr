# Tâche Codex 386 : U-M social avis, le choix d'avis conserve sujet et valeur

Lot d'interface de la refonte du MJ (`docs/plan-refonte-mj.md`, ligne U-M social avis), après G18 (avis formulé par le moteur, lot 351), U-D, U-C et les menus U-M information (354) et comptes (380, en cours), dont tu reprends la structure (rapport 354).

Lis `AGENTS.md`, `docs/etat-dev.md` (court) et les documents cités. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
**Le formulaire d'avis du menu web (prévenir d'une menace sur un lieu, ou dire qu'il n'y en a pas) soumet au moteur exactement le sujet et la valeur choisis, sans réinterprétation ni compilation par le modèle ; il ne propose que des lieux publics connus de Corvus.** Même réception et même dispute que la parole typée équivalente (G18). Cas : deux lieux, un avis contraire ; zéro appel au modèle ; recharge.

Luna : aucune passe (aucun chemin du modèle).

## Contraintes
**Poste : le laptop.** Fichiers attendus : `donjon/web/page.html`, `donjon/web/pont.py`, `donjon/paroles.py` seulement si un paramètre public manque, descripteur U-D ; pas `jeu.py`/`tui.py` (U-T viendra ensuite). Le lot 380 (U-M social comptes) touche aussi `web/page.html` : avant de livrer, fusionne `origin/integration` dans ta branche et résous un éventuel conflit en gardant les deux formulaires. Pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite, calculs longs détachés. La poussée de ta branche vers origin est autorisée par l'utilisateur.

## Vérification
Les méthodes ciblées vertes sans changer leurs assertions de sécurité (une adaptation seulement si le changement est
voulu et documenté, preuve citée) ; le cas réel et un autre de même nature après recharge et laps découpé ; tests
voisins verts. Empreintes 2 h, quatre graines, scénarios touchés et Relais, si le code du jeu change. Pas de suite
complète (le superviseur la relance), ni Luna.

## Livraison
Branche `codex-um-social-avis`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ;
poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-386-um-social-avis.md` ; entrée « non fusionnée » de
8 lignes au plus dans `docs/etat-dev.md` (puce commençant par « - » qui nomme la branche entre accents graves). Bruts
dans `C:\Users\msics\donjon\artifacts\um-social-avis-386\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
