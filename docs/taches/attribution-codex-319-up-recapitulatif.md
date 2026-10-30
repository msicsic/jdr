# Attribution des 47 incidents du lot 319

Suite d’essai `3fd819d` : 30 échecs, 17 erreurs. Référence isolée sans U-P : `9237e14` ; branche corrigée : `3ee69d4`.

La référence exécute les seules méthodes en incident (23 tests comptés, un échec de `setUpClass` empêchant sa méthode de démarrer). Elle reproduit exactement les sept incidents D : deux échecs et cinq erreurs, aucun incident supplémentaire. Sur la branche, les dix fichiers adaptés passent intégralement : 102 tests, zéro échec, erreur ou saut.

| Classe | Attribution et preuve |
|---|---|
| A — 24 | Attente historique périmée par U-P. La référence passe ces méthodes avec leur ancien texte ; le journal d’essai montre seulement la ligne moteur ajoutée. L’oracle corrigé compare le texte composé entier. Les assertions d’état, d’appels, de recharge et de refus restent présentes. Le témoin de résultat capture le texte composé sauvegardé avant affichage. |
| B — 12 | Défaut des tests U-P lors du portage G15 : l’ancien registre `paroles_joueur` a été retiré. Les tests utilisent désormais `emissions.joueur` et conservent le contrôle de l’état complet et du rendu ; les trois interfaces passent. |
| C — 4 | Préexistants déjà corrigés par 331/334 et fusionnés sans rebase. Les méthodes correspondantes passent sur la référence `9237e14`. |
| D — 7 | Préexistants reproduits individuellement sur l’intégration seule. Six incidents viennent de la sonde `_retentir` sans argument `emission` (rejeu et audit) ; le septième est le refus de vente d’huile dans la voie directe après 8 h, sans récapitulatif. Ils restent à traiter hors du lot 319. |

Les libellés et sous-cas ci-dessous sont ceux du journal d’essai ; aucun incident n’est regroupé ou retiré du dénominateur.

