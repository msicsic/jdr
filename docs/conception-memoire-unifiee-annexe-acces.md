# Annexe de mesure S0 — accès et dépendances

Relevé statique du commit `b83f5a59`, 30 octobre 2026. Ce fichier complète
[la conception](conception-memoire-unifiee.md). Aucun moteur ni test exécuté.

Méthode : AST Python (`Subscript`, `get`, `setdefault`, `pop`) dans `donjon/`,
`tests/`, `tools/`, clés littérales de `esprits.CHAMPS`, champs facultatifs des agendas et
registres voisins ; recherche `rg` et lecture des fonctions pour les alias et la sémantique.
Les fonctions ci-dessous sont des **sites d’accès**, pas toutes des lecteurs : installation,
validation et mutation figurent aussi. Les homonymes sont explicités dans la conception.
Un test cité atteste une dépendance de source, jamais son exécution ni une couverture complète.

## 1. Tous les sites de la clé `memoire` dans le moteur

74 expressions dans `donjon/` ; trois concernent le cache des recherches :
`banc_pnj.resume_diagnostic:462` (deux) et `banc_pnj.nuit:533` (une).
Il reste **71 expressions de mémoire narrative, dans 55 fonctions et 17 fichiers**.
Les affectations à un alias sont comptées une fois ici ; leurs lectures et mutations
internes sont décrites en annexe A de la conception.

| Fichier / fonction | Lignes des accès |
|---|---|
| `donjon/banc_pnj.py` · `_executer` | 254, 259, 261, 370 |
| `donjon/banc_pnj.py` · `issue` | 110 |
| `donjon/banc_pnj.py` · `main` | 743 |
| `donjon/banc_pnj.py` · `nuit` | 533, 547 |
| `donjon/banc_pnj.py` · `resume_diagnostic` | 462, 462 |
| `donjon/biens.py` · `prets_reclames` | 656 |
| `donjon/causes.py` · `connues` | 36 |
| `donjon/causes.py` · `recevoir` | 98 |
| `donjon/defense.py` · `approche_vue` | 109, 113 |
| `donjon/defense.py` · `avertir_acces` | 224 |
| `donjon/defense.py` · `interposition` | 169, 176 |
| `donjon/defense.py` · `protection` | 414, 423 |
| `donjon/defense.py` · `souvenirs` | 241 |
| `donjon/deliberation.py` · `_candidats` | 2061 |
| `donjon/deliberation.py` · `_lieux_a_dire` | 1166 |
| `donjon/deliberation.py` · `_plan_prevenir` | 1144 |
| `donjon/deliberation.py` · `alarme` | 1104 |
| `donjon/deliberation.py` · `bruit_a_voir` | 1081 |
| `donjon/deliberation.py` · `choisir` | 2396 |
| `donjon/deliberation.py` · `consommer_indices_recherche` | 621 |
| `donjon/deliberation.py` · `detresses_percues` | 903 |
| `donjon/deliberation.py` · `menager_flamme` | 2532 |
| `donjon/deliberation.py` · `ouvert_par_soi` | 1487 |
| `donjon/deliberation.py` · `promesse_en_cours` | 785, 795 |
| `donjon/deliberation.py` · `tache_payee` | 1572 |
| `donjon/echanges.py` · `affirmer` | 645 |
| `donjon/echanges.py` · `tenu` | 1311 |
| `donjon/esprits.py` · `dernier_son` | 843 |
| `donjon/esprits.py` · `installer` | 189, 192, 202, 212 |
| `donjon/esprits.py` · `memoriser` | 722 |
| `donjon/esprits.py` · `prete` | 1135 |
| `donjon/esprits.py` · `verifier` | 369, 369, 486, 486, 488 |
| `donjon/ouie.py` · `_bruit_inconnu` | 671 |
| `donjon/ouie.py` · `_retenir_seulement` | 647 |
| `donjon/ouie.py` · `couvert` | 631 |
| `donjon/ouie.py` · `parcouru` | 609 |
| `donjon/ouie.py` · `source` | 592 |
| `donjon/paroles.py` · `paroles_retenues` | 458 |
| `donjon/passage.py` · `_demande` | 286 |
| `donjon/passage.py` · `a_pousse` | 536 |
| `donjon/planification.py` · `__init__` | 494 |
| `donjon/planification.py` · `_entrees_communes` | 2256 |
| `donjon/planification.py` · `reagir` | 3959 |
| `donjon/pnj.py` · `_abriter` | 1205 |
| `donjon/pnj.py` · `_chauffer` | 1182 |
| `donjon/pnj.py` · `_executer_effet` | 940, 966 |
| `donjon/pnj.py` · `_temoins_a_l_oreille` | 427 |
| `donjon/recit_pnj.py` · `_noter` | 190 |
| `donjon/rejeu.py` · `_penser` | 153 |
| `donjon/relations.py` · `chance_demande` | 299 |
| `donjon/relations.py` · `souvenir` | 578, 590 |
| `donjon/signes.py` · `percevoir_tous` | 881 |
| `donjon/signes.py` · `retenir_detresses` | 575 |
| `donjon/social.py` · `_nouvelles` | 351 |
| `donjon/social.py` · `_sait` | 480 |
| `donjon/social.py` · `migrer_dits` | 274 |

## 2. Accès aux registres : jeu et outils

Chaque clé du socle est incluse, même si elle reste un état opérationnel hors mémoire.
Les détails de clé, invalidation, validation et remplacement sont dans les tables B/C de la conception.

### `accord_initial`

- `donjon/agendas.py` · `_verifier_reference_temporelle` : 1911, 1946
- `donjon/agendas.py` · `accord_deja_conclu` : 1750, 1751
- `donjon/agendas.py` · `prendre` : 2068
- `donjon/agendas.py` · `promesses_visibles` : 2635
- `donjon/agendas.py` · `verifier_references_temporelles` : 2047

### `agendas`

- `donjon/agendas.py` · `_stock` : 946, 947
- `donjon/agendas.py` · `depart` : 2181
- `donjon/agendas.py` · `devis_observateur` : 708
- `donjon/agendas.py` · `evaluation` : 980

### `agendas_joueur`

- `donjon/agendas.py` · `_stock` : 944
- `donjon/agendas.py` · `evaluation` : 978
- `donjon/agendas.py` · `verifier` : 2367

### `aides_attendues`

- `donjon/agendas.py` · `_amener` : 1604, 1646
- `donjon/agendas.py` · `clore_aides_constatees` : 1673, 1684
- `donjon/agendas.py` · `entrees_recours` : 1043, 1044
- `donjon/agendas.py` · `suivis_delegations` : 1701
- `donjon/echanges.py` · `_retenir_aide` : 1443, 1447
- `donjon/echanges.py` · `retenir_abandon` : 1761
- `donjon/esprits.py` · `verifier` : 528, 529, 535, 540
- `donjon/planification.py` · `__init__` : 483
- `donjon/pnj_propositions.py` · `plan_recours` : 256

### `attentes_bornees`

- `donjon/esprits.py` · `verifier` : 414, 415
- `donjon/planification.py` · `vues_du_choix` : 181, 203
- `donjon/pnj_propositions.py` · `recours` : 469
- `tools/bilan_attente_bornee.py` · `bilan` : 67
- `tools/rejouer_plans_attente.py` · `<module>` : 62

### `attributions`

- `donjon/agendas.py` · `_confies_attendus` : 847
- `donjon/agendas.py` · `_verifier_filiation` : 2278
- `donjon/agendas.py` · `avertir_retrait` : 883
- `donjon/agendas.py` · `avertissements` : 862
- `donjon/agendas.py` · `charge_retiree` : 909
- `donjon/agendas.py` · `choisir_mandataire` : 1339
- `donjon/agendas.py` · `confier` : 784, 828
- `donjon/agendas.py` · `planifier` : 1291
- `donjon/agendas.py` · `retenir_intention` : 128

### `balayage`

- `donjon/combat.py` · `approcher_dos` : 237, 239
- `donjon/esprits.py` · `verifier` : 430
- `donjon/pnj.py` · `_agir` : 2083, 2089

### `besoins`

- `donjon/banc_pnj.py` · `main` : 727
- `donjon/banc_pnj.py` · `nuit` : 541
- `donjon/biens.py` · `restitution_retenue` : 125
- `donjon/biens.py` · `valeur_bien` : 407
- `donjon/caractere.py` · `detresse` : 97
- `donjon/corps.py` · `installer` : 73
- `donjon/corps.py` · `malus` : 146
- `donjon/corps.py` · `valeurs` : 46
- `donjon/defense.py` · `choisir` : 447
- `donjon/deliberation.py` · `_candidats` : 1999, 2084, 2105
- `donjon/deliberation.py` · `_plan_lumiere` : 1467
- `donjon/deliberation.py` · `ajouter_recours` : 2004
- `donjon/deliberation.py` · `appeler_a_l_aide` : 1029, 1032
- `donjon/deliberation.py` · `ecart_securite` : 957
- `donjon/deliberation.py` · `eveiller` : 1654
- `donjon/deliberation.py` · `installer` : 183, 184
- `donjon/deliberation.py` · `peur_du_noir` : 1279
- `donjon/deliberation.py` · `relancer` : 193, 194
- `donjon/deliberation.py` · `seuils` : 76
- `donjon/deliberation.py` · `urgents` : 1600
- `donjon/deliberation.py` · `verifier_profil` : 131
- `donjon/depart.py` · `installer` : 62, 77, 78, 80, 81
- `donjon/echanges.py` · `condition_service` : 755
- `donjon/echanges.py` · `servir` : 1540
- `donjon/esprits.py` · `constater` : 1272
- `donjon/esprits.py` · `installer` : 217
- `donjon/esprits.py` · `verifier` : 389, 390, 525
- `donjon/monde.py` · `contexte` : 464
- `donjon/occasion_protection.py` · `utilite` : 86
- `donjon/planification.py` · `__init__` : 397
- `donjon/planification.py` · `chercher` : 2340, 2373
- `donjon/pnj.py` · `_abriter` : 1196, 1220
- `donjon/pnj.py` · `_chauffer` : 1175, 1186
- `donjon/pnj.py` · `_executer_effet` : 1116
- `donjon/pnj.py` · `_jugement_placement` : 1534
- `donjon/pnj.py` · `_reposer` : 1227
- `donjon/pnj.py` · `desespere` : 1253
- `donjon/recit_pnj.py` · `_noter` : 198
- `donjon/rejeu.py` · `_penser` : 141
- `donjon/services.py` · `conditions_manquantes` : 19
- `donjon/services.py` · `don_utile` : 45
- `donjon/signes.py` · `_de` : 146
- `donjon/signes.py` · `de` : 179
- `donjon/spatial.py` · `etat_signes` : 790
- `donjon/vecu.py` · `solder` : 76, 77, 78
- `donjon/voix.py` · `prudent` : 407
- `tools/audit_nuits.py` · `_releve` : 91
- `tools/banc_parties.py` · `preparer` : 248, 273, 274
- `tools/banc_rester_pres.py` · `integrer` : 65
- `tools/detecter_changements_avis.py` · `_est_accompli` : 131, 133, 140, 143
- `tools/detecter_changements_avis.py` · `relever_entrees` : 221, 224, 348
- `tools/diagnostic_refuge_mouille.py` · `diagnostiquer` : 79
- `tools/diagnostiquer_rester_pres.py` · `resume` : 38
- `tools/evaluation_echeance_371.py` · `analyser` : 324
- `tools/mesure_reflexion_190.py` · `profondeur` : 36
- `tools/mesurer_attente_bornee.py` · `observer` : 33
- `tools/tension_relais.py` · `echantillon` : 132
- `tools/tension_relais.py` · `tirage` : 92
- `tools/test_ecoute_reel.py` · `relais` : 31

### `bilan_signes`

- `donjon/signes.py` · `_bilan_signes` : 693, 695, 701

### `bruits`

- `donjon/appel.py` · `dernier_cri` : 380
- `donjon/appel.py` · `en_attente` : 363
- `donjon/appel.py` · `rompre_attente` : 445, 450
- `donjon/dialogues.py` · `_d_ou` : 196
- `donjon/ecoute.py` · `entendus` : 61
- `donjon/ecoute.py` · `lier` : 135
- `donjon/ecoute.py` · `verifier` : 222
- `donjon/ouie.py` · `_au_joueur` : 453
- `donjon/temps.py` · `installer` : 82

### `compagnie`

- `donjon/deliberation.py` · `ecart_securite` : 962
- `donjon/relations.py` · `partager` : 716, 717
- `donjon/relations.py` · `verifier` : 750, 751
- `donjon/signes.py` · `lire` : 456

### `compagnie_minute`

- `donjon/relations.py` · `partager` : 701, 703
- `donjon/relations.py` · `verifier` : 750

### `confies`

- `donjon/agendas.py` · `_verifier_filiation` : 2287, 2316, 2338, 2341
- `donjon/agendas.py` · `confier` : 797, 818
- `donjon/agendas.py` · `enfants` : 214
- `donjon/agendas.py` · `recevoir_compte` : 414

### `confirme`

- `donjon/agendas.py` · `_verifier_filiation` : 2329, 2330
- `donjon/agendas.py` · `confier` : 801

### `contrat_intention`

- `donjon/agendas.py` · `_clore_datee` : 1792
- `donjon/agendas.py` · `clore_intention` : 136
- `donjon/agendas.py` · `contrat_intention` : 110
- `donjon/agendas.py` · `dernier_contrat_intention` : 144
- `donjon/agendas.py` · `retenir_intention` : 123
- `donjon/agendas.py` · `verifier` : 2404
- `tools/diagnostiquer_rester_pres.py` · `resume` : 34

### `conversation`

- `donjon/mj.py` · `_echanger` : 1216
- `donjon/monde.py` · `_installer_recit` : 172
- `donjon/monde.py` · `memoriser` : 176, 178
- `donjon/narration.py` · `fondement` : 504
- `donjon/paroles.py` · `calculer` : 1180
- `donjon/paroles.py` · `preparer_parole` : 1818
- `tools/comparer_noms.py` · `mondes` : 80
- `tools/test_savoirs_reel.py` · `main` : 51
- `tools/valider_mimo_parties.py` · `ecrire` : 105
- `tools/verifier_websocket_jeu.py` · `ecrire` : 38
- `tools/verifier_websocket_jeu.py` · `parcours` : 79, 80, 83, 102

### `croyances`

