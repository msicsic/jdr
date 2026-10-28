# Tâche Codex 252 (A5, lot 3) : la filiation d'un mandat, unique et bornée

Troisième lot d'A5. Conception : `docs/taches/rapport-codex-245-conception-a5.md` (lot 3) ; plan :
`docs/plan-agendas.md` § 6.6 (le mandat) et § 9 (A5) ; arbitrages du 2026-10-28 dans `docs/etat-dev.md`
(« A5, arbitrages ») : **deux niveaux de mandat depuis l'agenda racine, cycles interdits**. Lis-les d'abord.

## L'invariant
**Un agenda confié porte une origine `mandat` reliée à son parent (agenda du mandant) ; chaque agenda connaît ses enfants
confiés ; la filiation est unique (un même parent ne confie pas deux fois la même condition au même titulaire), bornée à
deux arêtes depuis la racine, sans cycle (A→B→A refusé), et persiste après sauvegarde.** C'est l'API commune de
filiation dans `agendas.py`, seule voie d'écriture, que les mandats à venir (lots 4 à 7) utiliseront.

Ce lot **ne choisit pas de mandataire** (lot 5), **ne juge pas l'acceptation selon l'autorité** (lot 4), **ne convertit
pas les anciens contrats** (`echanges.confier`, engagements historiques) : ils gardent leur forme ; seule une délégation
qui passe par l'API nouvelle reçoit la filiation. Un refus du mandaté ne crée aucun enfant ; une relance du même
mandant pour la même condition réutilise l'enfant (idempotente, cohérente avec `agendas.renouveler` du lot 242).

Lot de 30 à 45 minutes (`AGENTS.md`, règles du 2026-10-28 : **pas de suite complète**, calculs longs détachés avec
`CALCUL EN COURS : <fichier>`). Pas de Luna. **Poste : le laptop** (l'utilisateur y travaille) : au plus 2 processus,
priorité réduite.

**Fichiers autorisés d'avance** : `agendas.py` ; la validation de sauvegarde des champs nouveaux (`esprits.py`) ; un
raccord minimal dans `echanges.py` seulement si l'API doit y être appelée par `amener`/`informer` ; `tests/test_agendas_*`,
le contrôle AST d'`agendas` (aucun accès direct aux champs de filiation hors du module). **Pas** : `social.py` (lot 250),
`pnj.py`, `deliberation.py`, `planification.py` (lot 251), le MJ, les scénarios.

## Vérification
- Tests : `amener` et `informer` confiés par l'API (deux sortes) ; refus sans enfant ; relance idempotente ; troisième
  niveau refusé avec cause ; cycle refusé ; profondeur et filiation identiques après sauvegarde et rechargement (monde et
  rendu) ; ancien contrat chargé inchangé ; contrôle AST vert.
- Comme aucune décision ne change : empreintes 2 h (`tools/comparer_bancs.py --empreintes`), Relais, mine, auberge, crue
  et hameau, quatre graines, référence `origin/integration` à ta base (cache) : chronique et mesures identiques, état
  complet identique hors champs nouveaux (montrés en les retirant).
- Pas de suite complète.

## Livraison
- Branche `codex-filiation-mandat` poussée. Rapport d'une page `docs/taches/rapport-codex-252-filiation-mandat.md` ;
  entrée « non fusionnée » dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\filiation-252\`.
  Termine par `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
