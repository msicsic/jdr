# Tâche Codex 256 (A5, lot 4) : le mandaté juge selon l'autorité qu'il perçoit, sans obéissance automatique

Quatrième lot d'A5. Conception : `docs/taches/rapport-codex-245-conception-a5.md` (lot 4) ; plan : `docs/plan-agendas.md`
§ 5 (« L'autorité ») et § 6.6 (le mandat) ; arbitrages du 2026-10-28 dans `docs/etat-dev.md` (« A5, arbitrages ») :
**les refus d'accueil actuels (méfiance, rancune) tiennent ; l'autorité perçue (statut, ascendant, dette) donne un bonus
borné au jugement de qui écoute déjà, sans obéissance automatique ; « obéir sous contrainte » (la peur arrache un mandat)
est un lot ultérieur.** Déjà fusionnés : ascendant neutre (248, `relations.autorite_reconnue`), statut sourcé (254,
`relations.statuts_reconnus`), filiation (252, `agendas.confier`). Lis-les d'abord.

## L'invariant
**Le PNJ à qui l'on confie un mandat l'accepte ou le refuse par le jugement commun de `echanges.confier` (faisabilité,
coût de son devis, altruisme, lien, VOL), auquel s'ajoute une seule lecture d'autorité perçue envers le mandant : statut
cru dans sa portée (lieu, domaine), ascendant, dette ; bonus borné, jamais une acceptation forcée ; la raison retenue
(adhésion, dette, autorité, refus et sa cause) est enregistrée avant tout récit.** Les refus d'accueil existants passent
avant ; un besoin désespéré, une alarme, le péril de l'eau gardent leur priorité sur le mandat accepté. Une demande
ordinaire (non mandat) garde exactement son jet actuel. Un mandat accepté passe par `agendas.confier` (filiation).

Ce lot **ne choisit pas le mandataire** (lot 5), ne fait pas évoluer l'ascendant (lot 8), n'ajoute pas de parole joueur
(lots 9-10), ne touche pas aux données des scénarios (lot 11 ; épreuves en profils de test).

Lot de 30 à 45 minutes (`AGENTS.md`, règles du 2026-10-28 : **pas de suite complète**, calculs longs détachés avec
`CALCUL EN COURS : <fichier>`). Pas de Luna. **Poste : le PC fixe**, au plus 2 processus, priorité réduite.

**Fichiers autorisés d'avance** : `relations.py` (lecture d'autorité commune), `echanges.py` (`confier` et son jugement),
`agendas.py` (publication du mandat accepté), raccord étroit de `paroles.jet_persuasion` et de l'urgence dans
`deliberation.py` ; tests `tests/test_agendas_*`, `tests/test_relations_*`, `tests/test_echanges_*` et voisins dont une
trajectoire change, **arbitrage avec preuve**. **Pas** : `social.py` et `esprits.py` (lot 255 en cours), `planification.py`,
le MJ, les scénarios.

## Vérification
- Scènes (profils de test) : Gorm, responsable reconnu de ses lieux, confie à Aubin d'amener Brune : Aubin accepte par
  autorité ; le même mandat hors de la portée du statut, ou d'un mandant sans statut ni ascendant, est jugé comme une
  demande ordinaire ; un mandaté endetté accepte par dette ; un mandaté méfiant refuse malgré le statut (refus d'accueil
  tenu) ; un besoin désespéré du mandaté passe devant le mandat accepté. Raison enregistrée, monde et rendu identiques
  après rechargement, même laps d'un bloc ou découpé.
- Banc rapide 4 h, cinq scénarios × quatre graines, références du cache (ta base `integration`), compteur 219, lancé
  détaché : aucun scénario ne déclarant encore de statut ni d'ascendant, les nuits doivent rester identiques ou les écarts
  être expliqués.
- Pas de suite complète.

## Livraison
- Branche `codex-jugement-mandat` poussée. Rapport d'une page `docs/taches/rapport-codex-256-jugement-mandat.md` ;
  entrée « non fusionnée » dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\mandat-256\`. Termine par
  `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
