# Tâche Codex 108 : un avertissement n'est pas redit à qui le sait déjà, sans fait nouveau

Petit lot (`AGENTS.md`, « Rythme des lots »). Pas de Luna. Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. **Un seul
poste** : priorité réduite, au plus 2 processus de calcul ; le lot 105 (`planification`) et le lot 107 (`echanges`,
`propositions`, `pnj_propositions`) tournent en même temps : ce lot reste dans `social.py` / `esprits.py` (nouvelles, avis,
registre `faits_dits`). Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

## Le constat (persistant, vérifications 5c2ce81 et 47d4d25, lot 103)
- Crue 2024 : Brune avertit Gorm de la torche éteinte à **146, 242 et 444 min** ; six redites au total sur la vérification
  47d4d25, espacées d'au moins 96 min (`docs/taches/rapport-codex-94-verif-integ.md`).
- Mine : avis textuels redits **3 → 7** dans le banc du lot 103 (Josse, minutes 76 et 79 en graine 2024 ; 76 et 78 en graine 7),
  `docs/taches/rapport-codex-103-boucle-garde-manger.md`.
Bruts : `C:\Users\msics\donjon\artifacts\verif-integ-47d4d25\`. Le lot 64 (`esprit.faits_dits`, registre des identités, valeurs
et destinataires) devait empêcher la redite d'une même valeur ; le lot 80/88 a ajouté les avis de menace.

## D'abord, établir la cause
Pour chaque redite réelle : la valeur dite est-elle la même (même fait, même état) ? Le destinataire le sait-il encore (souvenir,
croyance) ? Quel chemin la redit : nouvelles communes, avis de menace (lots 80/88), constats partagés (lot 55), un autre ? Le
registre `faits_dits` a-t-il été contourné, saturé, ou la valeur a-t-elle changé puis est revenue (éteinte → allumée → éteinte) ?

## L'invariant
**On ne redit pas à quelqu'un ce qu'il sait déjà, tant que rien de nouveau n'est arrivé à ce fait** : un fait revenu à une valeur
déjà dite n'est nouveau que si le destinataire a pu croire autre chose entre-temps (il l'a vu changer, on le lui a dit) ; tous les
chemins de parole des PNJ passent par la même règle (`social.faits_dits`, `_a_dire`). Corrige le chemin qui y échappe, pas un
personnage ni un texte.

## Vérification
- Tests après rechargement, même laps découpé : les deux cas réels (capture crue 2024 vers 140 min, capture mine 2024 vers 70 min)
  sans redite ; un fait réellement changé puis redit (le destinataire l'avait cru autrement) toujours dit.
- Banc rapide 4 h, quatre scénarios × quatre graines contre la base (cache, sinon calculée une fois et rangée) : avertissements
  redits, constats confiés, aucune usurpation.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-ouie.md` (« Ce qu'on a déjà dit ») si la règle change,
`docs/etat-dev.md` (« Branche `codex-avis-redits`, non fusionnée »). Rapport d'une demi-page :
`docs/taches/rapport-codex-108-avis-redits.md`.
