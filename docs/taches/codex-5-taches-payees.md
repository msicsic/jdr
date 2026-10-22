# Tâche Codex 5 : ce qu'on vend ou accepte, on peut le servir soi-même

Branche `codex-taches-payees`, worktree dans `tmp-worktrees/`. Lis d'abord `AGENTS.md`,
`docs/etat-dev.md` (entrées `echanges-argent`, `echanges-suite`, `refus-retenus`, `temps-reel`,
`crochetage-surenchere`), `docs/plan-social.md` (« Argent, prêts et garde confiée », « Suite des
échanges », « La surenchère progressive et la tâche aussitôt due ») et
`docs/taches/rapport-cloud-lots-abc.md` (lot C).

## Les cas réels
1. **Aubin et le brasero** (Relais, graine 42, 8 h, départ tiré, `main` actuel ; vu par le lot A) :
   à la minute 151, Aubin vend à Gorm une part de planches pour le brasero. Il n'a pas de flamme pour
   le rallumer, et Gorm lui refuse la torche (« nécessaire »). Il ne sert pas la part et ne le dit
   pas ; Gorm attend 60 minutes, puis la part devient une dette remboursée. À la minute 334, Aubin
   accepte pour 16 pièces de rallumer le brasero et le doit aussitôt.
2. **Odile paie Tilo pour l'âtre** (auberge, scène `tilo_paye_pour_l_atre` de
   `tests/test_crochetage_surenchere.py`, **avec** la réserve d'Odile, `bois_reserve`) : Tilo n'a
   pas de flamme ; il accepte, parce que son seul moyen est de demander une part de bois à Odile, qui
   la met elle-même au feu et le rallume de son briquet. Le payeur fait la tâche qu'il paie.

## L'invariant à garantir (règle commune, pas de cas par objet ou par personnage)
- On ne vend une part, un objet ou une tâche, on n'accepte une demande qui engage à servir, que si
  l'on voit comment la servir soi-même, par le plan que l'on suivra pour la servir (même règle que
  le lot C pour les tâches : l'acceptation et l'exécution jugent sur le même devis). Pour une part de
  combustible destinée à un feu, servir comprend ce que la part exige (le mettre au feu et l'allumer
  s'il est éteint) ; si le vendeur ne le peut pas, à lui de proposer ce qu'il peut (remettre le bois à
  l'acheteur, si l'acheteur peut l'allumer) ou de refuser avec la cause juste (refus retenu selon sa
  cause, `deliberation.retenir_refus`).
- Le plan d'une tâche payée ne passe pas par le payeur pour accomplir ce qui est payé : il peut
  employer les biens du payeur (règle A3, `devis_pulsion(seul=…)`), pas lui faire faire le geste.
- Quand ce qu'on a promis devient impossible, on le dit (refus, dette ou rendu, selon ce qui existe
  déjà), sans laisser l'autre attendre sans nouvelle.

## Vérifications
- Tests après rechargement (`tests/test_taches_payees.py`) : les deux cas réels, et au moins un autre
  cas de même nature (par exemple : une part de bois demandée à quelqu'un qui n'a pas de flamme, à
  la mine ou à l'auberge ; une tâche payée dont le seul moyen passe par le payeur).
- Remets la scène de Tilo de `test_crochetage_surenchere` avec la réserve d'Odile si la règle rend
  le `sans(m, "bois_reserve")` inutile, et dis-le.
- Suite complète verte (en priorité réduite, ou par `tools/tests.py` s'il est fusionné) ;
  `planification.VERIFIER` sur une nuit de 8 h de chaque scénario.
- Banc rapide (4 h, 4 graines) Relais, auberge, crue, `main` puis la branche (`tools/comparer_bancs.py`
  s'il est fusionné, sinon `tools/audit_nuits.py jouer`/`analyser`), `--processus 4` au plus :
  achats, parts servies ou non, dettes, tâches proposées / acceptées / faites / dues aussitôt,
  minutes sans recours et en attente, usurpations et violations (aucune). Et le cas réel au banc
  8 h : Relais graine 42.
- Docs : `docs/plan-social.md`, `docs/etat-dev.md` (« Branche `codex-taches-payees`, non
  fusionnée », compte de tests).

## Rapport
Dans `docs/taches/rapport-codex-5-taches-payees.md` : invariant, fonctions changées, cas vérifiés,
mesures avant → après, limites.
