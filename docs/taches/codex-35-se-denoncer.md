# Tâche Codex 35 : « Brune dit à Gorm que Brune porte les planches » — qui parle, et de qui

Branche `codex-soi-meme` (elle porte ce fichier, issue de l'intégration **41c1c7c**), worktree dans
`tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots »). Luna disponible mais non
requise (aucun changement du MJ attendu).

Lis `AGENTS.md`, `docs/etat-dev.md` (entrée « Vérification d'intégration ffcc295 »), puis `donjon/social.py`
(confidences, rumeurs, `retenir_parole`, `faire_entendre`), `donjon/paroles.py`, `donjon/signes.py` (lectures
`intention_lue`), `donjon/recit_pnj.py` (lignes « X dit à Y que … »), `donjon/relations.py` (`aveu`).

## Le constat (audit 12 h de l'intégration ffcc295, existe aussi sur `main` 42bb9c0)
- Crue, graine 2024, minute 421 : « Brune dit à Gorm que Brune porte les planches de bac, qui n'est pas à elle
  (doute). », juste avant « Brune surprend les mots d'Aubin à Gorm ».
- Crue, graine 7, minute 391 : « Brune dit à Ilse que Brune semble guetter la réserve ».
Extraits : `C:\Users\msics\donjon\artifacts\verif-integ-ffcc295\extraits.txt` ; nuits complètes dans
`audit-12h\`. Rejoue ces deux nuits (`donjon.banc_pnj --scenario crue --heures 8 --graine 2024 --chronique`,
puis 7) et établis d'abord **ce qui se passe** : un PNJ qui transmet vraiment une accusation contre lui-même
(confidence, rumeur ou lecture de ses propres signes), ou une ligne du récit qui attribue mal la parole d'un
autre (Aubin) ou la rumeur reçue.

## L'invariant (selon ce que tu trouves)
- Si c'est le comportement : ce qu'un personnage dit de lui-même qui l'accuse passe par une seule voie, l'aveu
  (contenu `aveu`, choix pesé par ses valeurs), jamais par la transmission d'une confidence, d'une rumeur ou
  d'une lecture ; et nul ne lit ses propres signes. Même règle pour le joueur et les PNJ.
- Si c'est le récit : chaque ligne nomme le vrai locuteur et le vrai destinataire, et distingue « dit » de
  « entend dire » ; une règle commune du récit, pas une phrase propre à ce cas.
Corrige la cause à la source, pas le symptôme ; dis si l'autre famille existe aussi.

## Vérification (minimale)
- Tests après rechargement (`tests/test_soi_meme.py`) : le cas réel (scène reconstituée ou enregistrée) et un
  autre cas de même nature (un autre PNJ, un autre fait qui l'accuse).
- Si le comportement change : banc rapide (`tools/comparer_bancs.py`, 4 h, 4 graines, crue et Relais, contre
  41c1c7c), écarts expliqués ; sinon empreintes 2 h identiques (récit exclu si seul le récit change : dis-le).
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/etat-dev.md` (« Branche `codex-soi-meme`, non fusionnée »).
Rapport d'une page : `docs/taches/rapport-codex-35-soi-meme.md`.