- `donjon/agendas.py` · `_actualiser_epreuves` : 591
- `donjon/agendas.py` · `_changer` : 1082
- `donjon/agendas.py` · `_constat_charge` : 390
- `donjon/agendas.py` · `_constater_issues` : 1881
- `donjon/agendas.py` · `_croyances` : 1005
- `donjon/agendas.py` · `_fin_garde` : 2188
- `donjon/agendas.py` · `_personne_disponible_crue` : 1222
- `donjon/agendas.py` · `_presence_connue` : 870
- `donjon/agendas.py` · `_prochain_sous_but` : 1453, 1479, 1541
- `donjon/agendas.py` · `_torts_connus` : 33
- `donjon/agendas.py` · `actualiser` : 1152, 1166
- `donjon/agendas.py` · `choisir_mandataire` : 1340
- `donjon/agendas.py` · `clore_aides_constatees` : 1677
- `donjon/agendas.py` · `devis_observateur` : 681
- `donjon/agendas.py` · `echeance_observee` : 925
- `donjon/agendas.py` · `entrees_recours` : 1036
- `donjon/agendas.py` · `essayables` : 1209
- `donjon/agendas.py` · `proteges` : 2230
- `donjon/agendas.py` · `verifier` : 2446
- `donjon/appel.py` · `rompre_attente` : 460
- `donjon/argent_projet.py` · `obtenir` : 53
- `donjon/biens.py` · `capacites_crues` : 350
- `donjon/biens.py` · `entrees_creance` : 500
- `donjon/biens.py` · `entrees_reemprunt` : 97
- `donjon/biens.py` · `services_proteges` : 863
- `donjon/causes.py` · `connues` : 20
- `donjon/causes.py` · `recevoir` : 83
- `donjon/combat.py` · `force_crue` : 202, 205
- `donjon/defense.py` · `_acces_charge` : 39
- `donjon/defense.py` · `_poste_atteignable` : 57
- `donjon/defense.py` · `auteurs` : 250
- `donjon/defense.py` · `constater_fin` : 295
- `donjon/defense.py` · `etat_cru` : 303
- `donjon/defense.py` · `interposition` : 148
- `donjon/defense.py` · `retenir` : 282
- `donjon/deliberation.py` · `_candidats` : 2056
- `donjon/deliberation.py` · `_connus` : 234
- `donjon/deliberation.py` · `_cru` : 223
- `donjon/deliberation.py` · `_fin_demande` : 1931, 1959
- `donjon/deliberation.py` · `_lieu_cru` : 201
- `donjon/deliberation.py` · `apport_cru` : 1221
- `donjon/deliberation.py` · `consommer_indices_recherche` : 617
- `donjon/deliberation.py` · `indice_recherche` : 686
- `donjon/deliberation.py` · `moyens_crus` : 511
- `donjon/deliberation.py` · `obstacle_patience` : 2575, 2584
- `donjon/deliberation.py` · `promesse_en_cours` : 797
- `donjon/deliberation.py` · `retenir_refus` : 303
- `donjon/deliberation.py` · `satisfaite` : 831
- `donjon/deliberation.py` · `secours` : 1783, 1793
- `donjon/deliberation.py` · `sources_posees_crues` : 1196
- `donjon/eau.py` · `borner` : 160
- `donjon/eau.py` · `eau_crue` : 139
- `donjon/eau.py` · `estimation` : 183
- `donjon/eau.py` · `observer` : 311
- `donjon/echanges.py` · `_remettre_part` : 1015
- `donjon/echanges.py` · `anticiper_valeur` : 390, 391
- `donjon/echanges.py` · `tenu` : 1302
- `donjon/esprits.py` · `_percevoir` : 1458
- `donjon/esprits.py` · `constater_fin_objet` : 1214
- `donjon/esprits.py` · `croire` : 601, 603, 623
- `donjon/esprits.py` · `croyance` : 591
- `donjon/esprits.py` · `installer` : 224
- `donjon/esprits.py` · `percevoir_tous` : 1547
- `donjon/esprits.py` · `prevision` : 683
- `donjon/esprits.py` · `prevision_propre` : 663
- `donjon/esprits.py` · `reviser` : 1119
- `donjon/esprits.py` · `verifier` : 362, 363, 450
- `donjon/noms.py` · `connait` : 168
- `donjon/noms.py` · `nom` : 196
- `donjon/obstacles.py` · `descriptions_crues` : 128
- `donjon/obstacles.py` · `metrique_necessaire` : 172
- `donjon/obstacles.py` · `monde_cru` : 339
- `donjon/occasion_protection.py` · `fin` : 95
- `donjon/occasion_protection.py` · `fonds_crus` : 20
- `donjon/occasion_protection.py` · `occasions` : 59
- `donjon/occasion_protection.py` · `peur_crue` : 12
- `donjon/ouie.py` · `_attribuer` : 540
- `donjon/ouie.py` · `_cru_le_plus_proche` : 528
- `donjon/ouie.py` · `_crus_la` : 480
- `donjon/ouie.py` · `objet_situe` : 504
- `donjon/ouie.py` · `resolu` : 584
- `donjon/paroles.py` · `esprits_interlocuteurs` : 413
- `donjon/planification.py` · `__init__` : 412
- `donjon/planification.py` · `_appeler` : 2112
- `donjon/planification.py` · `_entrees_communes` : 2228
- `donjon/planification.py` · `_vu_avant_la_tache` : 3519
- `donjon/planification.py` · `case` : 986
- `donjon/planification.py` · `embuscade_possible` : 691
- `donjon/planification.py` · `gestes` : 1708
- `donjon/planification.py` · `projeter` : 253, 264, 303, 306
- `donjon/planification.py` · `proximite` : 3394
- `donjon/planification.py` · `reagir` : 3963
- `donjon/pnj.py` · `_case_crue` : 1619
- `donjon/pnj.py` · `_cases_barrees_crues` : 122
- `donjon/pnj.py` · `_verrouillee_crue` : 115
- `donjon/pnj.py` · `croit_present` : 1817
- `donjon/pnj.py` · `oreilles_crues` : 246
- `donjon/pnj.py` · `temoins_crus` : 228
- `donjon/pnj_propositions.py` · `_contreparties` : 60
- `donjon/pnj_propositions.py` · `_entrees_negatives` : 123, 143
- `donjon/pnj_propositions.py` · `devis_intermediaire` : 359, 367
- `donjon/pnj_propositions.py` · `reclamation` : 216, 220
- `donjon/pnj_propositions.py` · `rendre_service` : 445
- `donjon/positions_crues.py` · `repere_contact` : 50
- `donjon/presence.py` · `franchir` : 79
- `donjon/propositions.py` · `verifier` : 222
- `donjon/proximite_vocale.py` · `arrivees` : 16
- `donjon/rejeu.py` · `_penser` : 142
- `donjon/relations.py` · `_appliquer` : 420
- `donjon/relations.py` · `partager` : 713
- `donjon/signes.py` · `actives` : 638
- `donjon/signes.py` · `detresse_retenue` : 528
- `donjon/signes.py` · `lire` : 465, 490
- `donjon/signes.py` · `percevoir_tous` : 880
- `donjon/signes.py` · `retenir_detresses` : 580, 586
- `donjon/social.py` · `_adopter` : 622, 626, 650
- `donjon/social.py` · `_apprendre_lieu` : 672
- `donjon/social.py` · `_constats` : 422
- `donjon/social.py` · `_croit_encore` : 319, 330
- `donjon/social.py` · `_cru_ailleurs` : 458
- `donjon/social.py` · `_nouvelles` : 373
- `donjon/social.py` · `_sait` : 470
- `donjon/social.py` · `installer_faits_initiaux` : 114
- `donjon/social.py` · `migrer_dits` : 280
- `donjon/spatial.py` · `etat_signes` : 791
- `donjon/tenir.py` · `retenus_apres` : 81
- `donjon/tenir.py` · `sorties_crues` : 36
- `donjon/voix.py` · `_vu_ailleurs` : 275
- `donjon/voix.py` · `connaitre` : 325
- `tools/audit_nuits.py` · `_releve` : 75
- `tools/detecter_changements_avis.py` · `_diff_croyances` : 387
- `tools/detecter_changements_avis.py` · `_entrees_utilisees` : 433
- `tools/detecter_changements_avis.py` · `_est_accompli` : 158
- `tools/detecter_changements_avis.py` · `cloturer_services` : 480
- `tools/detecter_changements_avis.py` · `relever_entrees` : 193, 256, 257
- `tools/diagnostiquer_reprises_313.py` · `etat` : 60
- `tools/mesure_saillance_210.py` · `esprit_saillant` : 64
- `tools/tension_relais.py` · `pain_ilse` : 62
- `tools/tension_relais.py` · `reserve_vannes` : 77

### `demande_refusee`

- `donjon/deliberation.py` · `choisir` : 2509
- `donjon/deliberation.py` · `retenir_refus` : 321
- `donjon/pnj_propositions.py` · `devis_intermediaire` : 350
- `donjon/pnj_propositions.py` · `executer` : 580
- `donjon/pnj_propositions.py` · `plan_recours` : 301
- `donjon/pnj_propositions.py` · `recours` : 488
- `donjon/pnj_propositions.py` · `rendre_service` : 416
- `donjon/pnj_propositions.py` · `verifier` : 14

### `derniere_confidence`

- `donjon/esprits.py` · `verifier` : 421, 422
- `donjon/social.py` · `bavarder` : 1029, 1035, 1059

### `detresses_appelees`

- `donjon/deliberation.py` · `appeler_a_l_aide` : 1012
- `donjon/esprits.py` · `verifier` : 524, 525, 526

### `dettes`

- `donjon/biens.py` · `dettes` : 423
- `donjon/biens.py` · `reclamer_dette` : 612
- `donjon/biens.py` · `rembourser` : 439
- `donjon/biens.py` · `solder` : 599
- `donjon/biens.py` · `verifier` : 915
- `donjon/pnj.py` · `_avancer` : 2357
- `tools/audit_nuits.py` · `_final` : 116
- `tools/audit_nuits.py` · `_releve` : 102
- `tools/audit_nuits.py` · `analyser_nuit` : 544
- `tools/banc_parties.py` · `preparer` : 282
- `tools/evaluation_echeance_371.py` · `jouer` : 195

### `donne`

- `donjon/deliberation.py` · `changer_etat` : 473, 477, 482
- `donjon/esprits.py` · `verifier` : 482, 485

### `echange`

- `donjon/esprits.py` · `verifier` : 447
- `donjon/voix.py` · `retenir_echange` : 254, 255

### `emissions_parole`

- `donjon/emissions.py` · `enregistrer` : 78
- `donjon/emissions.py` · `installer` : 44
- `donjon/emissions.py` · `lire` : 33
- `donjon/emissions.py` · `verifier` : 182

### `emotions`

- `donjon/signes.py` · `emotion` : 55
- `donjon/signes.py` · `eprouver` : 71
- `donjon/signes.py` · `verifier` : 858, 859
- `donjon/spatial.py` · `etat_signes` : 790

### `en_vue`

- `donjon/defense.py` · `approche_vue` : 89
- `donjon/esprits.py` · `_percevoir` : 1468, 1469, 1537
- `donjon/esprits.py` · `verifier` : 428, 429
- `donjon/pnj.py` · `tour_d_horizon` : 317, 325

### `engagements`

- `donjon/agendas.py` · `_obligations_datees` : 1763
- `donjon/agendas.py` · `affecter_part` : 2154
- `donjon/agendas.py` · `commencer_service` : 2106
- `donjon/agendas.py` · `contrats` : 2240
- `donjon/agendas.py` · `declares` : 2263
- `donjon/agendas.py` · `echoir` : 2510, 2539
- `donjon/agendas.py` · `en_cours` : 1719
- `donjon/agendas.py` · `installer_contrats` : 2244
- `donjon/agendas.py` · `oublier_personne` : 2173
- `donjon/agendas.py` · `payer_contrat` : 2256
- `donjon/agendas.py` · `prendre` : 2080
- `donjon/agendas.py` · `proposer_contrat` : 2248
- `donjon/agendas.py` · `renouveler` : 2126
- `donjon/agendas.py` · `repondre_contrat` : 2252
- `donjon/agendas.py` · `retirer_proposition` : 2119
- `donjon/agendas.py` · `verifier_references_temporelles` : 2000

### `entendus`

- `donjon/appel.py` · `en_attente` : 361
- `donjon/dialogues.py` · `interlocuteurs` : 171
- `donjon/ecoute.py` · `retenir` : 247
- `donjon/ecoute.py` · `verifier` : 230
- `donjon/monde.py` · `designable` : 344
- `donjon/moteur.py` · `_attendre_reveil` : 868
- `donjon/moteur.py` · `_executer_sequence` : 1081
- `donjon/moteur.py` · `_executer_simple` : 782
- `donjon/paroles.py` · `entendre_repondant` : 1721
- `donjon/passage.py` · `preparer_poussee` : 497
- `donjon/pnj.py` · `_temoins_a_l_oreille` : 412, 417
- `donjon/pnj.py` · `verifier` : 60
- `donjon/rejeu.py` · `_a_l_oreille` : 274, 278
- `donjon/rejeu.py` · `_commencer` : 248
- `tools/audit_nuits.py` · `analyser_nuit` : 529, 531, 533

### `eveil`

- `donjon/agendas.py` · `_clore_datee` : 1798
- `donjon/corps.py` · `verifier` : 271
- `donjon/esprits.py` · `reconsiderer` : 1443
- `donjon/esprits.py` · `verifier` : 423
- `donjon/pnj.py` · `_avancer` : 2310, 2315, 2349, 2393, 2396, 2424
- `donjon/pnj.py` · `_prochain` : 2255, 2257
- `donjon/pnj.py` · `tour_d_horizon` : 317, 325
- `tools/diagnostiquer_reprises_313.py` · `choix` : 93
- `tools/diagnostiquer_reprises_313.py` · `etat` : 67
- `tools/evaluation_echeance_371.py` · `jouer` : 175

### `faits_dits`

- `donjon/esprits.py` · `installer` : 196
- `donjon/esprits.py` · `verifier` : 371, 511, 519
- `donjon/social.py` · `_retenir_audience` : 200
- `donjon/social.py` · `deja_dit` : 149
- `donjon/social.py` · `retenir_dit` : 159
- `donjon/social.py` · `reviser_dits` : 220, 252, 262
- `donjon/social.py` · `transmission_attestee` : 141

### `faits_initiaux`

- `donjon/esprits.py` · `verifier` : 379
- `donjon/social.py` · `_initial` : 131
- `donjon/social.py` · `installer_faits_initiaux` : 103
- `donjon/social.py` · `reviser_dits` : 222

### `faits_vus`

- `donjon/faits_locaux.py` · `preparer_faits` : 548
- `donjon/faits_locaux.py` · `verifier` : 598, 603
- `donjon/monde.py` · `contexte` : 525

### `finances_pnj`

- `donjon/biens.py` · `bourse` : 286
- `donjon/biens.py` · `payer` : 309, 320
- `donjon/dialogues.py` · `disponible` : 241
- `donjon/dialogues.py` · `installer` : 150
- `donjon/dialogues.py` · `payer_remise` : 441
- `donjon/dialogues.py` · `verifier_remise` : 425
- `donjon/monde.py` · `verifier` : 604, 608
- `donjon/moteur.py` · `_appliquer_effet` : 1314
- `donjon/propositions.py` · `payer_terme` : 343
- `tools/test_dialogues_reel.py` · `main` : 55

### `indices_recherche`

