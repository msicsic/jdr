# Tâche Codex 254 (A5, lot 2) : un statut n'agit que comme croyance sourcée, de portée définie

Deuxième lot d'A5. Conception : `docs/taches/rapport-codex-245-conception-a5.md` (lot 2) ; plan : `docs/plan-agendas.md`
§ 5 (« L'autorité » : statut, ascendant, lecture dérivée) ; arbitrages du 2026-10-28 dans `docs/etat-dev.md`
(« A5, arbitrages ») : **statut de Gorm sourcé, portée limitée à ses lieux, connu des seuls occupants déclarés comme le
sachant ; ascendants initiaux neutres sauf liens renseignés**. Déjà fusionnés : l'axe `ascendant` neutre (248,
`relations.autorite_reconnue`) et la filiation des mandats (252). Lis-les d'abord.

## L'invariant
**Le statut de A (responsable de lieux, employeur, grade) est une donnée du scénario ; B ne le connaît que comme une
croyance sourcée (savoir déclaré, dit par A ou par un autre), avec une portée (lieux, domaine) ; un statut prétendu
peut être faux, comme un nom prétendu ; l'ignorance ou une prétention contradictoire ne deviennent jamais savoir réel.**
Le statut se lit par une lecture commune (`relations.py`, à côté de `autorite_reconnue`) ; **aucune décision ne le
consomme encore** (lot 4), aucun bonus de jet.

Lot de 30 à 45 minutes (`AGENTS.md`, règles du 2026-10-28 : **pas de suite complète**, calculs longs détachés avec
`CALCUL EN COURS : <fichier>`). Pas de Luna. **Poste : le laptop** (l'utilisateur y travaille) : au plus 2 processus,
priorité réduite.

**Fichiers autorisés d'avance** : `relations.py` (lecture), `esprits.py` (croyance du statut et sa validation),
la validation des profils (`deliberation.py`, raccord) ; la transmission d'un statut dit ou entendu par la voie commune des
nouvelles et de la parole **seulement si elle est nécessaire** à la preuve : `social.py` est en cours de modification par
le lot 250 (`_utile`, `bavarder`) ; ajoute ta transmission dans une fonction distincte, sans toucher ces deux-là.
Tests `tests/test_relations_*`, contrôle AST. **Pas** : `echanges.py`, `agendas.py`, `planification.py`, le MJ, et
**aucune donnée des scénarios historiques** (le statut de Gorm dans la crue étendue relève du lot 11) : les épreuves
utilisent des profils de test.

## Vérification
- Tests : statut déclaré (fixture, Gorm responsable de ses lieux) connu d'un occupant déclaré et inconnu d'un autre ;
  autre employeur ou grade, autre scénario ; statut dit par A, puis par un tiers, avec leur source ; prétention fausse
  crue sur parole puis démentie, sans confiance supérieure à celle d'une voix inconnue ; portée respectée (hors de ses
  lieux, le statut ne vaut pas) ; sauvegarde et rechargement identiques, monde et rendu ; contrôle AST vert.
- Comme aucune décision ne change : empreintes 2 h (`tools/comparer_bancs.py --empreintes`), Relais, mine, auberge,
  crue et hameau, quatre graines, référence `origin/integration` à ta base (cache) : jeu et état complet identiques
  tant qu'aucun scénario ne déclare de statut.
- Pas de suite complète.

## Livraison
- Branche `codex-statut-source` poussée. Rapport d'une page `docs/taches/rapport-codex-254-statut-source.md` ; entrée
  « non fusionnée » dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\statut-254\`. Termine par
  `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
