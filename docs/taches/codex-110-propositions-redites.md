# Tâche Codex 110 : une proposition refusée n'est pas refaite à l'identique sans fait nouveau

Petit lot (`AGENTS.md`, « Rythme des lots »). Pas de Luna. Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. **Un seul
poste** : priorité réduite, au plus 2 processus de calcul ; le lot 108 (`social`, `esprits`) et le lot 109 (`planification`)
tournent en même temps : ce lot reste dans `pnj_propositions.py`, `propositions.py`, `echanges.py` et, s'il le faut, la retenue
des refus (`deliberation.retenir_refus`/`tient`, sans toucher au choix des buts). Termine ton dernier message par `LOT TERMINÉ`
(résumé d'une ligne) ou par `QUESTION : …`.

## Le constat (vérifications 5c2ce81 et 47d4d25, persistant)
Mine, graine 7, minute 244 : **Josse fait deux fois la même proposition à Lucien**, refus « garde » les deux fois. À 5c2ce81 :
Brune à Gorm six fois en crue 11, offres identiques en moins d'une heure (6 / 14 / 16 / 14 sur huit nuits), achats refusés repris
au même prix. Bruts : `C:\Users\msics\donjon\artifacts\verif-integ-47d4d25\` (audit 12 h, mine 7 ; `evidence.json`), rapport
`docs/taches/rapport-codex-94-verif-integ.md`. Le lot 57 (refus d'un marché retenu avec ses moyens et la force offerte) et la
branche `refus-retenus` (un refus se retient selon sa cause) devaient l'empêcher ; le lot 107 vient de borner la demande.

## L'invariant
**Une proposition refusée tient comme un refus retenu selon sa cause** : refaite seulement si le proposant croit un moyen nouveau
(contrepartie plus forte réellement offerte, bien nouvellement porté, refus de méfiance estompé selon la règle existante), jamais à
l'identique dans la même minute ou sur le seul passage du temps quand la cause est « garde », « nécessaire » ou « impossible ».
Trouve le chemin qui refait la proposition (deux appels dans le même choix, retenue non écrite, clé de refus qui ne reconnaît pas
la même offre) et ferme-le dans la règle commune des refus retenus.

## Vérification
- Tests après rechargement, même laps découpé : le cas réel (capture mine 7 vers 240) sans redite ; un autre cas (crue 11, Brune
  à Gorm) ; une proposition refusée puis refaite avec une contrepartie réellement plus forte toujours permise.
- Banc rapide 4 h, quatre scénarios × quatre graines contre la base (cache, sinon calculée une fois et rangée) : propositions /
  acceptées, offres identiques en moins d'une heure, aucune usurpation ni boucle nouvelle.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-relations.md` (§ 7.2) ou `docs/plan-social.md` si la règle change,
`docs/etat-dev.md` (« Branche `codex-propositions-redites`, non fusionnée »). Rapport d'une demi-page :
`docs/taches/rapport-codex-110-propositions-redites.md`.
