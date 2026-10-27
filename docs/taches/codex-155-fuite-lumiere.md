# Tâche Codex 155 : la lumière ou l'abri ne ramènent pas vers le danger fui

Petit lot de correction issu de la vérification d'intégration 2d504ae (lot 148). Lot de 30 à 45 minutes (`AGENTS.md`). Pas de
Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres
lots tournent sur ce poste, deux sur le laptop : au plus 2 processus de calcul, priorité réduite. Ce lot touche `defense.py`,
`deliberation.py`, `planification.py` (pression, abri, lumière) et leurs tests ; **pas** `agendas.py`, ni `mj.py`, `sources.py`,
les fournisseurs, `consignes.py` (lots MJ en cours). Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par
`QUESTION : …`.

Lis `AGENTS.md`, le rapport du lot 148 (`docs/taches/rapport-codex-148-verif-integ.md`, défaut « Crue 2024, Brune, 687–715 »)
et ses bruts (`C:\Users\msics\donjon\artifacts\verif-integ-2d504ae\`, audit 12 h crue 2024), `docs/etat-dev.md` (« À revoir »,
**fuite ↔ sécurité** : Ilse au Relais 2024, et la correction proposée), les rapports des lots 17 (force 4c, fuite), 88 et 90
(boucle lumière/inspection d'Aubin, inertie des recours), puis `defense.choisir`, `_plan_abri`, `_plan_lumiere`, `Vue.pression`.

## Le défaut
Crue 2024 : après les coups d'Aubin (633, 686), Brune va et vient entre le palier et la galerie de 687 à 715 : 28 « reste dans
la lumière », 68 passages dans l'heure ; relevés : `fuir Aubin`, sécurité 100, noir. Absent de la même nuit `057766f`. La fuite
s'achève dès que la salle change ; puis la lumière ou l'abri la ramènent vers la salle du danger, et `defense.choisir` la fait
refuir.

## L'invariant
**Un lieu où le PNJ croit un danger actif (un agresseur perçu ou cru là, `defense`) n'est ni un abri ni une lumière désirable
pour lui, et y passer coûte comme une présence crainte, tant que le danger dure à ses yeux ; la fuite et les recours de sécurité
lisent la même croyance.** Pas de délai fixe ni de règle propre à Brune, Aubin ou la crue ; toute lecture nouvelle entre dans
`_entrees` (clé de la mémoire, graphes repris, certificat). Commence par reproduire sur une capture rechargée (rejoue la nuit
crue 2024 jusqu'à ~680 sur copie) ; si la cause est ailleurs, corrige l'invariant réel et dis-le.

## Vérification
- Tests après rechargement : la capture de Brune (plus de va-et-vient vers la salle d'Aubin, un abri ou une lumière ailleurs ou
  l'attente) ; un autre cas de même nature (Ilse au Relais après une violence, ou une scène d'auteur) ; même laps d'un bloc ou
  découpé, même `data` ; quand le danger cesse (agresseur parti, neutralisé), le lieu redevient un abri.
- Empreintes 2 h, quatre scénarios × quatre graines contre la base (cache) : identiques attendues hors des nuits avec violence ;
  banc rapide 4 h crue et `rixe` × quatre graines, passages par heure, aucune usurpation ni boucle nouvelle ; l'audit 12 h de la
  seule crue 2024 pour le cas réel. `VERIFIER` + `spatial.VERIFICATION` 0,2 sur 2 h, crue 2024.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-fuite-lumiere` poussée (pas `main`). `docs/etat-dev.md`
(« Branche `codex-fuite-lumiere`, non fusionnée » ; « À revoir » mis à jour). Rapport d'une page :
`docs/taches/rapport-codex-155-fuite-lumiere.md`.
