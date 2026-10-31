# Tâche Codex 414 : les rouges nouveaux de la suite 4539dd68

La suite complète de l'intégration `4539dd68` (3 427 tests, 10 920 s) donne **31 échecs et 5 erreurs** sur 31
méthodes. Toutes sont nouvelles depuis la suite `c562aa21`, dont les rouges ont été traités par les lots 391 à 396 et
403. Liste complète : `C:\Users\msics\donjon\artifacts\suite-4539dd68-echecs.txt` (laptop), avec le journal entier
`suite-4539dd68.log` à côté.

Familles visibles :
- **décisions des PNJ** : `test_reessai_obstacle` (cinq méthodes), `test_dynamique_besoins.TenirTests` (Lucien,
  deux), `test_signalements` (deux), `test_temps_reel.PatienceTests`, `test_recours_prioritaire` (deux),
  `test_gardien_detresse`, `test_empathie_peur` (deux), `test_eau` (fuite vers la galerie), `test_amener_flamme`,
  `test_recours_agenda`, `test_agendas_activation`, `test_planification.MemoireTests` ;
- **échanges** : `test_offre_sensee`, `test_contre_offre`, `test_propositions_redites`, `test_achat_promis_annule`,
  `test_refus_retenus` ;
- **empreintes et coût** : `test_completion_preuves`, `test_etapes_chainees`, `test_gestes_par_noeud`,
  `test_depart_feutre` ;
- `test_mj_restes.FaisabiliteTests.test_meme_nature_grimper_sans_appui`.

Fusions entre les deux suites (`git log --first-parent c562aa21..4539dd68`) : 391, 394, **374 (position crue comme
hypothèse datée, qui change les inspections et les appels)**, 392, 395, 398, 396, 397 (S1f), 401, 400 (S1g), 404 (S1h),
399, 405 (S1i), 381 (A2 passage) et 403. Les lots S1 ont tous des empreintes identiques à leur base : le suspect premier
pour la famille des décisions est le **374**, à vérifier par bissection.

Lis `AGENTS.md`, `docs/etat-dev.md` (court) et les rapports 374, 397, 400, 404, 405, 381 et 403.

## Invariant
**Chaque méthode rouge est attribuée à la fusion qui l'a fait basculer (bissection `--first-parent` entre `c562aa21` et
`4539dd68`, sur ces seuls fichiers de tests). Elle est ensuite corrigée dans le contrat commun si la cause est claire et
locale, ou adaptée seulement si son attente est devenue fausse par un changement voulu et documenté (preuve citée,
assertions de sécurité intactes). Sinon, elle est listée avec la question précise.**

Pour le 374 : une attente fondée sur la position éternelle d'autrui (un PNJ qui « sait » encore où est l'autre après
expiration) est devenue fausse par décision ; une boucle, un réessai par le seul délai ou une décision absurde est un
défaut du 374 à corriger. Commence par vérifier sur l'intégration actuelle (une méthode déjà verte n'est pas à
traiter), puis par la famille des décisions. Si le créneau ne suffit pas, livre les familles traitées et liste le reste
avec sa fusion fautive.

## Vérification
Les fichiers de tests concernés. Pour chaque correctif du moteur, un cas réel et un autre cas après recharge, plus un
banc rapide 4 h sur quatre graines (Relais et scénarios touchés). Pas de suite complète, ni Luna.

## Contraintes
**Poste : le laptop.** Lots en cours : 402 (vérification d'intégration, calcul seul), 412 (A4 dossier de revue), 413
(S1l recherche d'une personne : touche aussi les appels et la consommation du 374, signale tout recouvrement). Pendant
S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite, calculs longs détachés : vérifie qu'ils
vivent avant de rendre la main. La poussée de ta branche vers origin (https://github.com/msicsic/jdr.git, dépôt de
l'utilisateur) est autorisée.

## Livraison
- Branche `codex-suite-4539dd68`, base `integration`, poussée vers origin.
- Rapport d'une page `docs/taches/rapport-codex-414-suite-4539dd68.md` : tableau méthode → fusion fautive → cause →
  correction ou question ; entrée « non fusionnée » de 8 lignes au plus dans `docs/etat-dev.md` (puce « - » qui nomme la
  branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\suite-4539dd68-414\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
