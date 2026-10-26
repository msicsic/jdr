# Tâche Codex 103 : la boucle de Mathe au garde-manger (mine 3)

Petit lot de correction (`AGENTS.md`, « Rythme des lots »). Pas de Luna. Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`.
**Un seul poste** : priorité réduite, au plus 2 processus de calcul ; le lot 98 b (coût exact : `trajet_estime`, `spatial`, routes
et tarifs de `planification`) et le lot 102 (MJ) tournent en même temps : ne touche ni aux routes, ni à `trajet_estime`, ni à
`spatial`. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

## Le constat (vérification d'intégration du lot 94)
Mine, graine 3, 12 h : **Mathe**, dès 9–10 min, déverrouille, ouvre, ferme et verrouille le garde-manger en boucle :
**328 / 291 / 291 / 328** occurrences sur la nuit ; aucune telle rafale dans les références (`42bb9c0`, `5c2ce81`). Relevés :
garde à 10–15, service de Lucien à 20–25. Bruts : `C:\Users\msics\donjon\artifacts\verif-integ-47d4d25\` (audit 12 h, mine 3 ;
`bilan.txt`, `evidence.json`) et le rapport `docs/taches/rapport-codex-94-verif-integ.md`. Les bascules entre acteurs ne
détectent pas cette boucle d'un seul personnage. Le lot `boucles-pnj` (N1 : un geste défait sous ses yeux, `deliberation.changer_etat`,
`contrarie`) traitait la boucle à deux acteurs.

## D'abord, établir la cause
Reproduis sur une capture (mine 3, avant 9 min, puis rejouée minute par minute, même laps découpé et rechargé) et dis quel couple
de buts ou de gestes s'alterne (garde du garde-manger et service de Lucien, fermeture après soi, `donne`/`DEFAIT`, recours en
cours…) et quel lot l'a introduit (bissection courte si nécessaire, sur les fusions depuis `5c2ce81`).

## L'invariant
**Un PNJ ne défait pas lui-même, sans fait nouveau, l'état qu'il vient de produire pour un autre de ses buts** : la protection
d'un bien (fermer, verrouiller) et les préconditions d'un geste qu'il fera ensuite (ouvrir pour servir) restent compatibles ; le
plan qui ouvre pour servir porte la refermeture à sa fin, et la garde ne referme pas ce qu'un plan en cours a ouvert. Corrige la
règle commune (choix, effet terminal du plan, ce que la garde lit), pas Mathe, la mine ni le garde-manger ; pas de délai fixe.

## Vérification
- Tests après rechargement, même laps découpé : le cas réel (Mathe, mine 3) sans boucle ; un autre cas de même nature (un
  gardien qui sert depuis une réserve qu'il garde, à l'auberge ou au Relais) ; la garde ordinaire (refermer après un tiers)
  inchangée.
- Banc rapide 4 h, quatre scénarios × quatre graines contre la base (cache) ; audit 12 h de la mine 3 : la rafale disparaît,
  aucune boucle nouvelle, aucune usurpation.
- `VERIFIER` + `spatial.VERIFICATION=1`, mine 3, 2 h ; suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-planificateur.md` si une règle change, `docs/etat-dev.md` (« Branche
`codex-boucle-garde-manger`, non fusionnée »). Rapport d'une demi-page : `docs/taches/rapport-codex-103-boucle-garde-manger.md`.