- `donjon/deliberation.py` · `_retenir_indice` : 640
- `donjon/deliberation.py` · `moyens_crus` : 539
- `donjon/esprits.py` · `verifier` : 545, 555

### `indices_soupcon`

- `donjon/esprits.py` · `_constater_bien` : 802
- `donjon/esprits.py` · `_percevoir` : 1516
- `donjon/esprits.py` · `_purger_indices_soupcon` : 774
- `donjon/esprits.py` · `_retenir_presence` : 761
- `donjon/esprits.py` · `installer` : 184
- `donjon/esprits.py` · `memoriser` : 729
- `donjon/esprits.py` · `verifier` : 489
- `donjon/relations.py` · `deduire_soupcon` : 499, 507
- `donjon/relations.py` · `reviser_soupcons` : 518, 533
- `donjon/relations.py` · `verifier` : 734, 735

### `intention`

- `donjon/agendas.py` · `_clore_datee` : 1790, 1797
- `donjon/agendas.py` · `charges_suspendues` : 150
- `donjon/agendas.py` · `choisir_mandataire` : 1389
- `donjon/agendas.py` · `clore_intention` : 137
- `donjon/agendas.py` · `contrat_intention` : 111
- `donjon/agendas.py` · `retenir_charges` : 170
- `donjon/agendas.py` · `retenir_intention` : 120
- `donjon/agendas.py` · `verifier` : 2423, 2424
- `donjon/appel.py` · `attendre` : 231, 232
- `donjon/appel.py` · `decider` : 143
- `donjon/appel.py` · `presse_ailleurs` : 117
- `donjon/appel.py` · `raison_de` : 169
- `donjon/appel.py` · `retenu` : 102
- `donjon/banc_pnj.py` · `_executer` : 249
- `donjon/banc_pnj.py` · `main` : 728
- `donjon/banc_pnj.py` · `nuit` : 542
- `donjon/combat.py` · `approcher_dos` : 247
- `donjon/corps.py` · `endormir` : 347
- `donjon/defense.py` · `choisir` : 434
- `donjon/deliberation.py` · `_candidats` : 2083, 2105, 2106
- `donjon/deliberation.py` · `_continuer_progres` : 1731
- `donjon/deliberation.py` · `_plan_abri` : 1396
- `donjon/deliberation.py` · `_plan_attendre` : 744
- `donjon/deliberation.py` · `_plan_lumiere` : 1458
- `donjon/deliberation.py` · `_reprendre_demande` : 1911
- `donjon/deliberation.py` · `_voir_en_cours` : 1064
- `donjon/deliberation.py` · `appeler_a_l_aide` : 1036
- `donjon/deliberation.py` · `cherche` : 702
- `donjon/deliberation.py` · `choisir` : 2200, 2203, 2213, 2223, 2228, 2243, 2248, 2261, 2264, 2267, 2488, 2512
- `donjon/deliberation.py` · `evaluer` : 2285, 2289, 2302
- `donjon/deliberation.py` · `inactivite` : 1627
- `donjon/deliberation.py` · `lumiere_utile` : 1307
- `donjon/deliberation.py` · `menager_flamme` : 2530, 2541, 2544
- `donjon/deliberation.py` · `renoncer` : 2626, 2647
- `donjon/deliberation.py` · `retabli_par_son_plan` : 1750
- `donjon/deliberation.py` · `retenir_refus` : 319
- `donjon/deliberation.py` · `urgents` : 1601
- `donjon/eau.py` · `traversee_sure` : 265
- `donjon/echanges.py` · `condition_service` : 747, 756
- `donjon/echanges.py` · `demander` : 825, 827
- `donjon/echanges.py` · `necessaire` : 662
- `donjon/esprits.py` · `installer` : 229, 230, 231, 234
- `donjon/esprits.py` · `verifier` : 561
- `donjon/harnais.py` · `__call__` : 62
- `donjon/improvisation.py` · `action_persistante` : 79
- `donjon/improvisation.py` · `preparer` : 201, 271
- `donjon/mj.py` · `_appeler` : 1426
- `donjon/ouie.py` · `seuil` : 248
- `donjon/paroles.py` · `engagements_enregistres` : 483, 484
- `donjon/paroles.py` · `esprits_interlocuteurs` : 429
- `donjon/passage.py` · `_patienter` : 587
- `donjon/passage.py` · `faire_place` : 561
- `donjon/passage.py` · `raison_de_rester` : 114
- `donjon/planification.py` · `__init__` : 497
- `donjon/pnj.py` · `_abriter` : 1204
- `donjon/pnj.py` · `_agir` : 1988, 1994, 2004, 2137
- `donjon/pnj.py` · `_avancer` : 2398
- `donjon/pnj.py` · `_chauffer` : 1181
- `donjon/pnj.py` · `_executer_effet` : 937, 963
- `donjon/pnj.py` · `_impasse` : 1766, 1768
- `donjon/pnj.py` · `_interrompre_contact` : 1742
- `donjon/pnj.py` · `_noter_fuite` : 1378
- `donjon/pnj.py` · `_rejoindre_un_proche` : 1587
- `donjon/pnj.py` · `_reposer` : 1227
- `donjon/pnj.py` · `a_pas_feutres` : 1269
- `donjon/pnj.py` · `compter_attente` : 1907, 1910, 1911
- `donjon/pnj.py` · `desespere` : 1253
- `donjon/pnj_propositions.py` · `_entrees_negatives` : 131
- `donjon/pnj_propositions.py` · `executer` : 573, 586
- `donjon/recit_pnj.py` · `_episode` : 219
- `donjon/recit_pnj.py` · `_noter` : 202
- `donjon/rejeu.py` · `_penser` : 138
- `donjon/relations.py` · `partager` : 706
- `donjon/signes.py` · `_de` : 118
- `donjon/signes.py` · `attente_sous_regard` : 906
- `donjon/signes.py` · `de` : 170
- `donjon/signes.py` · `detresse_retenue` : 549
- `donjon/signes.py` · `dissimule` : 86
- `donjon/signes.py` · `guette` : 77
- `donjon/signes.py` · `place` : 831
- `donjon/signes.py` · `regard_a_suivre` : 768
- `donjon/signes.py` · `surveiller` : 809, 821
- `donjon/signes.py` · `verifier` : 862
- `donjon/spatial.py` · `etat_signes` : 790
- `tools/audit_nuits.py` · `_releve` : 70
- `tools/banc_rester_pres.py` · `cible` : 36
- `tools/bilan_saillance_210.py` · `bilan` : 50
- `tools/detecter_changements_avis.py` · `agir_sonde` : 933, 936
- `tools/detecter_changements_avis.py` · `enregistrer_choix` : 579
- `tools/detecter_changements_avis.py` · `menager_sonde` : 962
- `tools/diagnostiquer_garde_337.py` · `choix` : 61, 64
- `tools/diagnostiquer_reprises_313.py` · `etat` : 66
- `tools/diagnostiquer_rester_pres.py` · `observer` : 51
- `tools/diagnostiquer_rester_pres.py` · `resume` : 29
- `tools/evaluation_echeance_371.py` · `analyser` : 325
- `tools/mesure_saillance_210.py` · `choix` : 182
- `tools/mesurer_part_estimee.py` · `releve` : 41
- `tools/rejouer_choix_saillance_210.py` · `main` : 86, 91, 92
- `tools/scenes_saillance_210.py` · `main` : 72
- `tools/tension_relais.py` · `echantillon` : 129
- `tools/valider_cause_330.py` · `choix` : 64
- `tools/valider_reprise_garde_337.py` · `classer` : 54

### `issues_obligations`

- `donjon/agendas.py` · `_clore_datee` : 1776
- `donjon/agendas.py` · `_constater_issues` : 1865
- `donjon/agendas.py` · `accord_deja_conclu` : 1751
- `donjon/agendas.py` · `issues_temporelles` : 1740
- `donjon/agendas.py` · `verifier_references_temporelles` : 2002

### `journal_promesses`

- `donjon/agendas.py` · `_constater_issues` : 1896
- `donjon/agendas.py` · `observer_promesses` : 2582
- `donjon/monde.py` · `contexte` : 459, 460
- `donjon/rendu.py` · `decrire_comptes` : 362

### `lectures`

- `donjon/signes.py` · `_bilan_signes` : 689, 702
- `donjon/signes.py` · `actives` : 636
- `donjon/signes.py` · `lire` : 464, 487
- `tools/calibrer_signes.py` · `classer` : 147

### `libre`

- `donjon/corps.py` · `verifier` : 271
- `donjon/esprits.py` · `verifier` : 420
- `donjon/ouie.py` · `_se_tourner` : 567
- `donjon/passage.py` · `deplacer_personne` : 396
- `donjon/passage.py` · `s_ecarter` : 220
- `donjon/pnj.py` · `_avancer` : 2309, 2457, 2459
- `donjon/pnj.py` · `_prevu` : 2249
- `donjon/pnj.py` · `_prochain` : 2257
- `tools/diagnostiquer_reprises_313.py` · `etat` : 67
- `tools/evaluation_echeance_371.py` · `jouer` : 175

### `mandats_percus`

- `donjon/agendas.py` · `_percus` : 459
- `donjon/agendas.py` · `evaluation` : 982
- `donjon/agendas.py` · `verifier` : 2385

### `manque`

- `donjon/deliberation.py` · `choisir` : 2234
- `donjon/esprits.py` · `verifier` : 425, 426, 427
- `donjon/pnj.py` · `_agir` : 2010
- `donjon/pnj.py` · `_avancer` : 2347, 2423
- `tools/detecter_changements_avis.py` · `choisir_sonde` : 922
- `tools/detecter_changements_avis.py` · `relever_entrees` : 320
- `tools/diagnostiquer_reprises_313.py` · `etat` : 66
- `tools/diagnostiquer_rester_pres.py` · `resume` : 38

### `mesures_signes`

- `donjon/signes.py` · `_compter` : 346
- `donjon/signes.py` · `mesures` : 890

### `noms`

- `donjon/banc_pnj.py` · `_executer` : 360
- `donjon/esprits.py` · `verifier` : 448
- `donjon/noms.py` · `apprendre` : 176
- `donjon/noms.py` · `connait` : 164
- `donjon/voix.py` · `lier` : 242, 244
- `donjon/voix.py` · `verifier_echange` : 262, 263
- `tools/audit_nuits.py` · `analyser_nuit` : 391
- `tools/mesure_reflexion_190.py` · `main` : 151
- `tools/mesure_saillance_210.py` · `nuit` : 219
- `tools/rejouer_choix_saillance_210.py` · `premieres_divergences` : 34

### `noms_connus`

- `donjon/monde.py` · `contexte` : 516
- `donjon/noms.py` · `apprendre` : 176
- `donjon/noms.py` · `connait` : 161
- `donjon/noms.py` · `installer` : 113
- `donjon/noms.py` · `verifier` : 568
- `tools/banc_parties.py` · `jouer` : 317, 321
- `tools/banc_parties.py` · `preparer` : 258, 260

### `observation_joueur`

- `donjon/moteur.py` · `_terminer_etape` : 908
- `donjon/signes.py` · `_de` : 110
- `donjon/signes.py` · `de` : 166
- `donjon/spatial.py` · `etat_signes` : 789

### `observations_joueur`

- `donjon/signes.py` · `lire` : 506, 507

### `occurrences_signes`

- `donjon/signes.py` · `_occurrences` : 378
- `donjon/signes.py` · `regard_a_suivre` : 774

### `offres_mandat_joueur`

- `donjon/agendas.py` · `offres_mandat_joueur` : 243
- `donjon/agendas.py` · `proposer_mandat_joueur` : 255
- `donjon/agendas.py` · `repondre_mandat_joueur` : 270

### `paroles_joueur`

- `donjon/emissions.py` · `installer` : 45

### `paroles_pnj`

- `donjon/emissions.py` · `installer` : 46

### `patience`

- `donjon/deliberation.py` · `choisir` : 2505
- `donjon/deliberation.py` · `renoncer` : 2645
- `donjon/esprits.py` · `verifier` : 424
- `donjon/planification.py` · `_entrees_communes` : 2243
- `donjon/pnj.py` · `commencer_attente` : 1896, 1897
- `donjon/pnj.py` · `compter_attente` : 1905, 1907, 1909, 1910, 1911
- `donjon/signes.py` · `guette` : 78
- `donjon/spatial.py` · `etat_signes` : 790

### `permissions`

- `donjon/agendas.py` · `echoir` : 2556
- `donjon/biens.py` · `clore` : 77
- `donjon/biens.py` · `donner` : 140
- `donjon/biens.py` · `permis` : 181
- `donjon/biens.py` · `preter` : 64
- `donjon/biens.py` · `prets` : 51
- `donjon/biens.py` · `verifier` : 910
- `donjon/echanges.py` · `remettre` : 1488, 1505
- `donjon/moteur.py` · `_appliquer_effet` : 1266
- `donjon/paroles.py` · `_demander` : 1568
- `donjon/pnj.py` · `_avancer` : 2360
- `donjon/pnj_propositions.py` · `_entrees_negatives` : 133
- `tools/audit_nuits.py` · `_final` : 116

### `personnages_vus`

- `donjon/monde.py` · `designable` : 343
- `donjon/monde.py` · `identifier` : 194
- `donjon/noms.py` · `nom` : 192
- `donjon/noms.py` · `resoudre` : 211
- `donjon/voix.py` · `designation` : 438

### `personnes`

- `donjon/accords_publics.py` · `accords_publics` : 35
- `donjon/corps.py` · `mourir` : 429
- `donjon/noms.py` · `designation` : 183
- `donjon/noms.py` · `installer` : 114
- `donjon/noms.py` · `nom` : 199
- `donjon/noms.py` · `resoudre` : 210
- `donjon/noms.py` · `verifier` : 571
- `tools/comparer_noms.py` · `mondes` : 73

### `portages`

- `donjon/agendas.py` · `_torts_connus` : 32
- `donjon/esprits.py` · `_constater_bien` : 826
- `donjon/relations.py` · `oublier_portage` : 109
- `donjon/relations.py` · `portage_connu` : 115
- `donjon/relations.py` · `souvenir` : 631
- `donjon/relations.py` · `verifier` : 748, 749

### `presence_recherche`

- `donjon/deliberation.py` · `_situer_recherche` : 669, 673
- `donjon/esprits.py` · `verifier` : 556, 560

### `preuves_relations`

- `donjon/relations.py` · `_appliquer` : 426
- `donjon/relations.py` · `eprouver_mandat` : 243
- `donjon/relations.py` · `portage_connu` : 117
- `donjon/relations.py` · `souvenir` : 660
- `donjon/relations.py` · `verifier` : 745, 747

### `promesses_joueur`

- `donjon/agendas.py` · `_obligations_datees` : 1762
- `donjon/agendas.py` · `constater_geste_joueur` : 2606
- `donjon/agendas.py` · `en_cours` : 1719
- `donjon/agendas.py` · `oublier_personne` : 2176
- `donjon/agendas.py` · `prendre` : 2080
- `donjon/agendas.py` · `renouveler` : 2126
- `donjon/agendas.py` · `retirer_proposition` : 2119
- `donjon/agendas.py` · `verifier_references_temporelles` : 1999

