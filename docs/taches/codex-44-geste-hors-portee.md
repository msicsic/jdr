# Tâche Codex 44 : un geste sur un objet hors de portée suit une seule règle, typé ou improvisé

Branche `codex-geste-hors-portee` (elle porte ce fichier, issue de l'intégration **cd7195d** : lots 38 à 42 compris),
worktree dans `tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots ») : un invariant,
vérification minimale, rapport d'une page. **Luna disponible sur ce poste** (`SEUIL_AUTH` vers le coffre du dépôt
principal ; copies seulement).

Un autre lot tourne sur l'autre poste (43, gardien en détresse : `deliberation.py`, `planification.py`,
`echanges.py`, `esprits.py`). Ne touche pas à ces fichiers.

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées `codex-sous-obstacle`, `codex-luna-restes`, `temps-fin-marche`,
`repli-et-appel`, `mj-restes`, lots 40 et 42), `docs/contrat-mj.md`, puis `donjon/moteur.py` (validation et fiche
d'`improviser`, `_a_toucher`, `_approcher`), `donjon/obstacles.py` (`passer_obstacle`, `compiler`), `donjon/mj.py`
(question de faisabilité, fiche), `donjon/consignes.py` (ce que le MJ sait de `passer_obstacle` et d'`improviser`).
Bruts : `C:\Users\msics\donjon\artifacts\verif-luna-8443458\relecture.txt`, banc `relais`, saisies n° 20 et 21,
les quatre parties (`main` et intégration).

## Le constat (vérification Luna d'intégration 8443458, deux passes)
« est-ce que je pourrais passer sous la poutre effondrée ? », la poutre à deux mètres, hors de vue (Corvus s'est
tourné) : jamais `passer_obstacle` (alors que `codex-sous-obstacle` donnait la fiche « ramper 12 s » 12 fois sur 12,
poutre en vue). Luna essaie `franchir` (échelle), puis `improviser`. Passe 1 : le moteur accepte une fiche abstraite
« Geste concernant la poutre effondrée. Test DEX (+3), outil +0, difficulté 10 … Durée : 1 min », sans effet de
déplacement, sur une poutre hors de portée. Passe 2 : « Approche-toi de la poutre effondrée ». Sur `main`, refus
narratifs divers. Deux traitements incohérents du même geste.

## L'invariant
**Un geste sur un objet que Corvus peut désigner mais pas toucher suit une seule règle, quelle que soit l'opération,
`improviser` comprise** : le moteur rejoint l'objet par la marche quand un chemin connu y mène (comme les gestes
typés, `_a_toucher` / `_approcher`), sinon il dit d'approcher, avec `attendu` ; jamais une fiche de jet sans
déplacement sur un objet hors de portée. Et l'obstacle qu'on veut passer dessous ou par-dessus se prépare par
`passer_obstacle`, connu ou seulement en souvenir : trouve pourquoi Luna ne le choisit plus ici (fil complet de la
partie : contexte reçu, souvenirs visuels, refus du moteur), et corrige la règle commune (désignation d'un souvenir,
refus avec `attendu` qui oriente, consigne là où une règle manque vraiment), pas la poutre ni le Relais.

## Vérification (minimale)
- Tests après rechargement, chaîne complète avec MJ simulé : le cas réel (poutre à deux mètres, hors de vue :
  question de faisabilité → fiche de `passer_obstacle` avec la marche jusqu'à elle, ou refus « approche-toi »
  cohérent ; « tenter » fait marcher puis ramper) ; un autre de même nature (un `improviser` sur un objet hors de
  portée ailleurs : marche puis fiche, ou refus avec `attendu`, jamais une fiche sans déplacement).
- Luna, **une passe** : `relais`, `sous-obstacle-*` (les bancs de `codex-sous-obstacle`), `atelier`,
  `tools/banc_multi.py`, référence `main` lue du cache (voir le rapport du lot 40 pour lancer la référence avec son
  outil historique) ; appels par tour, textes affichés pour relais n° 20 et 21.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md` si le contrat change, `docs/etat-dev.md`
(« Branche `codex-geste-hors-portee`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-44-geste-hors-portee.md` (cause, invariant, fonctions, mesures, limites).
