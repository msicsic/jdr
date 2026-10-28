# Tâche Codex 240 : un recours d'aide reste valable une fois adopté

Diagnostic du lot 237 (`docs/taches/rapport-codex-237-alertes-231.md`, « Gorm, hameau 1985 ») : onze retours chaleur/devoir de
Gorm entre 541 et 545 (nuit 12 h, moteur `4306c14`). Premier abandon sans nouvel échec à **544, instant 326556** : but
chaleur/brasero vide adopté à 326536, après l'accord d'Aubin pour rapporter du bois. La revalidation le remplace par aucun
but, puis la chaleur revient et interrompt l'inspection. Contre-épreuve sur la capture 545 : seul
`urgences.chaleur.etat` change ; `attente` donne le recours vide, `presse` donne `None`, sur les deux moteurs.
`Vue.detresses` ouvre l'aide après une attente ; **sélectionner le recours efface la condition qui l'a ouvert**.
Sur l'intégration actuelle, l'occurrence a disparu de cette nuit, mais le mécanisme se reproduit sur capture.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna.

**Poste : le laptop** (l'utilisateur y travaille) : au plus 2 processus, priorité réduite. Les bruts du lot 237 sont sur
le PC fixe (`C:\Users\msics\donjon\artifacts\alertes-237\`) : rejoue la nuit (hameau, graine 1985, joueur et départ
comme l'audit `tools/audit_nuits.py`) sur un worktree détaché de `4306c14` jusqu'à 541, une seule nuit à la fois, pour
obtenir la capture.

**Fichiers** : `Vue.detresses` et la condition d'ouverture de l'aide (`planification.py`), l'attente de réalisation
d'une aide et son classement (`deliberation.py`), leurs tests (`tests/test_recours_prioritaire.py`,
`tests/test_contrat_engagement.py`). **Pas** : `deliberation.menager_flamme` et `biens.services_proteges` (lot 238),
`pnj_propositions` et `echanges` (lot 228), `pnj.py` (lot 234), `ouie.py` (lot 233), `_classer` tel que corrigé par 239
sauf raccord minimal justifié, le MJ.

**Bruts dans `C:\Users\msics\donjon\artifacts\aide-240\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou
`QUESTION : …`.

## L'invariant
**Un recours adopté reste admissible sous sa propre adoption.** La condition qui ouvre une aide (une attente sans moyen
propre) doit être jugée sur l'état d'avant l'adoption, ou sur une cause qui ne change pas parce que le PNJ a choisi ce
recours ; il ne cesse que si une entrée nouvelle (aide refusée, rompue, rendue inutile, besoin satisfait, palier
supérieur) le justifie. Attendre la réalisation promise par autrui est un état stable, pas une absence de but. Aucune règle
propre à Gorm, au hameau ou à la chaleur.

## Vérification
- Capture réelle 541 : plus de retours chaleur/devoir sans entrée nouvelle ; un autre cas de même nature (autre besoin
  ou scénario, aide promise puis attendue). Monde et rendu rechargés identiques, même laps d'un bloc ou découpé.
- Banc rapide 4 h, cinq scénarios × quatre graines, références du cache, compteur 219 : suspects sans hausse.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
- Branche `codex-aide-stable` poussée (pas `main`). Si la poussée est bloquée, laisse le commit local et dis-le.
- `docs/etat-dev.md` : « Branche `codex-aide-stable`, non fusionnée ». Rapport d'une page
  `docs/taches/rapport-codex-240-aide-stable.md`.
