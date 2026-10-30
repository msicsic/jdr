# Tâche Codex 323 : G5, la perception canonique rendue par le moteur

Lot G5 de la [feuille de route de la refonte du MJ](../plan-refonte-mj.md). Lis `AGENTS.md` (contrat du MJ, « Mécanique »),
`docs/conception-refonte-mj.md` (table des faits mécaniques, ligne « Présence et non-perception », et ligne G5) et
`docs/conception-valeur-llm.md` (ligne G5). G5 se fait **sur la voie actuelle**, sans attendre le compilateur G1
(conception 318, section 6 : les portages G5/G15–G19 se découpent sur leurs voies existantes).

## L'invariant
**Une réponse de perception (examiner, regarder, écouter, observer, fouiller sans trouvaille) est rendue par le moteur, à
partir des seules données perceptibles ou connues de Corvus, et distingue quatre états qui ne se confondent jamais :
présent et vu, présent mais non perçu (noir, dos, couverture partielle), absent constaté, souvenir d'une position
passée.** Le texte est enregistré avant affichage ; aucun appel de récit, d'audit ni de révision pour une réponse de
perception que le moteur sait rendre. Hors de vue n'est pas une absence ; une dernière position n'est pas une présence.
Réutilise les sources existantes (`pnj.suivre_presences`, `pnj.bilan_presences`, `rendu.regarder`,
`perception.non_vus_connus`, attestations de non-perception, couverture du lot 102) : aucune liste parallèle.

Ce qui ne change pas : une perception qui demande un détail que le moteur ne connaît pas garde la voie actuelle
d'admission (G12/G13 plus tard) ; aucune ambiance retirée (G8) ; aucun contrôle des autres voies retiré.

## Vérification
- Tests ciblés : `signes-guet`, `signes-noir` (personne présente non perçue), un absent constaté à l'auberge, un souvenir
  de position passée ; texte sauvegardé, monde, scène et carte identiques après recharge ; zéro appel au modèle sur ces
  réponses (MJ simulé qui échoue s'il est appelé).
- Luna : **une passe** de `signes-guet`, `signes-noir`, `luna-restes-ambiance`, `atelier`, référence lue du cache. Si la
  revue automatique bloque Luna, laisse la commande exacte dans `C:\Users\msics\donjon\artifacts\g5-323\luna-a-jouer.txt`.
- Pas de suite complète ni de banc PNJ (aucune décision des PNJ ne doit changer : si un fichier de décision change,
  empreintes 2 h Relais et auberge, 4 graines, contre l'intégration en cache).

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite. Recouvrements possibles : lot 320 (G15, `narration.py`,
`paroles.py`) et lot 319 (U-P, `rendu.py`, `jeu.py`) ; signale-les dans le rapport, sans les éviter au prix de l'invariant.

## Livraison
- Branche `codex-g5-perception`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur : la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-323-g5-perception.md`, entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\g5-323\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
