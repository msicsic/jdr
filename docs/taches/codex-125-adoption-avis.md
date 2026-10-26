# Tâche Codex 125 (diagnostic) : pourquoi aucun avis n'est adopté

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). **Diagnostic seul** : aucun code du jeu modifié, sauf un outil
de mesure sous `tools/` si nécessaire. Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste : au plus 2 processus de calcul,
priorité réduite. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-relations.md` (§ 7.3 : formation et poids des sources, § 7.4), les rapports des lots 80, 88 et 121,
puis `donjon/esprits.py` (`poids_source`, `prevision`, `recevoir_prevision`), `donjon/social.py` (avis de menace, réception),
`donjon/eau.py` (`estimation`, `attendue`, `menacee`).

## Constat
Depuis les lots 80 et 88, les PNJ de la crue se disent leurs avis de menace d'eau : **18 avis en 4 h** (crue × quatre
graines), **16 et 6** sur les nuits de 12 h 500 et 2024, et **zéro adoption** partout. Le lot 121 n'a vu aucune dispute
naturelle. Soit c'est voulu (chacun voit lui-même l'eau et ce qu'il voit pèse plus que ce qu'il entend, § 7.3), soit un
défaut (avis dit à qui sait déjà la même chose, poids mal calculés, conviction du locuteur écrasée, avis dit trop tard…).

## Ce qu'il faut établir (sans corriger)
- Pour chaque avis dit dans ces nuits (crue 4 h × 1985/7/42/2024, puis 12 h × 500/2024) : locuteur, auditeur, lieu, valeur,
  prévision propre de l'auditeur à cet instant (source, minute, conviction), poids comparés, issue (`doute`, rejet, sans
  objet parce que même valeur) ; classe chaque cas : **même avis déjà tenu**, **constat propre plus récent et plus fort**,
  **poids inférieur malgré l'absence de constat**, autre.
- Si des cas « poids inférieur sans constat » existent : la formule du § 7.3 est-elle appliquée telle quelle (0,7 × confiance
  × (1 + affection/200) × conviction) ? Les convictions transmises sont-elles plausibles ?
- Pourquoi aucune dispute : contradicteur absent, conviction pas assez forte, auditeur ne saisit pas les mots ?
- Si un défaut du contrat commun apparaît, propose l'invariant et le correctif (fonctions, effet attendu), **sans le coder** ;
  si le comportement est voulu, dis-le et propose ce qu'il faudrait au scénario (données) pour qu'un avis serve un jour.

## Vérification
Deux captures rechargées où un avis est dit, avec la décision de l'auditeur reproduite à l'identique ; empreintes des nuits
inchangées par l'instrumentation (l'outil observe sans modifier). Pas de suite complète si aucun code du jeu n'est touché.

## Livraison
Branche `codex-adoption-avis` poussée (pas `main`), commits signés si une clé est configurée sur ce poste. Rapport d'une page :
`docs/taches/rapport-codex-125-adoption-avis.md`, et une entrée dans `docs/etat-dev.md` (« Branche `codex-adoption-avis`,
diagnostic, non fusionnée »).
