# Tâche Codex 70 : vérification Luna de l'intégration (deux passes), sans code

Branche `codex-verif-luna-fbcf0ff` (elle porte ce fichier, issue de l'intégration **fbcf0ff** : lots 38 à 68 compris, sauf
33, 36, 52 et 62/63 qui sont des diagnostics). **Aucune modification du code** : c'est la vérification groupée prévue par
`AGENTS.md` (« Vérification à l'intégration »), confiée à Codex. **Luna disponible sur ce poste** (copies seulement ;
`SEUIL_AUTH` vers le coffre du dépôt principal ; `tools/banc_multi.py --connexion chatgpt`, sinon il joue avec
anthropic). Un seul poste : Luna en 4 exécutions parallèles au plus, priorité réduite pour le reste ; un lot de coût et le
lot 69 tournent aussi sur ce poste.

Lis `AGENTS.md`, puis dans `docs/etat-dev.md` l'entrée **« Vérification Luna de l'intégration f033364 »** (méthode,
scripts, défauts relevés) et les entrées des lots qui touchent le MJ depuis : 56 (sens des comptes), 59 (parole sans
contenu), 61 (orientation), 65 (`attendu` désignable), 67 (prime conditionnelle). Les bruts de la vérification précédente
sont dans `C:\Users\msics\donjon\artifacts\verif-luna-f033364\` (`relecture.txt`, `analyse.py`, `textes.py`, `fil.py`) :
reprends la même méthode et le même format.

## Ce qu'il faut faire
- **Deux passes** de l'intégration `fbcf0ff` sur les onze scripts de f033364 (relais, crypte, atelier, echanges,
  signes-ecart, signes-noir, signes-guet, luna-restes-ambiance, noms-dialogue, soir-appel, soir-noir), plus `ressources`,
  `comptes` (désormais préparé avec ses noms), `sous-obstacle-*`.
- Référence : `main` 42bb9c0 lue du cache (`artifacts/references/42bb9c0/`) pour les onze ; et l'intégration f033364 lue
  du cache (`artifacts/references/f033364…/banc_multi/`) pour tous, afin de mesurer l'évolution depuis la dernière
  vérification. **Ne rejoue pas `main`** (son lanceur ne lit plus les nouveaux modules ; voir la méthode de f033364 pour
  lire le cache avec un lanceur détaché de 3b6415b si la clé l'exige). Range les parties de fbcf0ff dans le cache.
- Relis saisie par saisie : textes affichés, appels, refus et motifs.

## Rapport (une page, `docs/taches/rapport-codex-70-verif-luna.md`, et une entrée « Vérification Luna de l'intégration
fbcf0ff » en tête de « Où on en est » dans `docs/etat-dev.md`)
- Appels/tour, s/tour, relances, refus, tours avec refus, replis, par groupe et ensemble : main → f033364 → fbcf0ff.
- Pour chacun des lots 56, 59, 61, 65 et 67 : son comportement tient-il dans les deux passes (textes cités) ?
- Les défauts de f033364 : corrigés ou non (prime inventée, faux « Précise… », méta-langage, orientation, impressions
  d'« observer », banc `comptes`).
- Défauts nouveaux, numérotés (texte affiché, banc, passe, saisie, cause probable). Ne corrige rien.

Bruts dans `artifacts/verif-luna-fbcf0ff/` (non versionnés). Commits signés (rapport et `etat-dev.md` seulement), branche
poussée (pas `main`).