### `pulsions`

- `donjon/agendas.py` · `clore_aides_constatees` : 1685
- `donjon/agendas.py` · `suivis_delegations` : 1703
- `donjon/banc_pnj.py` · `_usurpations` : 125
- `donjon/biens.py` · `gardes` : 164
- `donjon/deliberation.py` · `_candidats` : 2025, 2092, 2094, 2114
- `donjon/deliberation.py` · `appeler_a_l_aide` : 1015, 1017
- `donjon/deliberation.py` · `charges_gardees` : 1505
- `donjon/deliberation.py` · `confie_a_autrui` : 1683
- `donjon/deliberation.py` · `constater_pulsions` : 2134, 2135, 2142
- `donjon/deliberation.py` · `de_garde` : 1054
- `donjon/deliberation.py` · `garde_sous_cle` : 1492
- `donjon/deliberation.py` · `inactivite` : 1632, 1635
- `donjon/deliberation.py` · `installer` : 185, 187
- `donjon/deliberation.py` · `verifier_profil` : 136
- `donjon/depart.py` · `installer` : 84
- `donjon/echanges.py` · `evaluer_proposition` : 272
- `donjon/echanges.py` · `necessaire` : 671
- `donjon/esprits.py` · `verifier` : 392, 393
- `donjon/planification.py` · `retablir` : 3205
- `donjon/planification.py` · `suspensions` : 3157
- `donjon/pnj.py` · `_inspecter` : 586
- `donjon/pnj_propositions.py` · `_entrees_negatives` : 131
- `donjon/services.py` · `conditions_manquantes` : 15
- `tools/audit_nuits.py` · `_final` : 121
- `tools/banc_parties.py` · `preparer` : 251
- `tools/detecter_changements_avis.py` · `relever_entrees` : 235
- `tools/mesurer_part_estimee.py` · `releve` : 42

### `recherches`

- `donjon/appel.py` · `tenir` : 568
- `donjon/banc_pnj.py` · `resume_diagnostic` : 460
- `donjon/deliberation.py` · `appels_vains` : 604
- `donjon/deliberation.py` · `contact_recherche` : 658
- `donjon/deliberation.py` · `indice_recherche` : 683
- `donjon/deliberation.py` · `recherche_vaine` : 609
- `donjon/echanges.py` · `enqueter` : 1173
- `donjon/esprits.py` · `croire` : 632
- `donjon/esprits.py` · `installer` : 204, 208
- `donjon/esprits.py` · `verifier` : 541, 542, 544
- `donjon/planification.py` · `_entrees_communes` : 2252
- `tools/bilan_allers_utiles.py` · `bilan` : 17, 30
- `tools/bilan_attente_bornee.py` · `bilan` : 53
- `tools/bilan_attente_bornee.py` · `diagnostic` : 15
- `tools/bilan_completion_preuves.py` · `main` : 11, 12
- `tools/bilan_profil_98.py` · `main` : 74, 83
- `tools/bilan_recherche_109.py` · `main` : 60, 64, 67
- `tools/bilan_recherche_109.py` · `trace` : 86
- `tools/bilan_reflexion_190.py` · `bilan` : 35
- `tools/bilan_saillance_210.py` · `bilan` : 54
- `tools/bilan_sous_arbres.py` · `main` : 17, 18, 19, 21, 30, 33
- `tools/detecter_changements_avis.py` · `relever_entrees` : 289
- `tools/empreintes_nuits.py` · `nuit` : 113
- `tools/mesure_reflexion_190.py` · `main` : 157
- `tools/mesurer_attente_bornee.py` · `mesurer_cout` : 120
- `tools/mesurer_bissection_auberge.py` · `mesurer` : 69, 76
- `tools/mesurer_completion_preuves.py` · `main` : 89, 91, 105
- `tools/profil_compare_98.py` · `main` : 75
- `tools/rejouer_plans_attente.py` · `<module>` : 48

### `recours_intermediaires`

- `donjon/agendas.py` · `affecter_part` : 2159
- `donjon/agendas.py` · `tenir` : 2139
- `donjon/banc_pnj.py` · `_executer` : 265
- `donjon/echanges.py` · `executer` : 1961
- `donjon/pnj_propositions.py` · `devis_intermediaire` : 357
- `donjon/pnj_propositions.py` · `plan_recours` : 255, 297
- `donjon/pnj_propositions.py` · `verifier` : 15, 19

### `recours_propositions`

- `donjon/pnj_propositions.py` · `executer` : 577, 579
- `donjon/pnj_propositions.py` · `recours` : 519
- `donjon/pnj_propositions.py` · `verifier` : 27, 31

### `recours_services`

- `donjon/pnj_propositions.py` · `plan_recours` : 279, 296
- `donjon/pnj_propositions.py` · `rendre_service` : 430, 432, 434
- `donjon/pnj_propositions.py` · `verifier` : 23, 26

### `reference_temporelle`

- `donjon/agendas.py` · `prendre` : 2071, 2076
- `donjon/agendas.py` · `reference_temporelle` : 1735

### `references_personnes`

- `donjon/noms.py` · `installer` : 115
- `donjon/noms.py` · `reference` : 347
- `donjon/noms.py` · `verifier` : 576
- `donjon/voix.py` · `reel` : 474

### `refus`

- `donjon/agendas.py` · `_croyances` : 1011
- `donjon/agendas.py` · `entrees_recours` : 1042
- `donjon/causes.py` · `demander` : 139
- `donjon/deliberation.py` · `contrarie` : 493
- `donjon/deliberation.py` · `oublier_refus` : 328
- `donjon/deliberation.py` · `refus_geste` : 350
- `donjon/deliberation.py` · `refus_retenu` : 337
- `donjon/deliberation.py` · `retenir_refus` : 281, 318
- `donjon/echanges.py` · `offre_retenue` : 794
- `donjon/echanges.py` · `servir` : 1544
- `donjon/esprits.py` · `croire` : 611
- `donjon/esprits.py` · `verifier` : 455, 479
- `donjon/planification.py` · `juger` : 739
- `donjon/planification.py` · `projeter` : 308
- `donjon/planification.py` · `s_enquerir` : 3739, 3750
- `donjon/pnj_propositions.py` · `_entrees_negatives` : 128
- `donjon/pnj_propositions.py` · `offre_refusee` : 207
- `donjon/pnj_propositions.py` · `plan_recours` : 303
- `donjon/pnj_propositions.py` · `recours` : 520
- `donjon/propositions.py` · `taches_crues` : 308
- `donjon/relations.py` · `chance_demande` : 294
- `donjon/services.py` · `lever_refus` : 115
- `tools/banc_multi.py` · `mesurer` : 58, 66, 106
- `tools/banc_parties.py` · `resumer` : 357
- `tools/detecter_changements_avis.py` · `_est_accompli` : 181
- `tools/detecter_changements_avis.py` · `relever_entrees` : 273
- `tools/diagnostic_refuge_mouille.py` · `diagnostiquer` : 76
- `tools/oracle_g1.py` · `classer` : 100, 103
- `tools/oracle_g1.py` · `observation` : 54
- `tools/oracle_g1.py` · `rapport` : 155, 170
- `tools/rapport_fil.py` · `rendre` : 122
- `tools/valider_mandat_joueur_341.py` · `analyser_luna` : 59

### `regards_suivis`

- `donjon/esprits.py` · `verifier` : 434
- `donjon/signes.py` · `regard_a_suivre` : 782
- `donjon/signes.py` · `suivre_regard` : 795
- `tools/banc_attention_conjointe.py` · `main` : 87

### `rejoindre`

- `donjon/appel.py` · `plan_venir` : 603
- `donjon/appel.py` · `retenu` : 106
- `donjon/appel.py` · `rompre_attente` : 456
- `donjon/appel.py` · `tenir` : 535, 557, 561, 569
- `donjon/appel.py` · `venir` : 242
- `donjon/appel.py` · `verifier` : 619
- `donjon/deliberation.py` · `_attendre_qui_vient` : 764
- `donjon/deliberation.py` · `_candidats` : 2064

### `rejoint`

- `donjon/appel.py` · `attendre` : 227, 229
- `donjon/appel.py` · `decider` : 151
- `donjon/appel.py` · `dire` : 277, 278
- `donjon/appel.py` · `retenu` : 105
- `donjon/appel.py` · `rompre_attente` : 434, 437, 457
- `donjon/appel.py` · `tenir` : 530, 532, 547
- `donjon/appel.py` · `verifier` : 619
- `donjon/deliberation.py` · `_attendre_qui_vient` : 755, 769
- `donjon/deliberation.py` · `_candidats` : 2069
- `donjon/deliberation.py` · `_plan_attendre` : 743
- `donjon/ouie.py` · `entendre` : 745
- `donjon/social.py` · `_concerne` : 416
- `tools/audit_nuits.py` · `_final` : 118
- `tools/audit_nuits.py` · `_releve` : 99
- `tools/detecter_changements_avis.py` · `relever_entrees` : 299

### `relations`

- `donjon/agendas.py` · `_croyances` : 1011
- `donjon/agendas.py` · `entrees_recours` : 1042
- `donjon/faits_locaux.py` · `preparer_faits` : 497, 500
- `donjon/relations.py` · `_appliquer` : 419, 478
- `donjon/relations.py` · `_lecture` : 162
- `donjon/relations.py` · `_lecture_pure` : 147
- `donjon/relations.py` · `connus` : 99
- `donjon/relations.py` · `doit` : 399
- `donjon/relations.py` · `installer` : 93
- `donjon/relations.py` · `se_fie` : 383
- `donjon/relations.py` · `se_mefie` : 377
- `donjon/relations.py` · `signature` : 322
- `donjon/relations.py` · `signature_signes` : 184
- `donjon/relations.py` · `verifier` : 764
- `tools/banc_parties.py` · `preparer` : 277, 280

### `renoncements`

- `donjon/deliberation.py` · `choisir` : 2270, 2464, 2468
- `donjon/deliberation.py` · `evaluer` : 2303
- `donjon/deliberation.py` · `renoncer` : 2633, 2644
- `donjon/esprits.py` · `verifier` : 396, 413
- `donjon/pnj.py` · `refus_etape` : 1928
- `tools/audit_nuits.py` · `_final` : 119
- `tools/audit_nuits.py` · `_releve` : 95
- `tools/detecter_changements_avis.py` · `enregistrer_choix` : 623
- `tools/diagnostic_refuge_mouille.py` · `diagnostiquer` : 75
- `tools/diagnostiquer_reprises_313.py` · `etat` : 65

### `restitutions`

- `donjon/biens.py` · `restitution_retenue` : 121
- `donjon/biens.py` · `retenir_restitution` : 111
- `donjon/biens.py` · `verifier` : 898
- `donjon/planification.py` · `_entrees_communes` : 2273

### `secours`

- `donjon/deliberation.py` · `appeler_a_l_aide` : 1023, 1041
- `donjon/esprits.py` · `installer` : 211, 215
- `donjon/esprits.py` · `verifier` : 520, 521, 522

### `sequence_obligations`

- `donjon/agendas.py` · `_obligations_datees` : 1760
- `donjon/agendas.py` · `prendre` : 2075, 2079
- `donjon/agendas.py` · `verifier_references_temporelles` : 1995

### `service_en_cours`

- `donjon/pnj_propositions.py` · `plan_recours` : 264, 270, 275, 279, 286, 296
- `donjon/pnj_propositions.py` · `rendre_service` : 439
- `donjon/pnj_propositions.py` · `verifier` : 20, 21, 22

### `services_rendus`

- `donjon/biens.py` · `clotures_services_du_choix` : 816
- `donjon/biens.py` · `retenir_service` : 790
- `donjon/biens.py` · `services_proteges` : 841
- `donjon/biens.py` · `verifier` : 887, 888
- `donjon/pnj_propositions.py` · `_entrees_negatives` : 136
- `tools/detecter_changements_avis.py` · `cloturer_services` : 469
- `tools/detecter_changements_avis.py` · `clotures_sondees` : 860
- `tools/detecter_changements_avis.py` · `presence_service` : 513

### `signes_lus`

- `donjon/signes.py` · `lire` : 434

### `signes_lus_joueur`

- `donjon/signes.py` · `lire` : 434

### `souvenirs`

- `donjon/carte.py` · `_carte_cases` : 255
- `tools/audit_nuits.py` · `analyser_nuit` : 418
- `tools/detecter_changements_avis.py` · `jouer_nuit_sondee` : 1017
- `tools/empreintes_nuits.py` · `nuit` : 122

### `souvenirs_personnages`

- `donjon/enrichissement.py` · `catalogue` : 40
- `donjon/enrichissement.py` · `preparer_complements` : 115
- `donjon/monde.py` · `_installer_personnages` : 181
- `donjon/monde.py` · `actualiser_souvenirs_personnages` : 218
- `donjon/monde.py` · `contexte` : 514
- `donjon/projection_publique.py` · `projeter` : 148

### `souvenirs_portes`

- `donjon/scene.py` · `scene_percue` : 146
- `donjon/spatial.py` · `_memoriser` : 1196
- `donjon/spatial.py` · `verifier` : 1558

### `souvenirs_visuels`

- `donjon/couverture_action.py` · `_passages` : 181
- `donjon/localisation.py` · `phrases_positions` : 132
- `donjon/monde.py` · `contexte` : 474
- `donjon/monde.py` · `designable` : 342
- `donjon/narration.py` · `reperes_orientation` : 683
- `donjon/noms.py` · `references_fournies` : 423
- `donjon/paroles.py` · `_connu_du_joueur` : 1116
- `donjon/projection_publique.py` · `projeter` : 139, 150
- `donjon/rendu.py` · `non_perception` : 213
- `donjon/scene.py` · `scene_percue` : 152
- `donjon/spatial.py` · `_memoriser` : 1182
- `donjon/spatial.py` · `verifier` : 1536
- `donjon/tenir.py` · `retenus_apres` : 78

### `suites`

- `donjon/relations.py` · `annoncer_suites` : 684, 686
- `donjon/relations.py` · `souvenir` : 584
- `donjon/relations.py` · `verifier` : 752, 756
- `tools/bilan_allers_utiles.py` · `bilan` : 53
- `tools/bilan_recherche_109.py` · `resumer` : 17
- `tools/mesurer_allers_utiles.py` · `suites` : 88, 90
- `tools/recherche_tiree_109.py` · `normaliser` : 55

### `suivi_signes`

- `donjon/signes.py` · `_suivi` : 401

### `tirages_lecture`

- `donjon/signes.py` · `_jet` : 354
- `donjon/signes.py` · `verifier` : 855

### `tirages_lecture_acteurs`

- `donjon/signes.py` · `_jet` : 351

### `tons_percus`

- `donjon/signes.py` · `entendre_ton` : 924
- `donjon/signes.py` · `publics` : 339
- `donjon/spatial.py` · `etat_signes` : 789

