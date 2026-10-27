# Tâche Codex 205 (lot 196 b) : un seul juge pour l'évacuation et la traversée de l'eau

Deuxième lot correctif du diagnostic 196 (`docs/taches/rapport-codex-196-changements-avis.md`, § 2 cas 2 et 3, § 4.2, § 5
« Lot 196b »), après le lot 201 (196 a, fusionné : boucle de la réserve brisée, crue 271 → 19 retours non justifiés). Demande
de l'utilisateur du 2026-10-27 : **une parade générale aux changements d'avis intempestifs, pas au cas par cas.** Le compteur du
lot 199 (`tools/detecter_changements_avis.py`, intégré à `tools/audit_nuits.py` et `tools/comparer_bancs.py`) mesure le résultat.

Trois familles de retours non justifiés restent liées à l'eau, **à vérifier sur le cas réel avant de corriger** (la base a
changé depuis le diagnostic : lots 163, 185, 189, 197, 201) :
- **Brune, évacuation auto-annulée** (`crue 1985` vers 42 min ; `crue_hameau 1985` vers 204 min) : `eau.en_peril` exempte le PNJ
  dès que la première étape de son intention est une sortie sèche ; l'évacuation adoptée perd donc son palier `PERIL_EAU` à
  l'éveil suivant, dans la même salle humide, et un autre but reprend la main ; ou un recours ordinaire (chaleur) la fait
  rentrer dans la salle d'où l'évacuation vient de la sortir ;
- **Ilse, abri changé en route** (`crue_hameau 2024`, 42–97 min) : `_plan_abri` et l'accomplissement de l'abri ne lisent pas le
  même prédicat ;
- **hameau 7, retours d'abri 5 → 6** relevés au lot 201 (rapport 201), sans attribution établie.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot calcule sur ce poste (204 : `spatial.py`, `proximite.py`,
`monde.py`, `pnj.py`) : au plus 2 processus, priorité réduite. Fichiers : `eau.py`, `deliberation.py`, `planification.py`,
`route_admissible.py`, et leurs tests ; **pas** `pnj.py`, `spatial.py`, `monde.py`, `proximite.py` (lot 204), ni `biens.py`
/`echanges.py` (lot 202), ni le MJ. **Bruts dans `C:\Users\msics\donjon\artifacts\evacuation-205\`.** Termine par
`LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, le rapport 196 en entier, les rapports 199 et 201, puis 41 (route admissible), 163 (survie en route) et 185
(prévision bornée) ; puis `eau.en_peril`, `deliberation._plan_abri`, `_abriter`, `choisir`, `planification.route_admissible`
(ou `route_admissible.refus`).

## L'invariant
**Le péril d'eau d'un lieu est jugé par un seul prédicat, indépendant de l'intention en cours : tant qu'un PNJ se trouve dans
une salle qu'il croit en péril, son évacuation garde la priorité du péril jusqu'à ce qu'il en soit sorti ; aucun recours
ordinaire ne le fait entrer ou séjourner dans une salle qu'il croit en péril, sauf une traversée admissible vers une
destination qu'il croit sèche et sûre ; l'abri choisi, son trajet et son accomplissement lisent le même prédicat d'abri.**
Croyances du PNJ seulement (aucune lecture de l'eau cachée) ; même règle pour tout PNJ ; aucune règle propre à Brune, Ilse, une
salle ou un scénario. Le péril du joueur suit la même règle s'il la partage.

## Vérification
- Reproduire d'abord chaque famille sur la base (captures rechargeables juste avant) et dire laquelle joue encore et pourquoi ;
  si une famille ne se reproduit plus, le dire et ne pas la traiter par hypothèse.
- Tests après rechargement : l'évacuation de Brune va jusqu'au sec sans retour ; un autre cas de même nature (autre PNJ, autre
  salle humide, autre scénario) ; une traversée admissible vers le sec reste possible (le seul chemin vers l'abri passe par une
  salle humide) ; Ilse garde son abri en route sans le changer faute d'entrée nouvelle ; même laps d'un bloc ou découpé ; monde
  et rendu rechargés identiques.
- Banc rapide 4 h, cinq scénarios (dont hameau) × quatre graines (références du cache), **avec le compteur des changements
  d'avis** (départ du lot 201 : crue 19, hameau 17, Relais 1, mine 1, auberge 2) : crue et hameau doivent baisser, aucun
  scénario monter ; minutes dans l'eau, attente et pire passage relevés ; aucune usurpation, plantage ni boucle nouvelle ;
  `VERIFIER` + `spatial.VERIFICATION` 0,2, crue 1985, 2 h. Empreintes 2 h identiques sur Relais/mine/auberge (pas d'eau
  active).
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-evacuation-juge` poussée (pas `main`) ;
`docs/etat-dev.md` (« Branche `codex-evacuation-juge`, non fusionnée ») ; rapport d'une page
`docs/taches/rapport-codex-205-evacuation-juge.md`.
