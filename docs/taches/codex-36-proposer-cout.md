# Tâche Codex 36 (A2b, suite) : valider le lot 33 et ramener le coût du geste `proposer`

Branche `codex-proposer-cout` (elle porte ce fichier, issue de `codex-pnj-proposent` **0e7b8ad**), worktree
dans `tmp-worktrees/` (ou reprends celui du lot 33 en passant sur cette branche). **Lot de 30 à 45 minutes**.
Pas de Luna.

Lis `docs/taches/rapport-codex-33-pnj-proposent.md` (ton rapport) et `AGENTS.md` (« Rythme des lots »).

## Le problème
Le lot 33 fait proposer les PNJ, et c'est prometteur (Relais : vols tentés 6 → 4, sans recours 180 → 60 ;
auberge 80 → 20), mais une nuit de 4 h coûte **×7** (mine 11,7 → 83,2 s, auberge 11,5 → 78,2 s), mesuré avant
`684ee70`. Le reste des contrôles est inachevé.

## Ce qu'il faut
1. **Mesurer d'abord** sur 684ee70 (ffcc295 et la branche lancés ensemble, 4 h, graines 42 et 1985, mine et
   auberge) et profiler (`py-spy` ou `--diagnostic` : nœuds par but, offres engendrées par développement, appels
   de `devis_pulsion` et `evaluer_proposition` par recherche).
2. **Le coût d'un geste ne doit pas contenir une recherche.** Si un développement d'état évalue des offres en
   chaîne (un devis de tâche est une recherche ; une offre par bien × auditeur × contrepartie multiplie les
   branches), sors ce calcul de l'expansion : les offres candidates et leurs devis se calculent **une fois par
   choix du but**, sur ce qu'il croit au départ, sous une clé qui dit ce qu'elle lit (dans `_entrees`), et la
   recherche n'en voit que la meilleure par auditeur et par sorte de contrepartie. C'est une approximation
   (comme le trajet estimé du lot 30) : dis ce qu'elle peut faire manquer.
3. **Cible : au plus +20 %** contre ffcc295 sur 4 h, mine et auberge. Si elle n'est pas atteinte, dis où va
   le reste.
4. **Finir les contrôles du lot 33** sur le code final : banc rapide 4 h, 4 graines, quatre scénarios, contre
   ffcc295 (offres, acceptées, tenues, trahisons, vols tentés, sans recours ; chaque vol restant de la crue et du
   Relais expliqué en une ligne ; `voir_alterne` du Relais 7 et la mine 2024 lus) ; `VERIFIER` +
   `spatial.VERIFICATION` 1, 2 h, graine 42, crue et mine ; suite complète une fois.

## Livraison
Commits signés, branche poussée (pas `main`). Mets à jour `docs/etat-dev.md` (entrée du lot 33 : « Branche
`codex-proposer-cout`, non fusionnée », avec ces mesures) et le rapport
`docs/taches/rapport-codex-33-pnj-proposent.md` (une page, mesures finales, limites).