### `urgences`

- `donjon/deliberation.py` · `_classer` : 1667
- `donjon/deliberation.py` · `_etat_urgence` : 1585
- `donjon/deliberation.py` · `eveiller` : 1652
- `donjon/esprits.py` · `verifier` : 419
- `tools/audit_nuits.py` · `_final` : 120

### `veille`

- `donjon/corps.py` · `depart` : 53
- `donjon/corps.py` · `verifier` : 271
- `donjon/esprits.py` · `verifier` : 423
- `donjon/pnj.py` · `_avancer` : 2308, 2384, 2457
- `donjon/pnj.py` · `_prevu` : 2249
- `donjon/pnj.py` · `_prochain` : 2255, 2257
- `tools/evaluation_echeance_371.py` · `jouer` : 175

### `violences_joueur`

- `donjon/defense.py` · `noter_coup` : 348
- `donjon/defense.py` · `souvenirs` : 241

### `visites`

- `donjon/agendas.py` · `_amener` : 1652
- `donjon/agendas.py` · `suivis_delegations` : 1710
- `donjon/appel.py` · `tenir` : 567
- `donjon/deliberation.py` · `bruit_a_voir` : 1085
- `donjon/deliberation.py` · `satisfaite` : 826
- `donjon/depart.py` · `installer` : 62, 95, 99, 100
- `donjon/esprits.py` · `verifier` : 439
- `donjon/planification.py` · `_chercher` : 2153
- `donjon/planification.py` · `_confier_tache` : 1751
- `donjon/planification.py` · `_entrees_communes` : 2260
- `donjon/pnj.py` · `_inspecter` : 569
- `tools/banc_parties.py` · `preparer` : 253
- `tools/completion_preuves.py` · `parcours` : 36, 39
- `tools/detecter_changements_avis.py` · `relever_entrees` : 323

### `voix`

- `donjon/banc_pnj.py` · `_executer` : 226, 355
- `donjon/ecoute.py` · `_rendre` : 206
- `donjon/esprits.py` · `installer` : 224
- `donjon/esprits.py` · `verifier` : 442, 443, 444
- `donjon/proximite_vocale.py` · `arrivees` : 32
- `donjon/proximite_vocale.py` · `entrees` : 43
- `donjon/relations.py` · `_appliquer` : 419
- `donjon/voix.py` · `_connues` : 58
- `donjon/voix.py` · `connaitre` : 311

### `voix_connues`

- `donjon/ecoute.py` · `verifier` : 233
- `donjon/esprits.py` · `installer` : 245
- `donjon/voix.py` · `_connues` : 58
- `donjon/voix.py` · `connaitre` : 311

### `voix_entendues`

- `donjon/banc_pnj.py` · `_executer` : 357, 359
- `donjon/ecoute.py` · `verifier` : 237
- `donjon/esprits.py` · `installer` : 246
- `donjon/esprits.py` · `verifier` : 446
- `donjon/noms.py` · `_appellations_voix` : 296
- `donjon/voix.py` · `designation` : 445
- `donjon/voix.py` · `entendues` : 64, 65
- `donjon/voix.py` · `nom_pour_joueur` : 506
- `donjon/voix.py` · `porteur_du_nom` : 455
- `donjon/voix.py` · `reel` : 485

## 3. Tests qui accèdent explicitement à la mémoire

247 expressions, réparties dans **106 fichiers** (support compris). Les scénarios
et tests fonctionnels indirects à relancer par famille sont indiqués dans la conception.

| Fichier | Méthodes et lignes |
|---|---|
| `tests/support.py` | `sans_indices_soupcon_passifs` (67) |
| `tests/test_agendas_compte_rendu.py` | `test_doute_attribution_et_idempotence` (197) ; `test_mensonge_sans_effet_sur_le_monde_et_dementi_posterieur` (141) |
| `tests/test_agendas_evenement.py` | `test_deux_victimes_sur_preuve_persistante` (55) |
| `tests/test_agendas_fins.py` | `test_fin_datee_persiste_hors_memoire_et_apres_retrait_des_restes` (123) |
| `tests/test_agendas_naissance.py` | `test_naissance_independante_du_registre_de_souvenirs` (108) |
| `tests/test_agendas_pieces.py` | `test_deux_debiteurs_vendent_avant_une_faute` (67) |
| `tests/test_agendas_proteger.py` | `test_interposition_reelle_de_deux_protecteurs_sur_agenda_seul` (50) |
| `tests/test_agendas_socle.py` | `test_relais_part_promise_puis_tenue` (113) ; `test_tache_payee_acceptee_puis_abandonnee` (151) |
| `tests/test_agendas_transferts.py` | `test_preuve_hors_memoire_et_pas_de_double_prix` (193) |
| `tests/test_appel_negocie.py` | `test_cas_reel_hugues_previent_anselme_qui_vient` (159) ; `test_qui_avait_promis_et_ne_vient_pas_rompt_sa_parole` (319) ; `test_qui_guette_un_geste_sans_temoin_ne_se_signale_pas` (346) |
| `tests/test_appels_restes.py` | `test_bruit_reexplique_ne_recommence_pas_la_tournee` (98, 104) ; `test_retour_positivement_appris_vers_un_ancien_lieu_ou_une_ancienne_case` (26) |
| `tests/test_audience.py` | `test_achats_differes_acceptes_et_livres_apres_la_saisie_libre` (291) |
| `tests/test_avis_joueur.py` | `test_contradiction_temoins_et_pas_de_parole_inventee_du_joueur` (77) ; `test_deux_lieux_deux_auditeurs_et_conviction_devinee` (50) ; `test_trois_saisies_du_banc_reception_et_faits_recharges` (184) |
| `tests/test_avis_menace.py` | `test_avis_une_fois_meme_apres_oubli_et_nouveaux_reperes` (144) |
| `tests/test_avis_parles.py` | `test_avis_contraire_dispute_sans_replique_supplementaire` (91) |
| `tests/test_banc_pnj.py` | `derouler` (28) |
| `tests/test_besoins.py` | `test_crochets_disparus_elle_replanifie_et_reste_sans_plan` (113) ; `test_gorm_dans_l_ombre_la_voit_et_garde_sa_reserve` (159) ; `test_sous_les_yeux_du_joueur_elle_attend_puis_renonce` (91) |
| `tests/test_caractere.py` | `test_memes_moyens_valeurs_differentes` (153) |
| `tests/test_ceder_outil.py` | `test_cession_compensee_et_laps_decoupe` (140) ; `test_gaspard_marche_reel_refus_puis_doublon_ou_desespoir` (210) |
| `tests/test_combat.py` | `test_assommer_pour_prendre_cas_reel_et_autre_porteur_apres_recharge` (336) ; `test_assommer_surprise_et_identite_inconnue_apres_reveil_de_deux_victimes` (68, 73) ; `test_coup_vu_victime_et_temoin_se_mefient_apres_recharge` (86, 90, 91) ; `test_victime_frappee_par_surprise_montre_un_signe_de_peur` (169) |
| `tests/test_constater_rumeurs.py` | `test_hugues_voit_lucien_poser_le_ballot_et_anselme_va_le_reprendre` (141) ; `test_ilse_dit_a_gorm_ou_brune_a_pose_ses_vivres` (180) |
| `tests/test_constater_soupcon.py` | `scene` (34) ; `test_registre_borne_sans_eviction_des_souvenirs_communs` (264, 268, 272) ; `test_registre_passif_ne_change_pas_les_entrees_de_recherche` (325, 330) |
| `tests/test_contact_position_inconnue.py` | `test_contact_perdu_est_observe_avant_interruption` (230) |
| `tests/test_contact_sous_but.py` | `test_enquete_autonome_auberge_et_reponse_enregistree` (85) |
| `tests/test_contrat_engagement.py` | `test_autre_secours_froid_hors_vue_et_accomplissement` (263) |
| `tests/test_contre_offre.py` | `test_service_necessaire_condition_et_pret_apres_recharge` (88) ; `test_service_poursuivi_par_pnj_meme_laps_decoupe` (189) |
| `tests/test_contreparties.py` | `test_auberge_bien_indivisible_trop_cher_pas_offert_ni_affiche` (88) ; `test_capture_mine_253_plan_ancien_et_nouveau_recours` (52) ; `test_somme_utile_financee_livree_sans_ceder_la_bourse` (124) |
| `tests/test_corps.py` | `test_venue_convenue_ne_vaut_pas_presence_ni_part_deja_servie` (183) |
| `tests/test_corps_blessable.py` | `test_depouille_et_biens_et_decouverte_apres_recharge` (222) ; `test_inconscient_ne_percoit_entend_parle_ni_laisse_passer` (114) ; `test_protecteur_ranime_ilse_et_un_autre_protege` (159) |
| `tests/test_defense.py` | `test_aucun_nom_d_agresseur_apres_surprise_ou_cri_inconnu` (85) ; `test_un_cri_de_protege_inquiete_une_fois_et_se_retient_une_fois` (344, 347) ; `test_un_temoin_de_l_effraction_ne_la_fuit_pas` (418) |
| `tests/test_deja_dit.py` | `test_capture_mine3_episode_relu_et_souvenirs_sortis_ne_se_redisent_pas` (39) |
| `tests/test_deliberation_evenements.py` | `test_un_geste_illicite_sous_ses_yeux_le_fait_choisir_aussitot` (225) ; `test_un_voleur_qui_entre_dans_son_regard_le_fait_choisir_aussitot` (202) |
| `tests/test_demander_cause.py` | `test_bruit_inconnu_temoins_et_constat_plus_fort` (228) |
| `tests/test_disputes.py` | `test_deux_paires_lieux_paroles_et_suites_apres_recharge` (119, 128, 133) ; `test_eclat_voisin_et_aller_voir_par_la_regle_commune` (70) ; `test_egalite_departagee_et_constat_propre_preserve` (92) |
| `tests/test_don.py` | `test_donner_la_cloche_a_gorm_sans_mission` (36) |
| `tests/test_echanges_argent.py` | `memoires` (29) ; `test_l_affamee_qui_a_de_quoi_payer_achete_au_lieu_de_forcer_la_reserve` (194) ; `test_la_lampe_pretee_s_allume_sans_faute_puis_revient_a_gaspard` (67) |
| `tests/test_echanges_suite.py` | `memoires` (29) ; `test_mireille_paie_qui_veut_bien_entretenir_le_fourneau` (285, 287) |
| `tests/test_echelle_choix.py` | `anciens_candidats` (74) |
| `tests/test_elision.py` | `test_nouvelle_sur_une_personne_designee_entendue_et_rechargee` (92) |
| `tests/test_empathie.py` | `test_credit_du_froid_sans_charge_joueur_et_pnj_sans_double` (89) ; `test_credit_froid_exige_manque_local_et_effet_constate` (123) ; `test_feu_convenu_pas_de_second_credit_du_froid` (138, 140) |
| `tests/test_empathie_peur.py` | `test_ilse_et_mine_rejoint_reste_apaise_et_meme_laps` (302) |
| `tests/test_enfermer.py` | `test_assommer_trainer_verrouiller_temoin_reveil_et_decoupage` (152) ; `test_auteur_croit_victime_sans_la_reveler_a_la_victime` (67, 70, 71) |
| `tests/test_engagement_deplacement.py` | `test_gorm_confie_deux_marches_et_pas_un_transport` (79) |
| `tests/test_entretenir.py` | `test_la_cuisiniere_demande_au_palefrenier_du_bois_pour_son_fourneau` (76) ; `test_sans_bois_il_demande_les_buches_de_gaspard` (127) |
| `tests/test_esprits.py` | `test_croyance_perimee_jusqu_a_ce_qu_il_revoie_la_place` (135, 136) ; `test_vol_surpris_memorise_apres_rechargement` (174) |
| `tests/test_etapes_chainees.py` | `test_memoire_isole_les_mutations_profondes_des_deux_appelants` (329) |
| `tests/test_garde_ouidire.py` | `garde` (62) ; `test_nouvelle_doutee_ne_termine_pas_la_garde` (222) |
| `tests/test_garde_pret.py` | `test_un_temoin_non_remarque_n_est_appris_qu_en_le_voyant` (249) |
| `tests/test_installation_gardee.py` | `test_autre_contenant_et_temoins_joueur_et_pnj` (169) ; `test_joueur_frappe_et_temoin_reagit_par_le_moteur` (109) |
| `tests/test_interposition.py` | `test_deux_gardiens_poste_parole_persistance_et_rendu_recharges` (76) ; `test_epreuve_anselme_ballot_en_donnees` (149) |
| `tests/test_interposition_lieu.py` | `epreuve` (34) ; `test_acces_occupe_ou_obstacle_cru_ne_declenche_rien` (173) ; `test_approche_non_vue_ou_personne_sure` (148, 151) ; `test_deux_scenarios_poste_parole_persistance_et_recharge` (110) ; `test_gardien_dedans_rejoint_le_seuil_par_la_marche` (191) ; `test_guet_lu_et_garde_endormie` (162) |
| `tests/test_lampes_parts.py` | `parcours` (166) |
| `tests/test_livraison_inconnue.py` | `chaine` (83, 85) ; `test_aucun_moyen_admissible_le_temps_ne_rouvre_pas_la_recherche` (174) ; `test_depart_cru_annule_encore_meme_si_le_destinataire_est_reellement_present` (138) |
| `tests/test_lumiere.py` | `test_une_heure_dans_le_noir_ou_chaque_resultat_repris_ou_borne_est_recalcule` (251) |
| `tests/test_lumiere_garde.py` | `test_l_attente_d_une_part_se_compte_la_ou_elle_se_sert` (268, 270) ; `test_remy_cherche_gaspard_et_lui_demande_du_feu` (85) |
| `tests/test_marche.py` | `test_sans_chemin_le_but_ordinaire_patiente_puis_renonce` (192) |
| `tests/test_mine.py` | `test_le_noir_gagne_le_camp_et_les_protecteurs_accourent` (95) |
| `tests/test_noms.py` | `test_une_croyance_rapportee_descriptive_ne_donne_aucun_nom` (155) |
| `tests/test_occasion_protection.py` | `test_auberge_et_relais_offre_autonome_paiement_et_protection` (90) ; `test_refus_retenu_sans_rearmement_par_le_delai` (184) |
| `tests/test_offre_sensee.py` | `test_ce_qu_il_garde_et_ce_qui_vaut_plus_ne_se_proposent_pas` (112) ; `test_ilse_cas_reel_et_autre_fourniture_refuses_avant_paiement` (146) |
| `tests/test_ouie.py` | `souvenirs` (40) |
| `tests/test_ouie_commune.py` | `bruit` (28) ; `test_la_cloche_du_relais_sonne_comme_un_appel` (102) ; `test_le_gardien_au_seuil_d_alerte_bas_accourt` (148) |
| `tests/test_ouie_temoins.py` | `test_un_examen_vain_couvre_le_meme_bruit_pas_un_nouveau` (262) |
| `tests/test_parole_commune.py` | `paroles_retenues` (40) ; `test_un_aveu_a_voix_haute_devant_un_temoin` (327, 338, 348) ; `test_une_confidence_surprise_devient_une_rumeur` (378) |
| `tests/test_parole_corrections.py` | `test_cas_reel_c_est_moi_brune` (346) |
| `tests/test_parole_voix.py` | `obtient_sa_part` (240) ; `test_s_il_le_cherche_aussi_il_va_vers_lui` (232) |
| `tests/test_paroles.py` | `test_mensonge_credible_change_son_plan_puis_se_decouvre` (168) ; `test_mots_entre_guillemets_dits_tels_quels` (134) |
| `tests/test_pas_compagnons.py` | `test_aubin_saisit_l_occasion_de_demander_a_gorm_hameau_et_relais` (218) ; `test_bruit_inconnu_ne_devient_pas_presence_identifiee` (268, 269) ; `test_fracas_et_appel_restent_inhabituels` (313) ; `test_hameau_1985_service_admissible_mais_vente_compensee_prioritaire` (181) ; `test_mael_entend_le_refuge_depuis_une_autre_salle` (303) ; `test_promesse_hameau_1985_annoncee_retrouvee_apres_recharge` (120, 131) ; `test_temoin_illicite_reconnait_la_presence_mobile_crue` (410) ; `test_voisins_hors_du_cone_relais_et_autre_cas_auberge` (292) |
| `tests/test_passage.py` | `test_reussie_elle_recule_et_les_temoins_s_en_souviennent` (212) |
| `tests/test_petits_correctifs.py` | `test_la_promesse_expiree_la_dette_est_reclamee` (188, 189) ; `test_les_vivres_epuises_gorm_rend_les_pieces` (168) ; `test_un_temoin_voit_forcer` (302) |
| `tests/test_peur_transmise.py` | `test_un_appel_anonyme_ne_revele_pas_la_detresse_d_un_allie` (182) |
| `tests/test_planif_cout.py` | `test_lucien_garder_le_graphe_repris_rend_la_recherche_complete` (60) |
| `tests/test_planification.py` | `test_meme_situation_meme_resultat_sans_chercher` (170) ; `test_une_nuit_ou_chaque_resultat_repris_ou_borne_est_recalcule` (206) |
| `tests/test_promesse_tenable.py` | `test_capture_reelle_et_autre_presence_impossible_avant_accord` (54) ; `test_promesse_tenable_acceptee_et_tenue_apres_recharge` (96) |
| `tests/test_promesses.py` | `test_un_autre_objet_a_un_autre_personnage` (117) |
| `tests/test_proposer_recours.py` | `test_crue_offre_avant_faute_et_part_acceptee_deux_auditeurs` (118, 128) ; `test_mine_odon_paie_la_contre_offre_apres_refus_et_mathe_livre` (100) ; `test_part_promise_attendue_sans_racheter_ni_voler_avec_garde_active` (61) |
| `tests/test_propositions.py` | `test_accepter_honore_la_dette_de_deux_auditeurs` (69) ; `test_promesse_inscrite_tenue_ou_abandonnee_et_visible` (187) |
| `tests/test_propositions_redites.py` | `test_captures_reelles_meme_laps_decoupe_et_recharge` (69) |
| `tests/test_protection.py` | `test_gorm_voit_brune_prendre_les_planches_d_aubin_et_le_lui_dit` (98) |
| `tests/test_realisation_datee.py` | `test_constat_tardif_ne_change_pas_la_date_d_un_effet_de_tiers` (124) ; `test_expiration_arrete_le_plan_et_ne_previent_pas_un_absent` (152) ; `test_promesse_joueur_datee_constatee_plus_tard_une_seule_fois` (204) |
| `tests/test_reclamations_repetees.py` | `test_deux_scenarios_refus_reel_durable_et_recharge` (171, 176) ; `test_echeance_inconnue_ne_leve_pas_un_refus_sur_une_creance_connue` (93, 98) |
| `tests/test_refus_leve_contrepartie.py` | `test_autre_bien_service_pret_et_rendu_apres_laps_decoupe` (106) |
| `tests/test_refus_retenus.py` | `test_qui_ne_peut_plus_la_faire_la_rend_sans_attendre` (357) |
| `tests/test_relations_graduees.py` | `test_brune_donne_du_bois_puis_previent_gorm` (51) |
| `tests/test_relations_lectures.py` | `test_la_confidence_va_au_plus_aime_puis_a_l_identifiant` (126) ; `test_la_recherche_recalcule_son_cout_quand_la_peur_change_ou_s_estompe` (228) |
| `tests/test_rendre_service.py` | `test_deux_services_et_redemande_apres_recharge` (73) |
| `tests/test_repli_et_appel.py` | `test_une_parole_sans_issue_ni_phrase_admise` (251) |
| `tests/test_restes_fusions.py` | `_livrer` (62) |
| `tests/test_secours_acquitte.py` | `test_appel_reel_suivi_puis_constate_autre_scenario` (94, 101) ; `test_captures_reelles_ne_renvoient_plus_au_danger` (45, 69) ; `test_joueur_constate_et_nouveau_cri_reouvre` (115, 119) |
| `tests/test_securite.py` | `test_un_bruit_venu_d_ailleurs_inquiete_qui_n_en_voit_pas_la_cause` (82) ; `test_un_geste_illicite_vu_inquiete_le_temoin` (102) |
| `tests/test_service_non_defait.py` | `test_combustible_epuise_ne_rouvre_pas_la_parole` (314) ; `test_serrure_promise_et_payee_par_joueur` (254) |
| `tests/test_signalements.py` | `test_le_recours_survit_a_la_memoire_bornee` (93) |
| `tests/test_signes.py` | `test_guet_lu_a_psy_14_manque_a_8_et_autre_guetteur` (161) ; `test_mensonge_flaire_deux_locuteurs_sans_apprendre_le_vrai` (360) |
| `tests/test_signes_calibration.py` | `test_disparition_retour_et_peremption_sont_de_nouvelles_lectures` (193) ; `test_perdre_la_vue_ne_recree_pas_le_signal_physique` (202, 211) ; `test_relecture_du_guet_reel_relais7_a_441_minutes` (118, 124) ; `test_relecture_rafraichit_sans_souvenir_ni_ligne_et_echec_preserve` (156, 162, 172) |
| `tests/test_social.py` | `ilse_a_vu_le_joueur` (80) ; `rumeurs` (60) ; `test_affamee_a_l_extreme_elle_crochete_sous_les_yeux_d_ilse` (278) ; `test_gorm_voit_ses_vivres_aux_mains_de_brune` (171) ; `test_la_ronde_de_gorm_decouvre_la_reserve_forcee` (235) ; `test_temoin_qui_entre_pendant_le_geste` (220) ; `test_un_jet_rate_laisse_gorm_sceptique` (109) |
| `tests/test_soi_meme.py` | `accusation_directe` (60, 70, 78) ; `assertSansAutoRumeur` (36) ; `test_seul_un_aveu_explicitement_type_accuse_son_locuteur` (113) |
| `tests/test_suivi_vocal.py` | `test_changement_de_salle_repositionnement_et_appel_de_deux_scenarios` (74, 81) |
| `tests/test_surprise.py` | `test_a_pas_feutres_on_lui_prend_son_bien_dans_le_dos` (62) |
| `tests/test_tache_promise_recours.py` | `test_deux_services_remis_tenus_et_recharges_meme_laps` (201, 203) ; `test_offre_visible_dans_le_journal_moteur_recharge` (151) ; `test_promesse_rompue_annoncee_sans_second_marche` (227) |
| `tests/test_taches_payees.py` | `test_annulation_sauvee_n_informe_pas_a_distance_et_ne_promet_plus_le_service` (240) ; `test_promesse_gratuite_devenue_impossible_annoncee` (216) ; `test_relais42_la_part_ne_reste_pas_due_soixante_minutes` (83) |
| `tests/test_temps_etat.py` | `test_qui_se_retourne_pendant_le_vol_du_joueur_en_est_temoin` (306) ; `test_un_geste_de_pnj_a_cheval_sur_deux_actions_garde_ses_temoins` (325) |
| `tests/test_tensions.py` | `test_apres_avoir_mange_il_referme_sa_reserve` (507) ; `test_refusee_ilse_achete_sa_part_avec_sa_bourse` (471) |
| `tests/test_trainer.py` | `test_deces_aucune_contrainte_et_ligote_auberge` (101) ; `test_plusieurs_cases_et_seuil_reel_avec_temoin` (176) |
| `tests/test_tuer.py` | `test_autre_victime_sans_temoin_decouverte_sans_coupable` (84) ; `test_depouiller_bien_du_mort_faute_et_temoin` (145) ; `test_joueur_ligote_cri_temoin_nouvelle` (44, 45, 46) |
| `tests/test_voix.py` | `test_c_etait_bien_lui` (436) ; `test_cru_sur_parole_sans_gain_de_confiance_puis_demasque` (418) ; `test_hugues_hele_anselme_a_travers_la_porte` (132) ; `test_le_joueur_dans_le_noir_demande_sa_part_a_gorm` (257) ; `test_un_appel_sans_reponse_n_est_pas_repete_en_boucle` (192) ; `test_un_cri_sans_les_mots_inquiete_les_mots_non` (214) |
| `tests/test_voix_inconnues.py` | `test_cas_reel_une_voix_jamais_entendue_obtient_sa_part_comme_un_etranger_vu` (79) |

