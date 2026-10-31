# Tâche Codex 421 : G12, la portée d'une création interactive

Lot de la refonte du MJ (`docs/plan-refonte-mj.md`, ligne G12 ; `docs/conception-valeur-llm.md`, « G12 portée d'une création »), débloqué par la forme A complète du compilateur (A0 à A6, fusionnés ; dernier : lot 416). Quand le joueur veut agir sur un détail inventé (un élément d'ambiance, une pierre, une fissure), Luna peut proposer de le créer.

Lis `AGENTS.md` (contrat du MJ, « Interactif » et « Ambiance »), `docs/etat-dev.md` (court), la ligne G12 du plan, la section correspondante de `docs/conception-valeur-llm.md` et le rapport 416. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
**Un ajout interactif proposé par Luna n'est admis que s'il ne remplace ni une perception (ce que Corvus voit, entend ou touche) ni un indice protégé (un objet caché, une trace, une information de quête). Admis, il existe dans l'état avant toute manipulation, persiste après recharge, et l'intention du joueur reprend dessus. Il ne porte aucun engagement, effet ou capacité cosmétique.** Un faux indice ou une perception remplacée est refusé avec `attendu`, sans exception de scénario.

Cas : un ajout utile (une pierre détachée qu'on ramasse), un faux indice refusé (une empreinte qui désignerait le coupable), une perception remplacée refusée (« il n'y a rien derrière la porte » inventé), recharge.

**Luna : une passe ciblée**, sur copies : `atelier`, `relais`, `luna-restes-ambiance` et `materiaux`. Mesure les appels par tour jusqu'à la manipulation. Si la revue automatique bloque la passe, laisse la commande exacte dans les bruts.

## Contraintes
**Poste : le laptop.** Fichiers attendus : `donjon/mj.py`, `donjon/faits_locaux.py`, `donjon/portee_narrative.py`, tests. Lots en cours : 402 (vérification d'intégration, calcul seul), 419 (vérification de contact), 420 (S1n). Pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite, calculs longs détachés : vérifie qu'ils vivent avant de rendre la main ; une suite complète tourne aussi sur ce poste. La poussée de ta branche vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) est autorisée.

## Vérification
Les méthodes ciblées vertes sans changer leurs assertions de sécurité (une adaptation seulement si le changement est
voulu et documenté, preuve citée) ; le cas réel et un autre de même nature après recharge et laps découpé ; tests
voisins verts. Empreintes 2 h, quatre graines, scénarios touchés et Relais, si le code du jeu change. Pas de suite
complète (le superviseur la relance), ni Luna hors de la passe demandée ci-dessus.

## Livraison
Branche `codex-g12-portee-creation`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ;
poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-421-g12-portee-creation.md` ; entrée « non fusionnée » de
8 lignes au plus dans `docs/etat-dev.md` (puce commençant par « - » qui nomme la branche entre accents graves). Bruts
dans `C:\Users\msics\donjon\artifacts\g12-portee-creation-421\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
