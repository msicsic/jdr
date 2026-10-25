# Tâche Codex 69 : chercher quelqu'un en l'appelant, les cas qui restent

Branche `codex-appels-restes` (elle porte ce fichier, issue de l'intégration **4acc36c** : lots 38 à 65 compris), worktree
dans `tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots »). Pas de Luna. **Un seul poste**
désormais : priorité réduite, au plus 3 processus pour les bancs et la suite. Le lot 67 entre dans l'intégration pendant
ton lot : `git merge origin/integration` au début si elle a avancé.

Lots en même temps sur ce poste : 68 (`signes.py`) et un lot de coût (`planification.py`). Ce lot touche
`donjon/deliberation.py` (`appels_vains`, `indice_recherche`, la recherche d'une personne) et `donjon/appel.py` ; pas
`planification.py` ni `signes.py`.

Lis `AGENTS.md`, `docs/etat-dev.md` (**« Vérification d'intégration 5c2ce81 », défaut (2)** ; entrées
`codex-chercher-appeler` lot 37 (lieux cherchés écartés jusqu'à un nouvel indice), `codex-rendez-vous` lot 60,
`appel-negocie`), `docs/plan-ouie.md`, puis `donjon/deliberation.py`, `donjon/appel.py`, `donjon/esprits.py` (`croire`,
indices de lieu), `donjon/ouie.py` (`_bruit_inconnu`). Bruts : `C:\Users\msics\donjon\artifacts\verif-integ-5c2ce81\extraits.txt`
et `audit-12h\` (mine 7, auberge 7 et 2024).

## Le constat (audit 12 h de l'intégration 5c2ce81)
- Mine 7, 470-476 : Odon appelle « Lucien ? » dix fois en tournant baraquement ↔ bureau ↔ galerie (sur ffcc295, c'était
  « Mathe ? » huit fois), puis à 478 mange la croûte de pain de Lucien, qui venait de la lui refuser.
- Mine 1985, 464 : Odon appelle « Mathe ? » sept fois.
- Auberge 7, 624-634 : Odile appelle « Joss ? » dix fois (42 passages par heure) ; auberge 2024, 618-624, neuf fois. Le cas
  Odile/Joss existe déjà sur `main` 42bb9c0. Nuits avec une rafale (au moins cinq appels en quinze minutes) : auberge 6
  sur 8, mine 2 sur 8.
Le lot 37 a traité les lieux réactivés sans indice ; ces rafales ont une autre cause, à établir : un indice qui se renouvelle
(un bruit attribué, une voix entendue, une nouvelle reçue), une cible qui bouge, un appel qui ne compte pas le lieu comme
parcouru, ou un but qui change et recommence la recherche.

## L'invariant
**Chercher quelqu'un en l'appelant ne fait pas plus d'appels que de lieux à parcourir et d'indices réellement nouveaux** ;
un appel resté sans réponse dans un lieu le compte comme parcouru pour cette personne ; un indice ne rouvre que son lieu, et
seulement s'il est nouveau (pas la répétition d'un bruit ou d'une voix déjà prise en compte) ; changer de but ne remet pas
à zéro ce qu'on sait d'une recherche de la même personne. Trouve la cause dans chacun des deux cas réels (mine 7, auberge 7)
et corrige la règle commune ; pas d'Odon, d'Odile ni de délai fixe.
Le vol de la croûte de Lucien juste après son refus : signale-le seulement (le lot 57 retient les refus ; dis si c'est un
autre défaut).

## Vérification (minimale)
- Tests après rechargement, même laps découpé : les deux cas réels (captures mine 7 vers 470, auberge 7 vers 624) : appels
  bornés par les lieux et les indices nouveaux ; un autre cas de même nature ; une vraie réponse ou un vrai indice nouveau
  relancent comme avant.
- Banc rapide (`tools/comparer_bancs.py --reference 4acc36c --processus 3`, 4 h, 4 graines, quatre scénarios) puis l'audit
  12 h des seules nuits mine 7, mine 1985, auberge 7 et 2024, branche seule : appels, rafales, passages par heure.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-ouie.md`, `docs/etat-dev.md` (« Branche `codex-appels-restes`,
non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-69-appels-restes.md`.
