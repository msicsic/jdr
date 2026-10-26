# Tâche Codex 111 : vérification Luna de l'intégration 91a4351 (deux passes), sans code

Branche `codex-verif-luna-91a4351` (issue de l'intégration, code de **91a4351** : lots MJ 100, 101, 102, 104 et 106 depuis la
vérification Luna du lot 99). **Aucune modification du code** : vérification groupée de `AGENTS.md`, comme les lots 79 et 99.
**Luna disponible** (copies seulement ; `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth` ; `tools/banc_multi.py --connexion
chatgpt`). Un seul poste : Luna en 4 exécutions au plus, priorité réduite ; d'autres lots tournent. Termine ton dernier message
par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, le **rapport du lot 99** (`docs/taches/rapport-codex-99-verif-luna.md` : méthode, vingt scripts, mesures,
défauts N1–N3) et les rapports des lots 100, 101, 102, 104, 106. Reprends exactement la méthode, les vingt scripts et le format
du lot 99 ; ses bruts sont dans `C:\Users\msics\donjon\artifacts\verif-luna-b0042c9\`.

## Ce qu'il faut faire
- **Deux passes** de l'intégration (code 91a4351) sur les vingt scripts.
- Références lues du cache, jamais rejouées : `main` 42bb9c0, 882907c, **b0042c9** (rangée par le lot 99). Range les parties de
  cette intégration dans le cache.

## Rapport (une page, `docs/taches/rapport-codex-111-verif-luna.md`, et une entrée en tête de « Où on en est » de
`docs/etat-dev.md`)
- Appels/tour, s/tour (moyenne et médiane), relances, refus, tours avec refus, replis, par groupe et ensemble : main → 882907c →
  b0042c9 → 91a4351 ; secondes par fonction.
- N1 (message technique sur une description), N2 (mot courant censuré), N3 (« Reformule-la »), fausse absence dans le noir,
  achat du soir : corrigés ou non, textes cités ; « Je ne te dirai pas qui je suis » après un nom donné.
- Tout plantage ou erreur technique, trace complète.
- Défauts nouveaux numérotés (texte affiché, banc, passe, saisie, cause probable). Ne corrige rien.

Bruts dans `C:\Users\msics\donjon\artifacts\verif-luna-91a4351\`. Commits signés (rapport et `etat-dev.md`), branche poussée
(pas `main`).
