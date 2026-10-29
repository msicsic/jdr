# Tâche Codex 297 (A5, lot 7) : réaffecter une charge confiée en retard, sur les seules croyances du mandant

Suite du chantier A5 (mandat et autorité). Lis `AGENTS.md`, `docs/plan-agendas.md`, le rapport de conception
`docs/taches/rapport-codex-245-conception-a5.md` (ligne 7 du tableau et arbitrage « Retard »), puis les rapports des
lots déjà faits : 242 (suivi des charges confiées sur échéance), 256 (jugement du mandat), 258 et 260 (faire ou confier
selon le devis vu par le mandant) et 283 (compte rendu).

## Le constat
Depuis le lot 242, un mandant juge une charge confiée sur son échéance connue (`planification.duree_devis`,
`agendas.suivis_delegations`) : échéance passée sans constat, il va voir, reprend la charge ou la réaffecte. La
réaffectation elle-même n'a pas de contrat : rien ne dit quelle attribution est active, et rien n'empêche de redonner
la charge au titulaire en retard, de la redemander sans raison, ou d'alterner entre deux titulaires.

## L'invariant
**Réaffecter une charge en retard conserve une attribution cohérente : un seul titulaire actif connu du mandant,
choisi par le devis vu du mandant (lots 258/260) parmi les disponibles crus, sans délai arbitraire, sans redonner un
refus inchangé et sans navette.** L'ancien titulaire n'est pas annulé à distance : le mandant l'avertit s'il est
joignable, par la parole commune. Tant que cet avertissement n'est pas entendu, deux intervenants peuvent agir : c'est
un risque connu, à rendre visible dans le rapport, pas à masquer. Un résultat appris en route (compte rendu, constat)
arrête la visite ou la réaffectation. Hystérésis selon la VOL, comme les autres changements d'agenda.

C'est l'arbitrage du 2026-10-28 (`docs/etat-dev.md`, « Décisions prises le 2026-10-28 », A5) : avertir l'ancien
titulaire s'il est joignable puis réaffecter sur croyances, sans annulation à distance.

## Fichiers attendus
`donjon/agendas.py`, `donjon/deliberation.py` ; raccord du suivi 242 dans `donjon/echanges.py` et
`donjon/planification.py` si nécessaire. Ne touche pas au MJ (`mj.py`, `compilateur.py`, `paroles.py`, `sources.py` :
un lot du MJ y travaille).

## Vérification
- Scène réelle : Aubin en retard sur une charge de Gorm (crue étendue au hameau), puis remplacement par un autre
  titulaire. Autre cas de même nature : une charge à la mine. Pour chacun, vérifie :
  - une attribution unique ;
  - l'avertissement, entendu ou non ;
  - un résultat appris en route qui arrête la visite ;
  - un refus retenu non redemandé ;
  - l'absence de navette ;
  - monde et rendu identiques après recharge, même laps d'un bloc ou découpé.
- Empreintes 2 h si les nuits ne réaffectent pas naturellement ; sinon banc rapide 4 h, quatre graines, scénarios
  touchés et Relais, contre la référence de l'intégration (cache). Calcul long détaché avec fichier de fin.
- Pas de Luna ni de suite complète.

## Contraintes
**Poste : le PC fixe.** D'autres lots et une suite complète y tournent : deux processus au plus, priorité réduite.

## Livraison
- Branche `codex-a5-reaffecter` poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) ; si
  la poussée échoue, laisse le commit local et donne son hash.
- Rapport d'une page `docs/taches/rapport-codex-297-a5-reaffecter.md`.
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\reaffecter-297\`.
- Termine par `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
