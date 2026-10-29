# Tâche Codex 302 (A5, lot 11) : la crue du hameau déclare le statut et les liens de mandat, sans règle de décision

Suite du chantier A5 (mandat et autorité). Lis `AGENTS.md`, `docs/plan-agendas.md`, le rapport de conception
`docs/taches/rapport-codex-245-conception-a5.md` (ligne 11 du tableau et arbitrage « Gorm »), et les rapports des lots
A5 déjà faits : 248 (ascendant neutre), 254 (statut sourcé), 252 (filiation), 256 (jugement du mandat), 258 et 260
(faire ou confier), 283 (compte rendu), 297 (réaffectation).

## Le constat
Les mécaniques A5 existent : statut sourcé, ascendant, jugement du mandat selon l'autorité perçue, choix de confier
selon le devis du mandant, compte rendu, réaffectation. Mais aucun mandat n'est prononcé naturellement dans les nuits :
les preuves viennent toutes de scènes d'auteur. La crue étendue au hameau (`donjon/scenario_crue_hameau.json`, six
PNJ) est le banc prévu pour les groupes : elle ne déclare encore ni le statut de Gorm, ni ses connaisseurs, ni de lien
d'ascendant.

## L'invariant
**Les données du banc n'ajoutent aucune règle de décision : elles déclarent seulement le statut de Gorm, ses
connaisseurs et les liens initiaux. Un mandat qui naît dans la nuit le fait par les mécaniques communes (coûts du
devis vu par le mandant, jugement selon l'autorité perçue), jamais par une attribution forcée.** Arbitrage du
2026-10-28 : statut de Gorm sourcé, portée limitée à ses lieux, connu des seuls occupants déclarés, ascendants initiaux
neutres sauf liens explicitement renseignés. Choisis des liens plausibles d'après les traits des profils, et
justifie-les dans le rapport.

## Fichiers attendus
`donjon/scenario_crue_hameau.json`, tests et scènes ; compteurs de mandats dans `donjon/banc_pnj.py` et
`tools/audit_nuits.py` s'ils manquent (mandats proposés, acceptés, refusés par cause, comptes rendus, réaffectations).
**Aucun fichier du moteur.** Ne touche pas au MJ.

## Vérification
- Données chargées, statut et liens rechargés, validation d'un profil incohérent refusée avec `attendu`.
- Contre-épreuve : le même scénario sans autorité déclarée ne change que ce que l'autorité explique.
- Une autre scène hors crue garde son comportement.
- **Banc rapide** : crue du hameau 4 h × quatre graines contre la référence de l'intégration (cache). Compte les
  mandats naturels (proposés, acceptés, refusés), les comptes rendus et les réaffectations, et vérifie l'absence de
  boucle nouvelle, d'usurpation et de hausse des suspects 219 par nuit. Si aucun mandat ne naît, dis pourquoi : quel
  coût ou quel jugement l'empêche. N'ajuste pas les données pour forcer un mandat.
- Calcul long détaché, fichier de fin écrit même en cas d'échec. Pas de Luna ni de suite complète.

## Contraintes
**Poste : le PC fixe.** D'autres lots y tournent : deux processus au plus, priorité réduite.

## Livraison
- Branche `codex-a5-donnees-hameau` poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur :
  la poussée est autorisée) ; si elle échoue, laisse le commit local et donne son hash.
- Rapport d'une page `docs/taches/rapport-codex-302-a5-donnees-hameau.md`.
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\hameau-302\`.
- Termine par `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
