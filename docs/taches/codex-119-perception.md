# Tâche Codex 119 (coût) : la perception sans calcul redondant — piste A5 de la revue Argon

Lot de coût **exact** (mêmes décisions, empreintes identiques). Pas de Luna. Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. **Un seul poste** : priorité réduite, au plus 2 processus de calcul ; le lot 118
(`planification.py`) tourne en même temps : ce lot reste dans `pnj.py`, `esprits.py`, `signes.py`, `spatial.py`. Termine ton
dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

**Seuil de l'utilisateur** : auberge 1985, 12 h, CPU ≤ ×1,5 contre `42bb9c0`, départ fixe et tiré (aujourd'hui ×1,65 / ×2,64).
Le profil du lot 98 : perception (esprits, spatial, signes) **62 → 111 s** (fixe) et **52 → 104 s** (tiré) sur 8–12 h, jamais
attaquée. Lis `AGENTS.md`, la revue `docs/taches/rapport-revue-argon-cout.md` (point 4 et piste A5), les entrées
`perception-rapide`, `cout-calcul` et lot 72 de `docs/etat-dev.md`, puis `donjon/pnj.py` (`_avancer`), `donjon/esprits.py`
(`percevoir`, `_percus`, `_percus_depuis`), `donjon/signes.py` (`percevoir_tous`, `_percus_gardes`), `donjon/spatial.py`
(`etat_fige`, `etat_vue`).

## Leviers signalés par la revue (à confirmer par la mesure, un commit chacun)
- `pnj._avancer` : `percevoir(monde, id)` appelé pour chaque PNJ juste avant `percevoir_tous(monde)` (double perception à la
  frontière de minute ?).
- `percevoir_signes(monde)` exécuté hors de `with etat_fige(monde)` à chaque pas.
- `signes._percus_gardes` : `repr()` puis `copy.deepcopy(signature)` pour chaque PNJ ; une clé tuple immuable suffit-elle ?
- `esprits._percus_depuis` : quand l'acteur est dans `changes` (chaque pas qu'il fait), `_percus` balaie tous les objets du monde
  au lieu des seuls objets de la salle (index par salle dans la mémoire de l'état figé).

## L'invariant
**Ce qu'un PNJ perçoit est calculé une fois par état du monde qui le change**, sans balayage du monde entier quand la salle suffit,
et sans copie profonde d'une signature immuable ; mêmes perceptions, mêmes croyances, même ordre. Toute lecture gardée reste
recontrôlée par `spatial.VERIFICATION`.

## Vérification
- Pour chaque levier : nuits courtes identiques (empreintes 2 h, Relais et auberge × quatre graines, référence en cache).
- À la fin : empreintes 2 h, quatre scénarios × quatre graines ; `VERIFIER` + `spatial.VERIFICATION=1`, auberge 42, 2 h ; CPU 12 h
  auberge 1985 fixe et tiré par paires lancées ensemble (`42bb9c0`/branche, base/branche), deux processus, tranche 8–12 h,
  `comparer --calcul` identique ; suite complète une fois (`tools/tests.py --processus 2`). Décide sur le CPU nu, pas sur
  `cProfile`.

## Livraison
Commits signés (un par levier), branche poussée (pas `main`). `docs/etat-dev.md` (« Branche `codex-perception-exacte`, non
fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-119-perception.md`.
