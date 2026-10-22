# Tâche Codex 1 : varier les profils du Relais et de la crue

Données seulement, sans toucher au moteur. Décision de l'utilisateur (2026-10-22, voir
`docs/etat-dev.md`, « Décisions prises le 2026-10-22 ») : prendre les profils proposés par
l'analyse du Relais (`docs/analyse-relais.md`).

## Contexte
Au Relais (`donjon/scenario_relais.json`) et à la crue (`donjon/scenario_crue.json`, scénario dérivé
du Relais), presque tous les PNJ ont douceur 100 (`ne_blesse_pas`) et souvent honnêteté 100 : au banc,
ni poussée ni forçage, et un seul suspect possible (Brune). Les valeurs sont décrites dans
`donjon/caractere.py` (0 à 100 ; 100 interdit ce que la valeur réprouve, en dessous c'est un prix).

## À faire
1. Dans les deux scénarios : Brune douceur 75 ; Ilse honnêteté 80 ; Aubin honnêteté 65 et douceur 80 ;
   Gorm inchangé. Retire les anciennes limites tout ou rien qui imposeraient 100 à ces valeurs
   (`ne_vole_pas`, `ne_ment_pas`, `ne_blesse_pas` : voir `caractere.LIMITES` et la migration au
   chargement). Garde les traits narratifs cohérents (un texte qui dirait « il ne vole jamais »
   pour Aubin doit être nuancé).
2. Ne change rien d'autre.

## Vérifications
- Suite complète verte (`.venv\Scripts\python.exe -m unittest discover -s tests -q`, en priorité
  réduite). Les tests de scène qui supposaient l'ancienne honnêteté ou douceur : adapte-les en disant
  pourquoi dans un commentaire, ou construis la scène avec le profil voulu.
- `planification.VERIFIER` sur une nuit de 8 h de chaque scénario modifié.
- Bancs 8 h, `main` puis la branche, l'un après l'autre : Relais
  `python -m donjon.banc_pnj --heures 8 --graines 1985 7 42 2024 3 11 99 500 --joueur chambre_cloche`,
  crue `--scenario crue --joueur chambre_cloche` (8 graines). Rapporte : vols tentés et vus (par
  auteur), poussées, forçages, méfiances, rumeurs, échanges, achats, minutes sans recours et en
  attente, usurpations et violations (aucune tolérée). Et `tools/audit_nuits.py analyser` sur
  8 graines × 12 h de chaque scénario.
- Docs : `docs/analyse-relais.md` (proposition appliquée, mesures), `docs/etat-dev.md`
  (« Branche `codex-profils`, non fusionnée », compte de tests).

## Rapport
Dans `docs/taches/rapport-codex-1-profils.md` : changements, mesures avant → après, ce qui a changé
dans les nuits (qui vole, qui pousse, qui force), limites.
