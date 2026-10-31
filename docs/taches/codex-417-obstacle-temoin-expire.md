# Tâche Codex 417 : un renoncement dû à un témoin tient quand sa position expire

Famille R du lot 414 (`docs/taches/rapport-codex-414-suite-4539dd68.md`, fusionné). Le lot 374 (position crue comme
hypothèse datée) a fait basculer sept méthodes :
- `test_reessai_obstacle` : `essayer_un_autre_moyen_ne_fait_pas_oublier_le_premier_obstacle`,
  `faim_renoncee_attend_un_moyen_dans_les_deux_captures_reelles`, `la_ronde_ordinaire_reverifie_sans_reprendre_le_coffre`,
  `odon_pas_de_reprise_par_delai_ni_date_de_regard`, `odon_reprend_sur_absence_constatee_pas_sur_la_verite_cachee` ;
- `test_temps_reel.PatienceTests.test_cas_reel_brune_renonce_apres_trente_minutes_de_guet` ;
- `test_recours_agenda.RecoursAgendaTests.test_capture_317_constat_et_laps_apres_recharge`.

Cause relevée par le 414 :
- l'expiration de la position retire le témoin de `obstacle_patience` ;
- `_normaliser_suites` substitue au geste bloqué une recherche de personne, dont le préfixe ne porte plus la cause du
  renoncement. Dans la capture d'Odon (31), la proposition devient « demander à Bram où est Gaspard », avec le même but
  d'agenda que le crochetage retenu.

Le PNJ reprend ainsi un but renoncé **par le seul passage du temps**, ce que la décision du 2026-10-27 interdit (réessai
lié à l'obstacle, jamais au délai). Une correction limitée au dernier lieu du témoin ne suffisait pas
(`reessai-corrige.json` toujours rouge, bruts `C:\Users\msics\donjon\artifacts\suite-4539dd68-414\`, laptop).

Lis `AGENTS.md`, `docs/etat-dev.md` (court), les rapports 225 (réessai lié à l'obstacle ; cherche « reessai » dans
`docs/historique-lots.md`), 374, 413 et 414.

## Invariant (un seul)
**Un renoncement retenu sur un obstacle cru (témoin présent, passage barré, refus) tient tant que sa cause n'est pas
démentie par un constat ou une information nouvelle. L'expiration de la position d'un témoin ne dément rien : elle rend
la cause incertaine et permet seulement une vérification (inspection, question, appel). Si le constat établit l'absence,
le renoncement se lève ; sinon il tient.** La cause suit le plan à travers les préfixes de `_normaliser_suites` : une
recherche de personne qui précède le geste bloqué porte la cause, et n'autorise le geste qu'après le constat.

Un autre moyen légitime du même but reste permis (règle 225) ; aucune exception de scénario. Les cinq oracles de
`test_reessai_obstacle` restent intacts.

## Vérification
Les sept méthodes, plus `test_position_hypothese`, `test_chercher_appeler` et `test_contact_position_inconnue` ; cas
réel (Odon, capture 31) et autre cas (Brune au guet) après recharge, même laps entier ou découpé. Banc rapide 4 h,
quatre graines, mine et auberge, contre la base : retours suspects et appels au plus ceux de la base. Pas de suite
complète, ni Luna.

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : `donjon/deliberation.py`, `donjon/planification.py`, `donjon/memoire.py` ou
l'interface de croyances, tests. Lots en cours : 402 (vérification d'intégration, calcul seul), 416 (A6 raccord libre,
`mj.py`) ; pendant S1, n'ajoute aucun registre d'esprit (la cause vit dans les structures existantes). Deux processus au
plus, priorité réduite, calculs longs détachés : vérifie qu'ils vivent avant de rendre la main. La poussée de ta branche
vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) est autorisée.

## Livraison
- Branche `codex-obstacle-temoin-expire`, base `integration`, poussée vers origin.
- Rapport d'une page `docs/taches/rapport-codex-417-obstacle-temoin-expire.md` ; entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\obstacle-temoin-417\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
