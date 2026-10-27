# Tâche Codex 172 (force 4f, restes) : la contre-revue admet les pas inhérents à traîner et la porte d'enfermer

Petit lot issu des vérifications Luna `cdaf371` et `227c496` (lots 153, 157, 165 : traîner 4/3 appels, enfermer 6/1, critère des
trois appels non atteint). Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le laptop** (`C:\Users\msics\donjon`, Luna connectée ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, copies seulement : cadre normal, `AGENTS.md`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot tourne sur ce poste (173, destinations de dépôt) : au plus
2 processus de calcul, Luna en 2 exécutions au plus, priorité réduite. Ce lot touche la contre-revue d'action
(`couverture_action.py`), les titres et informations de plan de `tenir.py`, et les lignes de force de `consignes.py`, avec leurs
tests ; **pas** `operations.py`/`deplacement_objet.py` (lot 173), `narration.py`, `mj.py`. **Bruts dans
`C:\Users\msics\donjon\artifacts\force-172\`, jamais dans le worktree.** Si une revue automatique bloque Luna ou la poussée, termine
le reste, commite localement et écris la commande exacte dans `C:\Users\msics\donjon\artifacts\force-172\luna-a-jouer.txt`. Termine
ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/contrat-mj.md`, les rapports des lots 147, 157 et 165 (section force) et leurs fils (`force-4f-trainer`,
`force-4f-enfermer` dans `C:\Users\msics\donjon\artifacts\verif-luna-227c496\`), puis la contre-revue d'action et `tenir.preparer`.

## Les cas (lot 165)
- **Traîner** : la contre-revue rejette le pas du joueur (vers le sud) qui fait partie du geste de traîner (le corps suit
  Corvus), puis un faux refus de portée ; aucun déplacement.
- **Enfermer** : p1 exige d'amener Bram dans le bureau où il est déjà ; p2 veut le manipuler, l'approche est refusée ; aucune
  fermeture.

## L'invariant
**Ce que reçoit la contre-revue d'un geste composé dit les effets que le moteur établit pour chacun de ses pas (traîner : Corvus
et le corps avancent ensemble d'une case ; enfermer : la porte se ferme et se verrouille, la personne est déjà de l'autre côté),
de sorte qu'un pas inhérent au geste demandé n'est pas jugé ajouté ; et la consigne d'enfermer dit qu'on verrouille la porte
derrière la personne, sans la déplacer.** Même voie que les lots 154 et 157 (titre, information et dossier communs) ; aucune
consigne d'audit ou règle propre à Bram, à Brune ou à une salle.

## Vérification
- Tests MJ simulé/console après rechargement : dossier de contre-revue de traîner (pas commun de Corvus et du corps) et
  d'enfermer (porte, personne déjà derrière), plans conformes admis ; un plan réellement non conforme toujours rejeté.
- Luna, **deux passes** de `force-4f-trainer`, `force-4f-enfermer` ; une passe des neuf autres bancs de force ; critère : trois
  appels au plus par saisie, aucun état corporel inventé.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-force-contre-revue` poussée (pas `main`).
`docs/plan-force.md` (4f), `docs/etat-dev.md` (« Branche `codex-force-contre-revue`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-172-force-contre-revue.md`.
