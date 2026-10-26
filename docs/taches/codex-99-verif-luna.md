# Tâche Codex 99 : vérification Luna de l'intégration b0042c9 (deux passes), sans code

Branche `codex-verif-luna-b0042c9` (issue de l'intégration, code de **b0042c9** : lots 79 à 96 compris, dont les lots MJ 82,
83, 84, 89, 91, 93, 95 et 96). **Aucune modification du code** : vérification groupée de `AGENTS.md`, comme les lots 70 et 79.
**Luna disponible** (copies seulement ; `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth` ; `tools/banc_multi.py --connexion
chatgpt`). Un seul poste : Luna en 4 exécutions au plus, priorité réduite ; d'autres lots tournent (dont un qui mesure du CPU).
Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

**Objectif de l'utilisateur** : le temps avant la réponse au joueur (appels et secondes par tour) **et** la qualité du MJ.

Lis `AGENTS.md`, le **rapport du lot 79** (`docs/taches/rapport-codex-79-verif-luna.md` : méthode, vingt scripts, mesures,
défauts) et les rapports des lots 91, 93, 95, 96. Reprends exactement la méthode, les vingt scripts et le format du lot 79 ;
ses bruts sont dans `C:\Users\msics\donjon\artifacts\verif-luna-882907c\`. L'instrumentation du lot 93 (durée, premier jeton,
jetons par appel, chemin critique) est désormais dans le fil : sers-t'en.

## Ce qu'il faut faire
- **Deux passes** de l'intégration (code b0042c9) sur les vingt scripts du lot 79.
- Références lues du cache, jamais rejouées : `main` 42bb9c0, f033364, fbcf0ff, **882907c** (rangées par le lot 79). Range
  les parties de cette intégration dans le cache.

## Rapport (une page, `docs/taches/rapport-codex-99-verif-luna.md`, et une entrée en tête de « Où on en est » de
`docs/etat-dev.md`)
- Appels/tour, s/tour (moyenne et médiane), relances, refus, tours avec refus, replis, par groupe et ensemble : main → 882907c
  → b0042c9 ; secondes par fonction (interprétation, récit, audit narratif, fidélité, contre-revue, révision).
- Les défauts nouveaux du lot 79 (absence d'Ilse dans le noir, orientation de Gorm, motifs contradictoires, comptes de Gorm en
  noms publics, achat du soir une passe sur deux) : corrigés ou non, textes cités.
- **Tout plantage ou erreur technique** avec sa trace complète (le lot 96 a vu un plantage du planificateur lors d'une
  proposition du joueur ; le lot 97 le corrige en parallèle : signale s'il revient).
- Défauts nouveaux numérotés (texte affiché, banc, passe, saisie, cause probable). Ne corrige rien.

Bruts dans `C:\Users\msics\donjon\artifacts\verif-luna-b0042c9\`. Commits signés (rapport et `etat-dev.md`), branche poussée
(pas `main`).