## 4. Outils qui emploient la clé `memoire`

26 expressions brutes ; inclut les diagnostics de recherche, les copies de banc et les lectures d’archives.

| Fichier / fonction | Lignes |
|---|---|
| `tools/bilan_sous_arbres.py` · `main` | 71 |
| `tools/detecter_changements_avis.py` · `_est_accompli` | 126, 168 |
| `tools/detecter_changements_avis.py` · `relever_entrees` | 251, 282, 286, 291, 296 |
| `tools/detecter_changements_avis.py` · `relever_services` | 532 |
| `tools/diagnostiquer_rester_pres.py` · `resume` | 39 |
| `tools/empreintes_nuits.py` · `nuit` | 116, 133, 135, 137 |
| `tools/mesure_cout.py` · `recherche` | 72, 73 |
| `tools/mesure_reflexion_190.py` · `recherche` | 96 |
| `tools/mesure_saillance_210.py` · `esprit_saillant` | 68 |
| `tools/mesure_saillance_210.py` · `recherche` | 150, 151 |
| `tools/mesurer_attente_bornee.py` · `observer` | 43 |
| `tools/mesurer_bissection_auberge.py` · `mesurer` | 77, 80, 82 |
| `tools/valider_occasion_336.py` · `offre` | 79 |

## 5. Dépendances de tests par registre

Accès explicites, méthodes `get/setdefault/pop` comprises. Les clés génériques (`intention`,
`besoins`, `croyances`) touchent aussi des fixtures ; le relevé ne les assimile pas toutes à une mémoire PNJ.

