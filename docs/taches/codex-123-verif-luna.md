# Tâche Codex 123 : vérification Luna de l'intégration 057766f (deux passes), sans code

Branche `codex-verif-luna-057766f` (issue de l'intégration ; code de **057766f** : depuis la vérification Luna du lot 111
sur 91a4351, lots MJ 112 (rappels du passé), 113 (comptes avant règlement), 116 (rapports illisibles), et lots PNJ 115,
120, 121). **Aucune modification du code** : vérification groupée de `AGENTS.md`, comme les lots 99 et 111.
**Poste : le PC fixe** (`C:\Users\msics\donjon`, connexion stable). Luna disponible (copies seulement ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth` ; `tools/banc_multi.py --connexion chatgpt`). Luna en 4 exécutions au plus,
priorité réduite. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, le **rapport du lot 111** (`docs/taches/rapport-codex-111-verif-luna.md` : méthode, vingt scripts, mesures,
défauts) et celui du lot 99, puis les rapports des lots 112, 113 et 116. Reprends exactement la méthode, les vingt scripts et
le format du lot 111.

## Ce qu'il faut faire
- **Deux passes** de l'intégration (code 057766f) sur les vingt scripts.
- Références lues du cache, jamais rejouées : `main` 42bb9c0 et **91a4351** (rangée par le lot 111), présentes dans
  `C:\Users\msics\donjon\artifacts\references\` de ce poste. Les autres références historiques (882907c, b0042c9) ne sont
  pas sur ce poste : reprends leurs chiffres dans les rapports 99 et 111, sans les rejouer. Range les parties de cette
  intégration dans le cache.

## Rapport (une page, `docs/taches/rapport-codex-123-verif-luna.md`, et une entrée en tête de « Où on en est » de
`docs/etat-dev.md`)
- Appels/tour, s/tour (moyenne et médiane), relances, refus, tours avec refus, replis, rapports d'audit illisibles, par
  groupe et ensemble : main → 91a4351 → 057766f ; secondes par fonction.
- Défauts du lot 111 : remboursement de Gorm perdu (faux refus de quantité), réserve sur « les faits » en ambiance, confusion
  comptable de l'achat du soir, identité refusée après un nom donné, N1/N2/N3, fausse absence dans le noir : corrigés ou
  non, textes cités.
- Tout plantage ou erreur technique, trace complète.
- Défauts nouveaux numérotés (texte affiché, banc, passe, saisie, cause probable). Ne corrige rien.

Bruts dans `C:\Users\msics\donjon\artifacts\verif-luna-057766f\`. Commits signés (rapport et `etat-dev.md`), branche poussée
(pas `main`).
