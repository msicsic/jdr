# Tâche Codex 10 : le coût de calcul, suite (sans rien changer à ce que font les PNJ)

Branche `codex-cout-suite` (elle porte ce fichier, issue de `main` 9075aea), worktree dans
`tmp-worktrees/`. Lis d'abord `AGENTS.md`, `docs/etat-dev.md` (entrées `planif-rapide`,
`perception-rapide`, `planif-cout`, `cout-calcul`), `docs/plan-planificateur.md` (« Coût de calcul » et
« Coût de calcul, suite ») et `docs/taches/rapport-cout-calcul.md` (profils et limites).

## Ce qui reste (limites du rapport `cout-calcul`)
1. **Recherches épuisées refaites** : la mine reste dominée par les recherches neuves (45 % d'une nuit) ;
   Rémy, Josse et Mathe refont chaque minute des recherches qui épuisent l'espace sans plan. Une
   recherche épuisée sur des entrées données le reste tant que ces entrées ne changent pas : trouve
   pourquoi la mémoire (`_entrees`, `_GRAPHES`) ne les reprend pas (une entrée qui varie sans changer le
   résultat : temps, détresse, prix d'une faute…), et reprends-les exactement, ou borne-les par un
   raisonnement exact (une entrée qui ne peut que rendre le plan plus cher ne peut pas en créer un).
   Toute reprise est vérifiée par `VERIFIER`.
2. **L'empreinte de l'état** (`spatial.etat_vue`) se recalcule à chaque lecture hors d'un état figé :
   5 à 8 % d'une nuit. Rends-la incrémentale ou partagée, avec `spatial.VERIFICATION` comme référence.
3. **Qui bouge revoit toute sa perception** : à mesurer ; seulement si le profil le justifie.

Pas de code compilé pour le planificateur. PyPy a été essayé et écarté (rapport `cout-calcul`).

## Contrat
Rien ne change dans ce que décident les PNJ : nuits identiques à `main` 9075aea (chronique, mesures,
récit, souvenirs, état final complet, recherches) sur 32 nuits (4 scénarios × 4 graines, départ tiré et
fixe, 8 h), par `tools/empreintes_nuits.py` (lancer avec `PYTHONIOENCODING=utf-8`) ou
`tools/comparer_bancs.py --empreintes` ; `VERIFIER` et `spatial.VERIFICATION` 1 sur 2 h, puis 0,2 sur 8 h
graine 42, de chaque scénario, sans écart.

## Mesures
Temps au processeur d'une nuit, `main` → branche, lancés ensemble (le chantier mesure le temps de
calcul), 4 processus au plus ; part de chaque poste avant → après (`py-spy`) ; pic de mémoire ; nombre
de recherches reprises, bornées, refaites.

## Livraison
Commits signés comme d'habitude ; pousse la branche sur `origin` (pas `main`). Docs :
`docs/plan-planificateur.md` (« Coût de calcul, suite »), `docs/etat-dev.md` (« Branche
`codex-cout-suite`, non fusionnée »). Rapport dans `docs/taches/rapport-codex-10-cout-suite.md`. Les
relations 3b (fusion en cours) ajoutent les axes des relations aux entrées des recherches : la branche
sera accordée avec elles à la fusion, la vérification refaite sur le `main` final.