- `accord_initial` : `test_accord_date.py`
- `agendas` : `test_agendas_activation.py`, `test_agendas_amener_fin.py`, `test_agendas_amener_social.py`, `test_agendas_ascendant_evolue.py`, `test_agendas_compte_rendu.py`, `test_agendas_destinataires.py`, `test_agendas_evenement.py`, `test_agendas_faire_confier.py`, `test_agendas_fins.py`, `test_agendas_garder.py`, `test_agendas_mandat.py`, `test_agendas_naissance.py`, `test_agendas_proteger.py`, `test_agendas_reaffecter.py`, `test_agendas_socle.py`, `test_attente.py`, `test_crue_hameau_agenda.py`, `test_depart_definitif.py`, `test_eau.py`, `test_empathie.py`, `test_empathie_peur.py`, `test_installation_gardee.py`, `test_interposition_lieu.py`, `test_occasions_scenarios.py`, `test_proposer_recours.py`, `test_recit_agendas.py`, `test_recours_agenda.py`, `test_rendre_service.py`, `test_restitution_route.py`, `test_suivi_vocal.py`
- `aides_attendues` : `test_agendas_amener_social.py`, `test_allumer_pour_soi.py`, `test_contrat_engagement.py`, `test_recours_agenda.py`, `test_recours_prioritaire.py`, `test_suivi_delegation.py`
- `attentes_bornees` : `test_attente_bornee.py`, `test_compensation_outil.py`, `test_etapes_chainees.py`, `test_recours_negatif.py`
- `attributions` : `test_agendas_reaffecter.py`, `test_mandat_joueur.py`
- `balayage` : `test_temps_etat.py`
- `besoins` : `support.py`, `test_agendas_activation.py`, `test_agendas_amener_social.py`, `test_agendas_devis_observateur.py`, `test_agendas_jugement_mandat.py`, `test_agendas_naissance.py`, `test_allumer_pour_soi.py`, `test_appel_negocie.py`, `test_appeler_donneur.py`, `test_attente.py`, `test_attente_bornee.py`, `test_auberge.py`, `test_avis_menace.py`, `test_battants_brises.py`, `test_besoins.py`, `test_boucles_pnj.py`, `test_bourse_redemandee.py`, `test_captivite.py`, `test_caractere.py`, `test_ceder_outil.py`, `test_combat.py`, `test_constater_rumeurs.py`, `test_contact_position_inconnue.py`, `test_contact_sous_but.py`, `test_contrat_engagement.py`, `test_contre_offre.py`, `test_corps.py`, `test_cout_suite.py`, `test_crochetage_surenchere.py`, `test_defense.py`, `test_defenses_publiques.py`, `test_deliberation_evenements.py`, `test_demander_cause.py`, `test_depart.py`, `test_dynamique_besoins.py`, `test_eau.py`, `test_echanges_argent.py`, `test_echelle_choix.py`, `test_empathie.py`, `test_empathie_peur.py`, `test_entretenir.py`, `test_esprits.py`, `test_evacuation_juge.py`, `test_fuite_lumiere.py`, `test_garde_plan.py`, `test_garde_pret.py`, `test_gardien_detresse.py`, `test_installation_gardee.py`, `test_intermediaires.py`, `test_interposition.py`, `test_lampes_parts.py`, `test_lumiere.py`, `test_lumiere_garde.py`, `test_mine.py`, `test_navettes_garde.py`, `test_occasion_protection.py`, `test_offre_sensee.py`, `test_ouie.py`, `test_ouie_commune.py`, `test_ouie_temoins.py`, `test_parole_voix.py`, `test_paroles.py`, `test_petits_correctifs.py`, `test_peur_transmise.py`, `test_place_perimee.py`, `test_planif_cout.py`, `test_planif_defauts.py`, `test_promesse_sans_profil.py`, `test_proposer_recours.py`, `test_propositions.py`, `test_protection.py`, `test_recit_pnj.py`, `test_recours_negatif.py`, `test_recours_prioritaire.py`, `test_reessai_obstacle.py`, `test_refus_leve_contrepartie.py`, `test_refus_retenus.py`, `test_relations_graduees.py`, `test_relations_lectures.py`, `test_rendre_service.py`, `test_ressources.py`, `test_restauration_charges.py`, `test_restitution_route.py`, `test_securite.py`, `test_service_non_defait.py`, `test_service_rejoindre.py`, `test_signalements.py`, `test_signes.py`, `test_social.py`, `test_sortie_exterieure.py`, `test_sous_obstacle.py`, `test_suivi_vocal.py`, `test_survie_en_route.py`, `test_tache_promise_recours.py`, `test_temps_etat.py`, `test_temps_reel.py`, `test_tensions.py`, `test_une_source.py`, `test_verifier_eau.py`, `test_voix.py`, `test_voix_inconnues.py`, `test_voix_suite.py`
- `bruits` : `test_contreparties.py`, `test_disputes.py`, `test_ecoute.py`, `test_noms.py`, `test_offre_sensee.py`, `test_ouie_commune.py`, `test_peur_transmise.py`, `test_protection.py`, `test_relances_luna.py`, `test_relations_graduees.py`, `test_sous_obstacle.py`, `test_temps_etat.py`
- `compagnie` : `test_peur_transmise.py`, `test_recours_prioritaire.py`, `test_securite.py`
- `confies` : `test_agendas_mandat.py`
- `confirme` : `test_agendas_mandat.py`
- `contrat_intention` : `test_empathie_peur.py`, `test_etapes_chainees.py`, `test_recours_prioritaire.py`
- `conversation` : `perception_support.py`, `test_accords_nombre.py`, `test_artisanat.py`, `test_audience.py`, `test_avis_parles.py`, `test_cache_kv_local.py`, `test_comprehension.py`, `test_comptes_fidelite.py`, `test_comptes_issue.py`, `test_comptes_moteur.py`, `test_comptes_naturels.py`, `test_comptes_parles_moteur.py`, `test_comptes_paroles.py`, `test_connaissances.py`, `test_consentement.py`, `test_contenu_vide.py`, `test_corps_passage_terminal.py`, `test_corps_publics.py`, `test_correction_parole.py`, `test_descripteur_public.py`, `test_discours_indirect.py`, `test_elision.py`, `test_enrichissement.py`, `test_fabrication_publique.py`, `test_fabrication_terminal.py`, `test_fidelite_audience.py`, `test_fouille_faits.py`, `test_fournisseurs_jeu.py`, `test_gardes_justes.py`, `test_gestes_terminal.py`, `test_information_publique.py`, `test_informations_parlees.py`, `test_inventaire_public.py`, `test_inventaire_terminal.py`, `test_localisation.py`, `test_luna_noms.py`, `test_luna_restes.py`, `test_mandat_joueur.py`, `test_mj_restes.py`, `test_n3_reformule.py`, `test_narration.py`, `test_non_perception.py`, `test_operations.py`, `test_orientation_narrative.py`, `test_ou_est_il.py`, `test_outils_publics.py`, `test_outils_terminal.py`, `test_paiement_effectif.py`, `test_parole_corrections.py`, `test_parole_voix.py`, `test_passages_publics.py`, `test_perception.py`, `test_perception_canonique.py`, `test_perception_geste.py`, `test_piece_de_lot.py`, `test_prime_offre.py`, `test_projection_publique.py`, `test_promesse_sans_profil.py`, `test_promesses.py`, `test_propositions.py`, `test_question_absent.py`, `test_rappel_exact.py`, `test_rappels_g19.py`, `test_recit.py`, `test_recit_resultat.py`, `test_redire_passe.py`, `test_reperes_moteur.py`, `test_repli_et_appel.py`, `test_ressource_nommee.py`, `test_sans_message_technique.py`, `test_schema_invariant.py`, `test_sens_dette.py`, `test_signes_calibration.py`, `test_silence_rappel.py`, `test_tensions.py`, `test_transactions.py`, `test_tui.py`, `test_un_appel_de_moins.py`, `test_verdict_coherent.py`, `test_websocket_jeu.py`
- `croyances` : `support.py`, `test_accord_date.py`, `test_accords_publics.py`, `test_agendas_ascendant_evolue.py`, `test_agendas_compte_rendu.py`, `test_agendas_destinataires.py`, `test_agendas_devis_observateur.py`, `test_agendas_evenement.py`, `test_agendas_faire_confier.py`, `test_agendas_fins.py`, `test_agendas_jugement_mandat.py`, `test_agendas_pieces.py`, `test_agendas_reaffecter.py`, `test_agendas_socle.py`, `test_agendas_transferts.py`, `test_allumer_pour_soi.py`, `test_amener_flamme.py`, `test_appel_negocie.py`, `test_appels_restes.py`, `test_attention_conjointe.py`, `test_auberge.py`, `test_avis_joueur.py`, `test_avis_menace.py`, `test_avis_reels.py`, `test_battants_brises.py`, `test_besoins.py`, `test_boucles_pnj.py`, `test_bourse_redemandee.py`, `test_ceder_outil.py`, `test_constater_rumeurs.py`, `test_constater_soupcon.py`, `test_constats_partages.py`, `test_contact_position_inconnue.py`, `test_contact_sous_but.py`, `test_contrat_engagement.py`, `test_contreparties.py`, `test_corps_blessable.py`, `test_crochetage_surenchere.py`, `test_crue_hameau.py`, `test_defense.py`, `test_deja_dit.py`, `test_delai_cru.py`, `test_deliberation_evenements.py`, `test_demander_cause.py`, `test_depart.py`, `test_depart_definitif.py`, `test_detecter_changements_avis.py`, `test_diagonales.py`, `test_disputes.py`, `test_dynamique_besoins.py`, `test_eau.py`, `test_eau_plan_marche.py`, `test_echanges_argent.py`, `test_echanges_suite.py`, `test_echelle_choix.py`, `test_empathie.py`, `test_empathie_peur.py`, `test_enfermer.py`, `test_engagement_deplacement.py`, `test_entretenir.py`, `test_esprits.py`, `test_etapes_chainees.py`, `test_evacuation_juge.py`, `test_fermeture_invalidee.py`, `test_force_luna.py`, `test_garde_ouidire.py`, `test_garde_pret.py`, `test_gardien_detresse.py`, `test_installation_gardee.py`, `test_intermediaires.py`, `test_lieu_ouvertures.py`, `test_localisation_crue.py`, `test_lumiere.py`, `test_lumiere_faible.py`, `test_lumiere_garde.py`, `test_mandat_joueur.py`, `test_marche.py`, `test_nouvelles_initiales.py`, `test_occasions_scenarios.py`, `test_orientation.py`, `test_ou_est_il.py`, `test_ouie.py`, `test_ouie_commune.py`, `test_ouie_temoins.py`, `test_parole_commune.py`, `test_parole_voix.py`, `test_paroles.py`, `test_parts_achetees.py`, `test_pas_compagnons.py`, `test_passage.py`, `test_petits_correctifs.py`, `test_planif_defauts.py`, `test_planification.py`, `test_preuve_engagement.py`, `test_prevision_bornee.py`, `test_proposer_recours.py`, `test_racheter_bien.py`, `test_reclamations_repetees.py`, `test_reclamer_vol.py`, `test_recours_agenda.py`, `test_recours_negatif.py`, `test_reessai_obstacle.py`, `test_refus_retenus.py`, `test_regard_joueur.py`, `test_rejeu.py`, `test_relations_graduees.py`, `test_relations_lectures.py`, `test_relations_socle.py`, `test_relations_statuts.py`, `test_rendez_vous_tenu.py`, `test_reprise_contact.py`, `test_restes_fusions.py`, `test_revalider_apres_refus.py`, `test_route_admissible.py`, `test_secours_acquitte.py`, `test_securite.py`, `test_service_repropose.py`, `test_signalements.py`, `test_signes.py`, `test_signes_calibration.py`, `test_social.py`, `test_sous_obstacle.py`, `test_suivi_vocal.py`, `test_surprise.py`, `test_survie_en_route.py`, `test_tache_promise_recours.py`, `test_taches_payees.py`, `test_temps_etat.py`, `test_temps_reel.py`, `test_tensions.py`, `test_trajets_reels.py`, `test_tuer.py`, `test_voix.py`, `test_voix_inconnues.py`, `test_voix_suite.py`
- `demande_refusee` : `test_appeler_donneur.py`, `test_navettes_garde.py`, `test_proposer_recours.py`, `test_rendre_service.py`
- `detresses_appelees` : `test_gardien_detresse.py`
- `dettes` : `test_agendas_socle.py`, `test_comptes_fidelite.py`, `test_comptes_issue.py`, `test_comptes_moteur.py`, `test_comptes_parles_moteur.py`, `test_crochetage_surenchere.py`, `test_echanges_suite.py`, `test_gardes_justes.py`, `test_petits_correctifs.py`, `test_prime_offre.py`, `test_realisation_datee.py`, `test_reclamations_repetees.py`, `test_refus_retenus.py`, `test_sens_dette.py`, `test_service_non_defait.py`, `test_taches_payees.py`, `test_verdict_coherent.py`
- `emissions_parole` : `test_rappel_exact.py`, `test_rappels_g19.py`
- `emotions` : `test_disputes.py`, `test_peur_transmise.py`, `test_signes_calibration.py`
- `en_vue` : `test_empathie_peur.py`
- `engagements` : `test_accord_date.py`, `test_achat_promis_annule.py`, `test_agendas_amener_social.py`, `test_allumer_pour_soi.py`, `test_caractere.py`, `test_comptes_parles_moteur.py`, `test_connaissances.py`, `test_corps.py`, `test_crochetage_surenchere.py`, `test_crue_hameau_agenda.py`, `test_dialogues.py`, `test_echanges_argent.py`, `test_echanges_suite.py`, `test_echelle_choix.py`, `test_entretenir.py`, `test_garde_pret.py`, `test_gardien_detresse.py`, `test_improvisation.py`, `test_lampes_parts.py`, `test_parole_commune.py`, `test_parts_achetees.py`, `test_petits_correctifs.py`, `test_piece_de_lot.py`, `test_prime_offre.py`, `test_promesses.py`, `test_reference_temporelle.py`, `test_refus_retenus.py`, `test_restes_fusions.py`, `test_taches_payees.py`, `test_voix_inconnues.py`
- `entendus` : `test_constater_rumeurs.py`, `test_designations.py`, `test_emissions_parole.py`, `test_luna_noms.py`, `test_noms.py`, `test_ouie.py`, `test_rappels_g19.py`, `test_rendez_vous_tenu.py`, `test_temps_etat.py`, `test_voix.py`, `test_voix_inconnues.py`, `test_voix_suite.py`
- `eveil` : `support.py`, `test_accord_date.py`, `test_attention_conjointe.py`, `test_corps_blessable.py`, `test_empathie_peur.py`, `test_pas_compagnons.py`, `test_peur_transmise.py`, `test_realisation_datee.py`
- `faits_dits` : `test_agendas_activation.py`, `test_avis_redits.py`, `test_deja_dit.py`
- `faits_initiaux` : `test_etapes_chainees.py`, `test_nouvelles_initiales.py`
- `faits_vus` : `test_faits_locaux.py`, `test_fouille_faits.py`
- `finances_pnj` : `support.py`, `test_accord_date.py`, `test_accords_nombre.py`, `test_achat_promis_annule.py`, `test_agendas_evenement.py`, `test_agendas_naissance.py`, `test_agendas_pieces.py`, `test_agendas_socle.py`, `test_allumer_pour_soi.py`, `test_bourse_redemandee.py`, `test_ceder_outil.py`, `test_compensation_outil.py`, `test_comptes_parles_moteur.py`, `test_consentement.py`, `test_contre_offre.py`, `test_contreparties.py`, `test_crochetage_surenchere.py`, `test_delai_cru.py`, `test_dialogues.py`, `test_dynamique_besoins.py`, `test_echanges_argent.py`, `test_echanges_suite.py`, `test_intermediaires.py`, `test_lampes_parts.py`, `test_marche.py`, `test_navettes_garde.py`, `test_occasion_protection.py`, `test_offre_sensee.py`, `test_ouie_temoins.py`, `test_prime_offre.py`, `test_proposer_recours.py`, `test_propositions_redites.py`, `test_racheter_bien.py`, `test_realisation_datee.py`, `test_reclamations_repetees.py`, `test_recours_negatif.py`, `test_reference_temporelle.py`, `test_refus_leve_contrepartie.py`, `test_refus_retenus.py`, `test_restes_fusions.py`, `test_revalider_apres_refus.py`, `test_securite.py`, `test_service_non_defait.py`, `test_tache_promise_recours.py`, `test_temps_etat.py`, `test_tensions.py`, `test_vente_generique.py`, `test_verifier_eau.py`, `test_vol.py`
- `indices_soupcon` : `support.py`, `test_constater_soupcon.py`
- `intention` : `test_accords_nombre.py`, `test_agendas_ascendant_evolue.py`, `test_agendas_compte_rendu.py`, `test_agendas_evenement.py`, `test_agendas_faire_confier.py`, `test_agendas_naissance.py`, `test_agendas_pieces.py`, `test_agendas_proteger.py`, `test_agendas_reaffecter.py`, `test_amener_flamme.py`, `test_appel_negocie.py`, `test_appeler_donneur.py`, `test_appels_restes.py`, `test_attention_conjointe.py`, `test_battants_brises.py`, `test_besoins.py`, `test_boucles_pnj.py`, `test_bourse_redemandee.py`, `test_but_protection.py`, `test_ceder_outil.py`, `test_chercher_appeler.py`, `test_combat.py`, `test_compensation_outil.py`, `test_constater_rumeurs.py`, `test_contact_position_inconnue.py`, `test_contact_sous_but.py`, `test_contrat_engagement.py`, `test_contre_offre.py`, `test_contreparties.py`, `test_corps_blessable.py`, `test_crochetage_surenchere.py`, `test_defense.py`, `test_deliberation_evenements.py`, `test_demander_cause.py`, `test_detecter_changements_avis.py`, `test_diagonales.py`, `test_dynamique_besoins.py`, `test_eau.py`, `test_echanges_argent.py`, `test_echanges_suite.py`, `test_echelle_choix.py`, `test_empathie.py`, `test_empathie_peur.py`, `test_enfermer.py`, `test_esprits.py`, `test_evacuation_juge.py`, `test_fuite_lumiere.py`, `test_impressions_observer.py`, `test_improvisation.py`, `test_intermediaires.py`, `test_interposition.py`, `test_interposition_lieu.py`, `test_livraison_inconnue.py`, `test_localisation_crue.py`, `test_lumiere.py`, `test_lumiere_faible.py`, `test_lumiere_garde.py`, `test_marche.py`, `test_navettes_garde.py`, `test_occasion_protection.py`, `test_offre_sensee.py`, `test_ou_est_il.py`, `test_ouie.py`, `test_ouie_commune.py`, `test_ouie_temoins.py`, `test_parole_voix.py`, `test_paroles.py`, `test_pas_compagnons.py`, `test_petits_correctifs.py`, `test_peur_transmise.py`, `test_place_perimee.py`, `test_presences.py`, `test_promesses.py`, `test_proposer_recours.py`, `test_propositions_redites.py`, `test_protection.py`, `test_reactions.py`, `test_realisation_datee.py`, `test_recit_agendas.py`, `test_reclamer_vol.py`, `test_recours_agenda.py`, `test_recours_negatif.py`, `test_recours_prioritaire.py`, `test_reessai_obstacle.py`, `test_refus_leve_contrepartie.py`, `test_relations_graduees.py`, `test_rendez_vous_tenu.py`, `test_rendre_service.py`, `test_restauration_charges.py`, `test_restitution_route.py`, `test_revalider_apres_refus.py`, `test_route_admissible.py`, `test_securite.py`, `test_service_non_defait.py`, `test_service_rejoindre.py`, `test_service_repropose.py`, `test_signes.py`, `test_signes_calibration.py`, `test_social.py`, `test_suivi_delegation.py`, `test_suivi_vocal.py`, `test_surprise.py`, `test_survie_en_route.py`, `test_tache_promise_recours.py`, `test_taches_payees.py`, `test_temps_etat.py`, `test_temps_reel.py`, `test_tensions.py`, `test_trajets_reels.py`, `test_verifier_eau.py`, `test_voix_inconnues.py`
- `issues_obligations` : `test_realisation_datee.py`
- `lectures` : `test_attention_conjointe.py`, `test_calibrer_signes.py`, `test_impressions_observer.py`, `test_signes.py`, `test_signes_calibration.py`, `test_soi_meme.py`
- `libre` : `test_accord_date.py`, `test_agendas_activation.py`, `test_agendas_amener_fin.py`, `test_agendas_amener_social.py`, `test_agendas_ascendant_evolue.py`, `test_agendas_compte_rendu.py`, `test_agendas_jugement_mandat.py`, `test_agendas_mandat.py`, `test_agendas_pieces.py`, `test_agendas_reaffecter.py`, `test_agendas_socle.py`, `test_avis_menace.py`, `test_captivite.py`, `test_caractere.py`, `test_constats_partages.py`, `test_crue_hameau_agenda.py`, `test_defense.py`, `test_deja_dit.py`, `test_deliberation_evenements.py`, `test_disputes.py`, `test_empathie.py`, `test_empathie_peur.py`, `test_enfermer.py`, `test_engagement_deplacement.py`, `test_entretenir.py`, `test_mandat_joueur.py`, `test_occasion_protection.py`, `test_orientation.py`, `test_ouie.py`, `test_ouie_temoins.py`, `test_pas_compagnons.py`, `test_place_perimee.py`, `test_realisation_datee.py`, `test_recit_pnj.py`, `test_relations_lectures.py`, `test_restitution_route.py`, `test_revalider_apres_refus.py`, `test_securite.py`, `test_signalements.py`, `test_social.py`, `test_sous_obstacle.py`, `test_temps_etat.py`, `test_temps_reel.py`, `test_tenir.py`, `test_trainer.py`, `test_verifier_eau.py`
- `manque` : `test_contrat_engagement.py`, `test_empathie_peur.py`, `test_pas_compagnons.py`, `test_restauration_charges.py`
- `noms` : `test_constater_soupcon.py`, `test_elision.py`, `test_restes_fusions.py`, `test_signalements.py`, `test_voix_suite.py`
- `noms_connus` : `test_accords_publics.py`, `test_avis_menace.py`, `test_corps_publics_limites.py`, `test_defense.py`, `test_deja_dit.py`, `test_designations.py`, `test_elision.py`, `test_emissions_parole.py`, `test_luna_noms.py`, `test_nom_non_relie.py`, `test_non_perception.py`, `test_orientation_narrative.py`, `test_parole_corrections.py`, `test_parole_voix.py`, `test_perception_canonique.py`, `test_question_absent.py`, `test_reperes_moteur.py`, `test_restes_fusions.py`, `test_signes.py`, `test_social.py`, `test_voix.py`
- `occurrences_signes` : `test_signes_calibration.py`
- `offres_mandat_joueur` : `test_mandat_joueur.py`
- `paroles_joueur` : `test_emissions_parole.py`, `test_parole_commune.py`, `test_question_absent.py`
- `paroles_pnj` : `test_corps_blessable.py`, `test_emissions_parole.py`, `test_question_absent.py`, `test_rappel_exact.py`, `test_redire_passe.py`, `test_silence_rappel.py`
- `patience` : `test_marche.py`, `test_signes.py`, `test_signes_calibration.py`, `test_survie_en_route.py`, `test_temps_reel.py`
- `permissions` : `test_agendas_pieces.py`, `test_agendas_transferts.py`, `test_allumer_pour_soi.py`, `test_contre_offre.py`, `test_echanges_argent.py`, `test_echanges_suite.py`, `test_garde_ouidire.py`, `test_racheter_bien.py`, `test_recours_negatif.py`, `test_refus_leve_contrepartie.py`, `test_restitution_route.py`, `test_sens_dette.py`, `test_temps_etat.py`
- `personnages_vus` : `test_attendu_designable.py`, `test_noms.py`, `test_parole_voix.py`, `test_restes_fusions.py`
- `personnes` : `test_noms.py`
- `portages` : `test_agendas_evenement.py`, `test_constater_soupcon.py`
- `preuves_relations` : `support.py`, `test_agendas_ascendant_evolue.py`
- `promesses_joueur` : `test_reference_temporelle.py`
- `pulsions` : `support.py`, `test_agendas_evenement.py`, `test_agendas_fins.py`, `test_agendas_garder.py`, `test_agendas_proteger.py`, `test_agendas_transferts.py`, `test_allumer_pour_soi.py`, `test_appeler_donneur.py`, `test_ceder_outil.py`, `test_contact_position_inconnue.py`, `test_contact_sous_but.py`, `test_contrat_engagement.py`, `test_contre_offre.py`, `test_contreparties.py`, `test_crue_hameau_autorite.py`, `test_defense.py`, `test_depart.py`, `test_descripteur_public.py`, `test_dynamique_besoins.py`, `test_echelle_choix.py`, `test_empathie.py`, `test_empathie_peur.py`, `test_entretenir.py`, `test_garde_ouidire.py`, `test_garde_plan.py`, `test_gardien_detresse.py`, `test_intermediaires.py`, `test_interposition.py`, `test_interposition_lieu.py`, `test_navettes_garde.py`, `test_ouie.py`, `test_petits_correctifs.py`, `test_planif_defauts.py`, `test_promesse_sans_profil.py`, `test_proposer_recours.py`, `test_propositions.py`, `test_reclamer_vol.py`, `test_recours_prioritaire.py`, `test_reessai_obstacle.py`, `test_refus_leve_contrepartie.py`, `test_relations_graduees.py`, `test_rendre_service.py`, `test_restauration_charges.py`, `test_restitution_route.py`, `test_service_non_defait.py`, `test_service_rejoindre.py`, `test_signalements.py`, `test_sortie_exterieure.py`, `test_suivi_delegation.py`, `test_tache_promise_recours.py`, `test_trajets_reels.py`
- `recherches` : `test_dynamique_besoins.py`, `test_recit_pnj.py`, `test_rendez_vous_tenu.py`, `test_signalements.py`
- `recours_intermediaires` : `test_completion_preuves.py`, `test_etapes_chainees.py`, `test_intermediaires.py`
- `recours_propositions` : `test_besoins.py`
- `recours_services` : `test_completion_preuves.py`, `test_etapes_chainees.py`, `test_intermediaires.py`, `test_rendre_service.py`
- `reference_temporelle` : `test_realisation_datee.py`, `test_reference_temporelle.py`
- `refus` : `test_achat_promis_annule.py`, `test_agendas_devis_observateur.py`, `test_agendas_faire_confier.py`, `test_agendas_reaffecter.py`, `test_attente_bornee.py`, `test_compensation_outil.py`, `test_constats_partages.py`, `test_contact_sous_but.py`, `test_contre_offre.py`, `test_demander_cause.py`, `test_intermediaires.py`, `test_navettes_garde.py`, `test_offre_sensee.py`, `test_oracle_g1.py`, `test_ou_est_il.py`, `test_pas_compagnons.py`, `test_propositions_redites.py`, `test_refus_leve_contrepartie.py`, `test_refus_retenus.py`, `test_rendre_service.py`, `test_revalider_apres_refus.py`, `test_sous_obstacle.py`, `test_tensions.py`
- `regards_suivis` : `test_attention_conjointe.py`, `test_completion_preuves.py`
- `rejoindre` : `test_appel_negocie.py`, `test_appeler_donneur.py`, `test_echelle_choix.py`, `test_ou_est_il.py`, `test_rendez_vous.py`, `test_rendez_vous_tenu.py`, `test_restes_fusions.py`
- `rejoint` : `test_appel_negocie.py`, `test_appeler_donneur.py`, `test_avis_menace.py`, `test_echelle_choix.py`, `test_luna_noms.py`, `test_ou_est_il.py`, `test_parole_voix.py`, `test_rendez_vous.py`, `test_rendez_vous_tenu.py`
- `relations` : `support.py`, `test_accord_date.py`, `test_accords_publics.py`, `test_agendas_pieces.py`, `test_attention_conjointe.py`, `test_avis_menace.py`, `test_besoins.py`, `test_ceder_outil.py`, `test_constater_rumeurs.py`, `test_constater_soupcon.py`, `test_contrat_engagement.py`, `test_contreparties.py`, `test_defense.py`, `test_demander_cause.py`, `test_dynamique_besoins.py`, `test_empathie.py`, `test_empathie_peur.py`, `test_garde_pret.py`, `test_impressions_observer.py`, `test_intermediaires.py`, `test_interposition.py`, `test_interposition_lieu.py`, `test_occasion_protection.py`, `test_peur_transmise.py`, `test_place_perimee.py`, `test_proposer_recours.py`, `test_propositions.py`, `test_realisation_datee.py`, `test_recit_pnj.py`, `test_reclamer_vol.py`, `test_recours_negatif.py`, `test_rejeu.py`, `test_relations_ascendant.py`, `test_relations_graduees.py`, `test_relations_lectures.py`, `test_rendre_service.py`, `test_restes_fusions.py`, `test_service_non_defait.py`, `test_signes.py`, `test_signes_calibration.py`, `test_tache_promise_recours.py`, `test_taches_payees.py`, `test_temps_reel.py`
- `renoncements` : `test_dynamique_besoins.py`, `test_reessai_obstacle.py`, `test_reprise_contact.py`, `test_survie_en_route.py`, `test_temps_reel.py`
- `restitutions` : `test_bourse_redemandee.py`
- `secours` : `test_gardien_detresse.py`, `test_signalements.py`, `test_transitions_scenario.py`
- `sequence_obligations` : `test_reference_temporelle.py`
- `service_en_cours` : `test_completion_preuves.py`, `test_etapes_chainees.py`, `test_rendre_service.py`
- `services_rendus` : `test_pas_compagnons.py`, `test_purete_services.py`, `test_recours_negatif.py`, `test_service_non_defait.py`
- `signes_lus` : `test_attention_conjointe.py`, `test_empathie_peur.py`
- `souvenirs` : `test_scene.py`
- `souvenirs_personnages` : `test_comparaison.py`, `test_enrichissement.py`, `test_noms.py`, `test_parole_voix.py`, `test_personnages.py`, `test_projection_publique.py`, `test_recit.py`
- `souvenirs_portes` : `test_carte_cases.py`
- `souvenirs_visuels` : `test_attendu_designable.py`, `test_carte_cases.py`, `test_geste_hors_portee.py`, `test_localisation.py`, `test_luna_restes.py`, `test_moteur_cases.py`, `test_orientation_narrative.py`, `test_parole_voix.py`, `test_perception_canonique.py`, `test_regard_joueur.py`, `test_reperes_moteur.py`, `test_transitions_scenario.py`, `test_verdict_coherent.py`
- `suites` : `test_relations_graduees.py`, `test_restes_fusions.py`
- `suivi_signes` : `test_signes_calibration.py`
- `tirages_lecture_acteurs` : `test_attention_conjointe.py`, `test_impressions_observer.py`
- `urgences` : `test_dynamique_besoins.py`, `test_evacuation_juge.py`, `test_gardien_detresse.py`, `test_recours_prioritaire.py`, `test_reessai_obstacle.py`, `test_signalements.py`
- `veille` : `test_accord_date.py`, `test_realisation_datee.py`, `test_recours_negatif.py`
- `violences_joueur` : `test_corps_publics_limites.py`
- `visites` : `support.py`, `test_appel_negocie.py`, `test_besoins.py`, `test_constater_rumeurs.py`, `test_deliberation_evenements.py`, `test_depart.py`, `test_dynamique_besoins.py`, `test_echelle_choix.py`, `test_empathie_peur.py`, `test_esprits.py`, `test_lampes_buts.py`, `test_parole_voix.py`, `test_paroles.py`, `test_recours_agenda.py`, `test_recours_prioritaire.py`, `test_reessai_obstacle.py`, `test_securite.py`, `test_social.py`, `test_sortie_exterieure.py`, `test_sous_obstacle.py`, `test_suivi_delegation.py`, `test_temps_etat.py`, `test_temps_reel.py`, `test_tensions.py`, `test_voix.py`, `test_voix_inconnues.py`
- `voix` : `test_constater_rumeurs.py`, `test_echanges_argent.py`, `test_ouie.py`, `test_ouie_commune.py`, `test_parole_commune.py`, `test_parole_voix.py`, `test_peur_transmise.py`, `test_relations_graduees.py`, `test_relations_lectures.py`, `test_relations_statuts.py`, `test_signalements.py`, `test_social.py`, `test_soi_meme.py`, `test_voix.py`, `test_voix_inconnues.py`, `test_voix_suite.py`
- `voix_connues` : `test_agendas_compte_rendu.py`, `test_agendas_reaffecter.py`, `test_avis_menace.py`, `test_constater_rumeurs.py`, `test_designations.py`, `test_disputes.py`, `test_engagement_deplacement.py`, `test_mandat_joueur.py`, `test_noms.py`, `test_parole_voix.py`, `test_voix.py`, `test_voix_inconnues.py`, `test_voix_suite.py`
- `voix_entendues` : `test_constater_rumeurs.py`, `test_designations.py`, `test_information_publique.py`, `test_informations_parlees.py`, `test_noms.py`, `test_parole_commune.py`, `test_parole_corrections.py`, `test_parole_voix.py`, `test_relances_luna.py`, `test_silence_rappel.py`, `test_voix.py`, `test_voix_inconnues.py`, `test_voix_suite.py`

## 6. Limites du relevé

Une clé calculée, un alias de dictionnaire ou une structure entièrement sérialisée ne se
déduit pas d’un accès littéral. Les accès indirects identifiés (voix, mémoire, projets,
engagements et preuves) figurent dans la conception ; le futur contrôle AST doit fermer
ces voies. Les branches concurrentes 372/374 ne sont pas le code mesuré.
