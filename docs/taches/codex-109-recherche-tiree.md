# Tâche Codex 109 (coût) : pourquoi une recherche de l'auberge tirée coûte deux fois plus, puis un levier exact

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). Pas de Luna. Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`.
**Un seul poste** : priorité réduite, au plus 2 processus de calcul ; le lot 107 (`echanges`, `propositions`, `narration`) et le lot
108 (`social`, `esprits`) tournent en même temps. Ce lot touche `planification.py`. Termine ton dernier message par `LOT TERMINÉ`
(résumé d'une ligne) ou par `QUESTION : …`.

**Contexte.** Seuil de l'utilisateur pour avancer `main` : auberge 12 h ≤ ×1,5 contre `42bb9c0`, fixe et tiré. Après le lot 105 :
**×1,75 fixe / ×2,67 tiré** (cohorte du lot 105). Le profil du lot 98 : 58 % du surcoût vient de la **fréquence** des recherches
(décision de l'utilisateur en attente, **hors de ce lot**), 42 % de leur **coût moyen** ; ce coût moyen est surtout un écart du
départ **tiré** : **123 → 209 ms par recherche** (fixe : 99 → 92 ms). Les lots 98 b et 105 ont pris les leviers exacts les plus
simples (obstacles, recopie des états).

## D'abord, mesurer
Auberge 1985 **tirée**, tranche 8–12 h, ancien `42bb9c0` contre intégration actuelle, mêmes conditions : distribution des
recherches par PNJ et but (nombre, nœuds, ms, issue), états développés par recherche, successeurs par état, et µs par nœud ; dis
si l'écart vient de **plus d'états par recherche** (quels buts, quelles familles de gestes) ou d'**états plus chers** (quelles
fonctions), et en quoi le tiré diffère du fixe (PNJ, buts, salles, objets portés).

## L'invariant (choisi d'après la mesure, un seul)
Le premier levier **exact** que désigne la mesure, à résultats de recherche identiques (`comparer --calcul`) : par exemple une
lecture refaite par nœud qui ne dépend que de la `Vue` ou de la salle, une normalisation de geste (`_normaliser_suites`) faite une
fois, une génération de `gestes` qui reconstruit ce qui ne change pas. Si le levier principal change des résultats de recherche
ou des décisions, **n'implémente rien** et termine par `QUESTION :` avec la mesure.

## Vérification (si implémentation)
Captures (lots 81/86/105) mêmes successeurs ordonnés et coûts hexadécimaux ; empreintes 2 h quatre scénarios × quatre graines
(référence en cache) ; `VERIFIER` + spatial 1, auberge 42 tirée, 2 h ; CPU 12 h auberge 1985 fixe et tirée, mine 1985 fixe, par
paires lancées ensemble (`42bb9c0`/branche, base/branche), deux processus, tranche 8–12 h ; `comparer --calcul` ; suite complète une
fois. Dis où cela place l'auberge contre ×1,5.

## Livraison
Commits signés, branche poussée (pas `main`). `docs/etat-dev.md` (« Branche `codex-recherche-tiree`, non fusionnée »). Rapport
d'une page : `docs/taches/rapport-codex-109-recherche-tiree.md`.
