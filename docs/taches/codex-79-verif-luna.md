# Tâche Codex 79 : vérification Luna de l'intégration 882907c (deux passes), sans code

Branche `codex-verif-luna-882907c` (elle porte ce fichier, issue de l'intégration **882907c** : lots 38 à 78 compris).
**Aucune modification du code** : vérification groupée de `AGENTS.md`, comme le lot 70. **Luna disponible** (copies
seulement ; `SEUIL_AUTH` vers le coffre du dépôt principal ; `tools/banc_multi.py --connexion chatgpt`). Un seul poste :
Luna en 4 exécutions au plus, priorité réduite ; un autre lot tourne sur ce poste.

Lis `AGENTS.md`, le **rapport du lot 70** (`docs/taches/rapport-codex-70-verif-luna.md` : méthode, scripts, mesures,
défauts) et les entrées des lots du MJ fusionnés depuis : 73 (comptes de l'issue), 74 (gardes justes), 78 (pièce d'un lot).
Reprends exactement la méthode, les vingt scripts et le format du lot 70 ; ses bruts sont dans
`C:\Users\msics\donjon\artifacts\verif-luna-fbcf0ff\`.

## Ce qu'il faut faire
- **Deux passes** de l'intégration `882907c` sur les vingt scripts du lot 70.
- Références lues du cache, jamais rejouées : `main` 42bb9c0 (onze scripts), f033364 et **fbcf0ff** (tous, rangés par le
  lot 70). Range les parties de 882907c dans le cache.

## Rapport (une page, `docs/taches/rapport-codex-79-verif-luna.md`, et une entrée en tête de « Où on en est » de
`docs/etat-dev.md`)
- Appels/tour, s/tour, relances, refus, tours avec refus, replis, par groupe et ensemble : main → f033364 → fbcf0ff → 882907c.
- Les huit constats nouveaux du lot 70 : corrigés ou non (textes cités) ; l'achat d'une planche au soir exécuté en ligne ?
- Défauts nouveaux numérotés (texte affiché, banc, passe, saisie, cause probable). Ne corrige rien.

Bruts dans `artifacts/verif-luna-882907c/`. Commits signés (rapport et `etat-dev.md`), branche poussée (pas `main`).
