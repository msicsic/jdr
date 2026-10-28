# Tâche Codex 211 : un PNJ ne sait pas où est un personnage qu'il n'a pas localisé

Issu du diagnostic 209 (`docs/taches/rapport-codex-209-retours-restants.md`, famille « Localisation inconnue », n° 21/30/31) :
`deliberation._lieu_cru` répond, faute de croyance `lieu`, par **le lieu réel** de tout objet qui n'est pas marqué `mobile`. Les
personnages n'étant pas marqués `mobile`, un PNJ « sait » où est n'importe qui sans l'avoir vu ni entendu : Ilse (crue 2024/42/7,
min 1,2–1,7) voit son abri apparaître et disparaître selon les déplacements réels d'Aubin, sans rien percevoir. C'est une fuite
de l'état réel dans les croyances, contraire au principe de subjectivité (chacun agit sur ses propres croyances). `_lieu_cru` et
`salle_crue` ont environ 77 appelants : l'effet peut être large. Priorité de l'utilisateur : justesse des comportements des PNJ.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots calculent sur ce poste (205, 210) : au plus 2 processus,
priorité réduite. Fichiers : dans `deliberation.py`, **seulement `_lieu_cru`/`salle_crue`** (le lot 205 modifie d'autres
fonctions de ce fichier : n'y touche pas) ; une lecture commune « mobile par nature » où elle a sa place (`monde.py` ou un module
de lecture) ; les appelants qui supposaient la position réelle, s'il faut leur donner une vraie source de croyance ; et leurs tests.
**Pas** `eau.py`, `planification.py`, `route_admissible.py`, `pnj._abriter` (lot 205), `social.py`, `esprits.py` (lot 206),
`agendas.py`, `echanges.py`, `biens.py`, `paroles.py` (lot 207), ni le MJ. **Bruts dans
`C:\Users\msics\donjon\artifacts\localisation-211\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, le rapport 209 (et ses captures `localisation-ilse-753.json`, `localisation-ilse-1034.json`,
`preuve-localisation.json` dans `C:\Users\msics\donjon\artifacts\retours-209\` sur ce poste), les rapports 37 et 69 (recherche
et indices), 135 et 132 (connu, non vu), puis `_lieu_cru`, `salle_crue` et leurs appelants.

## L'invariant
**La position d'une entité mobile par nature (personnage, et tout objet qu'on peut déplacer) ne vient que des croyances de
l'observateur (vue, ouïe, parole, savoir de départ déclaré) ; sans croyance, elle est inconnue. Seuls les éléments fixes du décor
(salles, portes, installations scellées) se savent par leur place.** Les savoirs de départ que le scénario donne explicitement
(qui est où au début, liens connus) restent des croyances déclarées, pas une lecture de l'état réel. Même règle pour tout PNJ ;
aucune règle propre à Ilse, Aubin ou un scénario.

## Vérification
- Reproduire d'abord les trois cas avec les captures du lot 209 (même esprit, seule la position physique d'Aubin change, et la
  position « crue » change aussi), puis montrer qu'après correction elle ne change plus.
- Inventorier les appelants qui dépendaient de cette lecture (recherche de quelqu'un, appel, abri, compagnie, protégé, rendez-vous)
  et dire pour chacun la croyance qui le remplace ; pas de repli caché vers la position réelle.
- Tests après rechargement : le cas réel et un autre de même nature (autre PNJ, autre scénario) ; un savoir de départ déclaré reste
  connu ; un objet fixe reste su ; même laps d'un bloc ou découpé ; monde et rendu rechargés identiques.
- Banc rapide 4 h, cinq scénarios (dont `crue_hameau`) × quatre graines, références du cache, **avec le compteur des changements
  d'avis** (départ du lot 209 : 57 au total) : recherches de personnes, appels, retrouvailles, attentes, S/F/D du lot 183 ; aucune
  usurpation, plantage ni boucle nouvelle.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-localisation-crue` poussée (pas `main`) ;
`docs/etat-dev.md` (« Branche `codex-localisation-crue`, non fusionnée ») ; rapport d'une page
`docs/taches/rapport-codex-211-localisation-crue.md`.
