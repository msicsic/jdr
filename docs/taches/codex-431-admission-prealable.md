# Tâche Codex 431 : admettre la création préalable d'un geste sans la juger comme une recherche

Correction proposée par le diagnostic 430 (`docs/taches/rapport-codex-430-creation-utile-luna.md`, fusionné ; bruts
`C:\Users\msics\donjon\artifacts\creation-utile-430\`, PC fixe, avec `preuves.md`, `refus.json` et les 13 dossiers de
portée rejouables sans modèle). Avec Luna, aucune création ou qualification utile n'aboutit (lots 421, 422, 423, 427).
La revue de portée (`portee_narrative`, `usages`) juge globalement demande et ajout : la matérialisation ou la
qualification qui précède un geste (« je ramasse la pierre mouillée », « elle mesure combien, la torche ? ») devient une
« recherche implicite » (`perception_requise`). Les descriptions arrivent vides, sans dossier des champs à établir, et
les cardinalités du rapport ne sont pas fixées à l'entrée, d'où des rapports illisibles.

Lis `AGENTS.md` (contrat du MJ, « Interactif »), `docs/etat-dev.md` (court), le rapport 430 et les rapports 421, 422, 427.

## Invariant (un seul)
**Quand une proposition porte une création ou une qualification interactive suivie d'un geste (`suite`), la revue de
portée juge cette mutation comme le préalable du geste : elle reçoit un dossier dérivé de la mutation autorisée
(propriétés établies, propriétés manquantes à établir, suite non encore exécutée), avec des cardinalités fixées à
l'entrée (un jugement par ajout, une description par propriété à établir), et elle ne contrôle que les affirmations
qui dépassent cette mutation. Elle n'exige pas la propriété nouvelle comme preuve préalable.** Budgets, physique (masse,
capacités), fidélité, consentement et refus d'indice restent inchangés. Aucune exception d'objet ni consigne nouvelle à
Luna.

Fonctions visées par le diagnostic : `portee_narrative` (`contexte_admission`, schéma, `controler_usages`) et
`mj._appeler` / `_echanger_prepare`.

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : `donjon/portee_narrative.py` (ou son équivalent), `donjon/mj.py`, tests.
Lots en cours : 402 (calcul), 419, 429 (K1, laptop), 432 (refus du rendu sans `attendu`, `rendu.py` / `narration.py`).
Pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite.

## Vérification
Rejoue d'abord les 13 dossiers du 430 sans modèle : les faux refus (torche, planches qualifiées, pierre mouillée, éclat
de bois) passent, les refus justes (masse incompatible, odeur, rapport réellement incohérent) restent. Puis vraie boucle
avec MJ simulé : pierre/éclat et torche/planches, geste fait sans ressaisie, état et rendu après recharge ; contre-épreuves
indice, absence inventée, capacité non déclarée, masse incompatible, odeur. **Luna : une passe ciblée** sur copies (les
scripts des lots 422, 423 et 427 qui exercent ces cas) ; si la revue automatique la bloque ou si le coffre est illisible,
laisse la commande exacte dans les bruts. Pas de suite complète.

## Livraison
Branche `codex-admission-prealable`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt
de l'utilisateur ; poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-431-admission-prealable.md` ;
entrée « non fusionnée » de 8 lignes au plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents
graves). Bruts dans `C:\Users\msics\donjon\artifacts\admission-prealable-431\`. Termine par `LOT TERMINÉ`,
`CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
