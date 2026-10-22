# Tâche : un outil pour comparer `main` et une branche au banc

## Le besoin
Chaque chantier compare `main` et sa branche au banc sans joueur, et chaque agent réécrit pour cela
ses propres scripts (worktree de référence, boucles de bancs, extraction des mesures, comparaison
d'empreintes). C'est long, coûteux et inégal. Un outil commun, utilisé par tous, doit le faire.

## À faire : `tools/comparer_bancs.py`
- Entrées : la référence (par défaut `main`) et la branche à comparer (par défaut le worktree
  courant) ; scénarios (par défaut ceux qu'on donne, sinon le Relais) avec leur salle de joueur
  (Relais et crue `chambre_cloche`, mine `galerie`, auberge `dortoir`) ; graines (défaut 4) ; heures
  (défaut 4) ; départ tiré ou fixe ; `--processus` ; `--verifier` (active `planification.VERIFIER`) ;
  `--empreintes` (mode identité : seulement chronique, mesures et état final, 2 h par défaut).
- Il crée lui-même un worktree détaché temporaire de la référence (dans le dossier temporaire du
  système ou `.worktrees/ref-<hash>`), le supprime à la fin, et ne change jamais de branche dans le
  dépôt principal.
- Il joue la référence puis la branche, l'un après l'autre, en cédant la priorité comme `banc_pnj`.
- Sortie : un tableau par scénario, mesure par mesure, référence → branche (moyennes et étendues),
  les écarts notables en tête, les usurpations et violations, le temps d'une nuit ; en mode
  `--empreintes`, « identique » ou la première nuit et la première minute où elles divergent.
  Option `--sortie` (JSON) pour les rapports.
- Réutilise `donjon/banc_pnj.py` (nuits, mesures, empreintes, `divergence`) plutôt que de les recopier.

## Vérifications
- Tests de l'outil (`tests/test_comparer_bancs.py`) : deux références identiques donnent
  « identique » ; une différence de donnée est détectée (scène construite) ; le worktree temporaire
  est supprimé même en cas d'erreur.
- Essai réel : `main` contre `main` (identique) et `main` contre une branche connue.
- Docs : section « Outils de mesure » de `docs/etat-dev.md`, et `CLAUDE.md` si la commande change.
