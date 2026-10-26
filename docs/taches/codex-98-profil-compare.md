# Tâche Codex 98 (coût) : profil comparé de l'auberge contre `42bb9c0`, puis le premier levier exact

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). Pas de Luna. Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`.
**Un seul poste** : priorité réduite, au plus 2 processus de calcul ; d'autres lots Codex tournent (vérification lourde, MJ).
Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

**Seuil de l'utilisateur pour avancer `main`** : auberge 12 h ≤ ×1,5 contre `42bb9c0`, départ fixe **et** tiré. Après le lot
92 c : **×1,96 fixe / ×3,22 tiré**. Le lot 92 c a retiré 40 % des nœuds de l'auberge tirée pour seulement 5 % de CPU :
**le temps n'est plus principalement dans le nombre d'états développés**.

Lis `AGENTS.md`, `docs/etat-dev.md` (lots 71, 72, 76, 81, 86, 87, 92 c), les rapports `rapport-codex-76-bissection-auberge.md`
(Q ×4,3 à nœuds presque égaux), `rapport-codex-86-gestes-par-noeud.md`, `rapport-codex-92c-preuves.md`.

## D'abord, mesurer (le cœur du lot)
Auberge 1985, départ **fixe** puis **tiré**, tranche **8–12 h** (capture à 480 min, comme les lots précédents) : profil par
échantillonnage (`py-spy` si disponible, sinon `cProfile` en gardant à l'esprit qu'il grossit les petites fonctions), sur
`42bb9c0` et sur l'intégration actuelle, mêmes conditions. Décompose le temps CPU par grande famille : choix du but
(`deliberation.choisir`, préparation de `Vue`), recherches (expansions, `gestes`, routes/tarifs, devis), reprises de graphes et
certificats, perception (`esprits`, `spatial`, signes), ouïe, marche/exécution des gestes, empreintes d'état, sauvegarde. Tableau
ancien → actuel en secondes, et les dix fonctions qui portent l'essentiel de l'écart. Compte aussi les **choix** (appels de
`choisir`) et les **recherches** par minute de jeu des deux côtés : le surcoût vient-il de plus de décisions (délibération à
l'événement, temps réel, recours) ou de décisions plus chères ?

## L'invariant (choisi d'après la mesure, un seul)
Le premier levier **exact** que désigne la mesure : mêmes décisions, même monde, mêmes résultats de recherche (`comparer
--calcul`), avec une clé ou une preuve contrôlée par `VERIFIER` / `spatial.VERIFICATION` si c'est une reprise. Si le levier
principal change des décisions (moins de délibérations, par exemple), **n'implémente rien** : rapporte la mesure et termine par
`QUESTION :` avec ce qu'il faudrait accepter.

## Vérification (si implémentation)
Empreintes 2 h quatre scénarios × quatre graines (référence en cache) ; `VERIFIER` + spatial 1, auberge 42, 2 h ; CPU 12 h
auberge et mine 1985, fixe et tiré, par paires lancées ensemble (`42bb9c0`/branche puis base/branche, deux processus), tranche
8–12 h, `comparer --calcul` ; suite complète une fois. Dis où le lot nous place par rapport au seuil ×1,5.

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-planificateur.md` si une règle change, `docs/etat-dev.md` (« Branche
`codex-profil-compare`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-98-profil-compare.md` (le tableau
ancien → actuel, le levier, le gain, la suite).
