# Tâche Codex 246 : rendre un bien ne s'annule pas en route parce qu'on s'en sert pour y aller

Diagnostic du lot 237 (`docs/taches/rapport-codex-237-alertes-231.md`, « Maël, hameau 42 ») : quatre retours suspects de
Maël, 419–451 (moteur `4306c14`). **419, instant 251779** : restitution torche → Aubin adoptée ; **251840**, au beffroi
sombre, `necessaire=True` fait disparaître ce même recours au profit de l'inspection de la crypte (palier 9 contre 5).
Même bascule antichambre/échoppe à 420 ; restitution effective seulement à 451. `_rendre` consulte la nécessité immédiate
du bien via `echanges.necessaire` et `deliberation.lumiere_utile`, **sans distinguer son emploi pendant le transport de
son abandon à la remise**. Sur l'intégration actuelle l'occurrence a disparu de cette nuit, mais la capture 421 rejette
encore le retour en cours sur les deux moteurs.

Lot de 30 à 45 minutes (`AGENTS.md`, dont les règles du 2026-10-28 : **pas de suite complète**, calculs longs détachés
avec `CALCUL EN COURS : <fichier>`). Pas de Luna.

**Poste : le laptop** (l'utilisateur y travaille) : au plus 2 processus, priorité réduite. Les bruts du lot 237 sont sur le
PC fixe : rejoue hameau 42 (départ tiré, joueur et graine de l'audit) sur un worktree détaché de `4306c14` jusqu'à 421
pour obtenir la capture, une seule nuit à la fois.

**Fichiers autorisés d'avance** : `_rendre` et l'admission/revalidation de la restitution (`planification.py`,
`deliberation.py`), `echanges.necessaire` et `deliberation.lumiere_utile` **en raccord** si la distinction transport /
remise l'exige (le lot 228, qui touchait `necessaire`, est fusionné : intègre son contrat de capacité sans le défaire), et
leurs tests (`tests/test_garde_pret.py`, `tests/test_contrat_engagement.py`, et tout fichier de tests voisin dont une
attente de trajectoire change : **arbitrage autorisé avec preuve**, aucune assertion affaiblie sans preuve, capture
réancrée dite). **Pas** : la recherche et sa borne, `Vue.detresses` (240), `Vue.aides` et `duree_devis` (242),
`Vue.recharge_utile` (244), `pnj._jugement_placement` (234), `biens.services_proteges` (232/238), le MJ.

**Bruts dans `C:\Users\msics\donjon\artifacts\restitution-246\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou
`QUESTION : …`.

## L'invariant
**Admission et revalidation communes du transport et de l'état de remise.** Un bien qu'on rapporte reste utilisable
pendant le trajet de remise (s'éclairer avec la torche qu'on rend) : ce besoin du trajet ne rend pas la remise
inadmissible. La restitution n'est écartée que si le PNJ a besoin du bien **après** la remise, d'après ses croyances, et
sans autre moyen. On ne force pas non plus une remise qui laisserait un besoin sans moyen à son arrivée. Aucune règle
propre à Maël, à la torche ou au hameau.

## Vérification
- Capture réelle 421 : plus de rejet du retour en cours ; restitution effectuée ; un autre cas de même nature (autre bien
  utilisé en chemin : clé, lampe, outil ; autre scénario). Monde et rendu rechargés identiques, même laps d'un bloc ou
  découpé ; un cas où le bien reste vraiment nécessaire après la remise (pas de remise forcée).
- Banc rapide 4 h, cinq scénarios × quatre graines, références du cache, compteur 219 : lancé détaché ; suspects sans
  hausse.
- Pas de suite complète : le superviseur la lance à la fusion.

## Livraison
- Branche `codex-restitution-route` poussée (pas `main`). Si la poussée est bloquée, laisse le commit local et dis-le.
- `docs/etat-dev.md` : « Branche `codex-restitution-route`, non fusionnée ». Rapport d'une page
  `docs/taches/rapport-codex-246-restitution-route.md`.