| Nº | Incident du journal | Classe | Résultat sur la référence |
|---:|---|:---:|:---:|
| 1 | `ERROR: test_la_lumiere_suit_les_sources_dans_un_autre_scenario (test_rejeu.AutresNuitsTests.test_la_lumiere_suit_les_sources_dans_un_autre_scenario)` | D | même incident |
| 2 | `ERROR: test_la_page_tourne_avec_ses_filtres (test_rejeu.AutresNuitsTests.test_la_page_tourne_avec_ses_filtres)` | D | même incident |
| 3 | `ERROR: test_les_gestes_illicites_gardent_leurs_temoins (test_rejeu.AutresNuitsTests.test_les_gestes_illicites_gardent_leurs_temoins)` | D | même incident |
| 4 | `ERROR: test_une_page_par_graine (test_rejeu.AutresNuitsTests.test_une_page_par_graine)` | D | même incident |
| 5 | `ERROR: setUpClass (test_rejeu.RejeuTests)` | D | même incident |
| 6 | `ERROR: test_tui_tous_les_cas (test_comprehension.ComprehensionTUITests.test_tui_tous_les_cas) (cas='avis')` | B | test U-P absent |
| 7 | `ERROR: test_tui_tous_les_cas (test_comprehension.ComprehensionTUITests.test_tui_tous_les_cas) (cas='tous')` | B | test U-P absent |
| 8 | `ERROR: test_tui_tous_les_cas (test_comprehension.ComprehensionTUITests.test_tui_tous_les_cas) (cas='parole')` | B | test U-P absent |
| 9 | `ERROR: test_tui_tous_les_cas (test_comprehension.ComprehensionTUITests.test_tui_tous_les_cas) (cas='chuchotement')` | B | test U-P absent |
| 10 | `ERROR: test_console_et_web_tous_les_cas_puis_reprise (test_comprehension.ComprehensionTests.test_console_et_web_tous_les_cas_puis_reprise) (transport='console', cas='avis')` | B | test U-P absent |
| 11 | `ERROR: test_console_et_web_tous_les_cas_puis_reprise (test_comprehension.ComprehensionTests.test_console_et_web_tous_les_cas_puis_reprise) (transport='console', cas='tous')` | B | test U-P absent |
| 12 | `ERROR: test_console_et_web_tous_les_cas_puis_reprise (test_comprehension.ComprehensionTests.test_console_et_web_tous_les_cas_puis_reprise) (transport='console', cas='parole')` | B | test U-P absent |
| 13 | `ERROR: test_console_et_web_tous_les_cas_puis_reprise (test_comprehension.ComprehensionTests.test_console_et_web_tous_les_cas_puis_reprise) (transport='console', cas='chuchotement')` | B | test U-P absent |
| 14 | `ERROR: test_console_et_web_tous_les_cas_puis_reprise (test_comprehension.ComprehensionTests.test_console_et_web_tous_les_cas_puis_reprise) (transport='web', cas='avis')` | B | test U-P absent |
| 15 | `ERROR: test_console_et_web_tous_les_cas_puis_reprise (test_comprehension.ComprehensionTests.test_console_et_web_tous_les_cas_puis_reprise) (transport='web', cas='tous')` | B | test U-P absent |
| 16 | `ERROR: test_console_et_web_tous_les_cas_puis_reprise (test_comprehension.ComprehensionTests.test_console_et_web_tous_les_cas_puis_reprise) (transport='web', cas='parole')` | B | test U-P absent |
| 17 | `ERROR: test_console_et_web_tous_les_cas_puis_reprise (test_comprehension.ComprehensionTests.test_console_et_web_tous_les_cas_puis_reprise) (transport='web', cas='chuchotement')` | B | test U-P absent |
| 18 | `FAIL: test_cas_reel_auberge_apres_huit_heures_l_huile_achetee_recharge_une_lanterne_a_sec (test_lampes_parts.PartsPourSourcesTests.test_cas_reel_auberge_apres_huit_heures_l_huile_achetee_recharge_une_lanterne_a_sec)` | D | même incident |
| 19 | `FAIL: test_audit_ecrit_une_nuit_mesuree (test_detecter_changements_avis.DetecterAvisTests.test_audit_ecrit_une_nuit_mesuree)` | D | même incident |
| 20 | `FAIL: test_inverse_ne_retire_que_les_occasions_du_lot (test_occasions_scenarios.OccasionsScenariosTests.test_inverse_ne_retire_que_les_occasions_du_lot) (scenario='crue_hameau')` | C | vert |
| 21 | `FAIL: test_l_approche_structuree_ne_devient_pas_la_description_du_geste (test_luna_noms.NarrationTests.test_l_approche_structuree_ne_devient_pas_la_description_du_geste) (saisie="je m'étire")` | A | vert |
| 22 | `FAIL: test_l_approche_structuree_ne_devient_pas_la_description_du_geste (test_luna_noms.NarrationTests.test_l_approche_structuree_ne_devient_pas_la_description_du_geste) (saisie='je fais un salut')` | A | vert |
| 23 | `FAIL: test_geste_immediat_sans_second_appel (test_recit_resultat.RecitResultatTests.test_geste_immediat_sans_second_appel)` | A | vert |
| 24 | `FAIL: test_une_intention_nommee_reste_individuelle_sans_devenir_une_parole_forcee (test_audience.AudienceTests.test_une_intention_nommee_reste_individuelle_sans_devenir_une_parole_forcee) (saisie='je paie Aubin trois pièces pour une de ses planches')` | C | vert |
| 25 | `FAIL: test_question_reelle_dans_le_noir_ne_devient_pas_observation (test_question_absent.QuestionAbsentTests.test_question_reelle_dans_le_noir_ne_devient_pas_observation)` | A | vert |
| 26 | `FAIL: test_questions_reelles_sur_les_absents_une_interpretation_auditee (test_question_absent.QuestionAbsentTests.test_questions_reelles_sur_les_absents_une_interpretation_auditee) (saisie='Que fait Brune ?')` | A | vert |
| 27 | `FAIL: test_questions_reelles_sur_les_absents_une_interpretation_auditee (test_question_absent.QuestionAbsentTests.test_questions_reelles_sur_les_absents_une_interpretation_auditee) (saisie='Que fait Gorm en ce moment ?')` | A | vert |
| 28 | `FAIL: test_questions_reelles_sur_les_absents_une_interpretation_auditee (test_question_absent.QuestionAbsentTests.test_questions_reelles_sur_les_absents_une_interpretation_auditee) (saisie='Où est Brune')` | A | vert |
| 29 | `FAIL: test_questions_reelles_sur_les_absents_une_interpretation_auditee (test_question_absent.QuestionAbsentTests.test_questions_reelles_sur_les_absents_une_interpretation_auditee) (saisie='Gorm est-il encore en bas ?')` | A | vert |
| 30 | `FAIL: test_cas_reel_un_refus_de_forme_n_est_pas_montre (test_parole_corrections.FaisabiliteTests.test_cas_reel_un_refus_de_forme_n_est_pas_montre)` | A | vert |
| 31 | `FAIL: test_captures_mine_et_auberge_memes_plans_visites_monde_et_rendu_recharges (test_etapes_chainees.EtapesTests.test_captures_mine_et_auberge_memes_plans_visites_monde_et_rendu_recharges) (scenario='mine')` | C | vert |
| 32 | `FAIL: test_captures_mine_et_auberge_memes_plans_visites_monde_et_rendu_recharges (test_etapes_chainees.EtapesTests.test_captures_mine_et_auberge_memes_plans_visites_monde_et_rendu_recharges) (scenario='auberge')` | C | vert |
| 33 | `FAIL: test_description_mal_formee_corrigee_ou_repli_apres_recharge (test_sans_message_technique.SansMessageTechniqueTests.test_description_mal_formee_corrigee_ou_repli_apres_recharge) (saisie="à quoi ressemble le mur de l'atelier ?", corrigee=True)` | A | vert |
| 34 | `FAIL: test_description_mal_formee_corrigee_ou_repli_apres_recharge (test_sans_message_technique.SansMessageTechniqueTests.test_description_mal_formee_corrigee_ou_repli_apres_recharge) (saisie='à quoi ressemble la bobine de ficelle ?', corrigee=True)` | A | vert |
| 35 | `FAIL: test_console_exacte_sans_audit_sur_deux_scenes (test_rappel_exact.RappelExactTests.test_console_exacte_sans_audit_sur_deux_scenes)` | A | vert |
| 36 | `FAIL: test_rappel_deforme_refuse_puis_exact_affiche_apres_recharge (test_rappel_exact.RappelExactTests.test_rappel_deforme_refuse_puis_exact_affiche_apres_recharge)` | A | vert |
| 37 | `FAIL: test_ecouter_et_chercher_passent_la_revue_du_premier_coup_et_sont_sauves (test_perception_geste.PerceptionGesteTests.test_ecouter_et_chercher_passent_la_revue_du_premier_coup_et_sont_sauves) (saisie='je cherche des traces de pas sur le sol')` | A | vert |
| 38 | `FAIL: test_absence_dans_le_noir_personnes_et_objet_apres_recharge (test_perception_geste.VueCouranteTests.test_absence_dans_le_noir_personnes_et_objet_apres_recharge) (faux='Tu ne sais pas si Ilse a peur de Brune : tu n’as aucun indice sur ses sentiments, et aucune des deux n’est ici pour que tu puisses le vérifier.')` | A | vert |
| 39 | `FAIL: test_absence_dans_le_noir_personnes_et_objet_apres_recharge (test_perception_geste.VueCouranteTests.test_absence_dans_le_noir_personnes_et_objet_apres_recharge) (faux="Il n'y a aucun objet dans cette pièce.")` | A | vert |
| 40 | `FAIL: test_absence_etablie_par_fouille_reste_admise_apres_recharge (test_perception_geste.VueCouranteTests.test_absence_etablie_par_fouille_reste_admise_apres_recharge)` | A | vert |
| 41 | `FAIL: test_absence_visible_atelier_et_autre_salle_sans_fouille_apres_recharge (test_perception_geste.VueCouranteTests.test_absence_visible_atelier_et_autre_salle_sans_fouille_apres_recharge) (saisie='y a-t-il des outils qui traînent dans la cour ?')` | A | vert |
| 42 | `FAIL: test_absence_visible_atelier_et_autre_salle_sans_fouille_apres_recharge (test_perception_geste.VueCouranteTests.test_absence_visible_atelier_et_autre_salle_sans_fouille_apres_recharge) (saisie='y a-t-il des outils posés ici ?')` | A | vert |
| 43 | `FAIL: test_console_preuve_exacte_et_paraphrase_apres_recharge (test_non_perception.NonPerceptionTests.test_console_preuve_exacte_et_paraphrase_apres_recharge) (id='marchand', exacte=True)` | A | vert |
| 44 | `FAIL: test_console_preuve_exacte_et_paraphrase_apres_recharge (test_non_perception.NonPerceptionTests.test_console_preuve_exacte_et_paraphrase_apres_recharge) (id='marchand', exacte=False)` | A | vert |
| 45 | `FAIL: test_console_preuve_exacte_et_paraphrase_apres_recharge (test_non_perception.NonPerceptionTests.test_console_preuve_exacte_et_paraphrase_apres_recharge) (id='pied_de_biche', exacte=True)` | A | vert |
| 46 | `FAIL: test_console_preuve_exacte_et_paraphrase_apres_recharge (test_non_perception.NonPerceptionTests.test_console_preuve_exacte_et_paraphrase_apres_recharge) (id='pied_de_biche', exacte=False)` | A | vert |
| 47 | `FAIL: test_question_arrivee_est_un_dialogue_memorise (test_perception.QuestionsConsoleTests.test_question_arrivee_est_un_dialogue_memorise)` | A | vert |

Bruts complets : `C:/Users/msics/donjon/artifacts/up-319/reprise/attribution.json`, `reference.json`, `reference.log`, `branche.json`, `branche.log` et `fin-reprise.json` (`ok=true`). Les contrôles de monde et de rendu après recharge restent dans les fichiers de tests adaptés. Aucune nouvelle suite complète, aucun appel à Luna.
