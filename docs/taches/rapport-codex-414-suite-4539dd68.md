# Lot 414 — attribution des rouges de 4539dd68

31 octobre 2026, laptop ; `codex-suite-4539dd68`, base `integration d54d15ae`.
**Livraison partielle : attribution acquise, trois adaptations de tests ; aucun correctif moteur.**
Bruts : `C:/Users/msics/donjon/artifacts/suite-4539dd68-414/`.

**Preuve.** La liste fournie contient **30 méthodes distinctes**, toutes encore rouges
sur la base actuelle. Rejeu isolé, puis bissection des versions historiques des tests
sur la première parenté `c562aa21..4539dd68`, bornes vertes/rouges conservées :
**29 basculent au 374**, une au 381. Les étapes chaînées sont non monotones : déjà
rouges à la borne initiale, elles repassent vertes à `1fd48fb5`, puis rouges au 374.
`actuel/fin.json`, `bissection/attribution.json` et `fin-attribution.json` donnent
les traces, commits exacts et durées ; `complements/fin.json` prouve cette seconde
bascule et `fin-livraison.json` consolide les résultats. Deux travailleurs réduits au plus ; pas de
suite complète ni de Luna. Le premier lancement invalide (chemin d'import) est exclu.

**Adaptations justifiées.** P : le [374](rapport-codex-374-position-hypothese-datee.md)
expire la position du marchand au même saut de temps que le refus. Le test exige
d'abord l'inspection, puis apprend une position neuve avant d'éprouver de nouveau
la demande et son refus ; monde, plan et vues sont aussi vérifiés après recharge.
D : la fausse vue fournit les dépendances introduites par la vérification des
positions (`monde`, `id`, `personnes`) ; assertions de lumière/discrétion inchangées.
M : le [381](rapport-codex-381-a2-passage.md) exige un outil non vide pour l'appui
mobile. Le test exige ce refus typé au MJ, la clarification publique sauvegardée,
aucun déplacement et aucun journal d'action, au lieu du refus mécanique antérieur.

**Questions ouvertes.** R : l'expiration retire le témoin de `obstacle_patience` ;
surtout, `_normaliser_suites` substitue au geste furtif une recherche de personne,
dont le préfixe ne porte plus le geste bloqué. Dans la capture Odon 31, la proposition
est « demander à Bram où est Gaspard », avec le même but d'agenda que le crochetage
retenu. Comment conserver la cause du plan pendant ce préfixe sans bloquer un autre
moyen légitime ? Une correction limitée au dernier lieu du témoin ne suffit pas
(rejeu `reessai-corrige.json` toujours rouge) : elle a été retirée. Les cinq oracles
restent intacts. C : faut-il une vérification unique de position ou un nouveau contact,
et quelle preuve autorise sa reprise ? Ces cas recouvrent les appels/consommations du
**413** ; aucun de ses fichiers moteur n'est modifié ici. E : les empreintes changent
avec le comportement du 374 ; distinguer les décisions voulues des défauts avant
tout réancrage. Les autres questions précises figurent dans la dernière colonne.

Noms ci-dessous : fichier et méthode, sans les préfixes `test_`. **374 = `c3f0c2d5`**
(parent vert `1fd48fb5`) ; **381 = `62142fbe`** (parent vert `cd77998a`).

| Méthode | Fusion | Cause observée ; correction ou question |
|---|---|---|
| achat_promis_annule : capture_reelle_avant_36582_bloc_et_decoupe | 374 | Offre à 40267 au lieu de 36477 ; C, quel contact retarde l'offre et l'annulation ? |
| agendas_activation : deux_parcours_parole_reception_et_rendu_recharges | 374 | Plus de plan pour le marchand ; C, quelle position manque à la transmission ? |
| amener_flamme : capture_1985_avant_premier_allumage_sans_cycle | 374 | Extinctions après 213 ; quelle vérification rouvre le cycle d'entretien ? |
| completion_preuves : captures_reelles_plans_et_absences_prix_recharge_et_rendu | 374 | Quatre empreintes du monde diffèrent ; E, attribuer chaque différence avant réancrage. |
| contre_offre : condition_impossible_retenue_sans_offres_aleatoires_ni_delai | 374 | Inspection du marchand au lieu de `None` ; C, vérification unique ou réessai du refus ? |
| depart_feutre : la_decouverte_ne_deplace_pas_les_lectures_de_lumiere | 374 | Fausse vue sans `personnes` ; D, adaptée. |
| dynamique_besoins : lucien_attend_une_information_apres_la_reprise_du_ballot | 374 | Recherche ne couvrant plus toutes les salles ; C, arrêt voulu par consommation ou perte de recherche ? |
| dynamique_besoins : lucien_rapporte_la_lanterne_de_l_etable_au_grenier_au_lieu_d_aller_et_venir | 374 | Passages supplémentaires après retour ; quelle preuve nouvelle justifie chacun ? |
| eau : l_eau_qui_monte_fait_fuir_vers_la_galerie | 374 | Estimation d'Ilse absente à 80 ; quelle décision empêche son observation de l'eau ? |
| empathie_peur : gorm_attend_un_moyen_sur_pour_le_feu_mais_execute_encore_sa_ronde | 374 | Question à Aubin sur Mael à 85 ; C, vérification unique ou reprise sans moyen neuf ? |
| empathie_peur : lecture_retenue_revisee_par_un_dementi_percu_et_non_par_le_regard | 374 | Détresse encore retenue après démenti attendu ; le démenti a-t-il réellement été perçu dans la nouvelle trajectoire ? |
| etapes_chainees : captures_mine_et_auberge_memes_plans_visites_monde_et_rendu_recharges | 374 | Re-verte à `1fd48fb5`, re-rouge à `c3f0c2d5` ; assertions de faits/offre échouent, E. Ancien rouge à `663d1308`/`c562aa21` conservé dans les bruts. |
| gardien_detresse : capture_reelle_appel_deja_lance_biscuits_epuises_et_pas_de_boucle | 374 | Compteur de cris 1/0 ; quel contact remplace l'appel et sa preuve dans la chronique ? |
| gestes_par_noeud : successeurs_ordre_couts_et_noeuds_de_la_base | 374 | Successeurs/empreintes différents ; E, séparer préfixes voulus et régressions. |
| mj_restes : meme_nature_grimper_sans_appui | 381 | Outil vide désormais refusé en forme ; M, adaptée. |
| offre_sensee : refus_recharge_ne_repart_pas_avec_fortune_ou_biens_retrouves | 374 | Recours absent même après ressource neuve, deux interlocuteurs ; C, manque-t-il leur localisation neuve ? |
| planification : une_croyance_une_limite_ou_l_horloge_relancent_la_recherche | 374 | Inspection au lieu de demande après expiration ; P, adaptée. |
| propositions_redites : capture_mine_interlocuteur_inaccessible_hele_et_interrompt_l_attente | 374 | Bram non localisé au lieu de bureau ; C, quelle enquête remplace l'appel attendu ? |
| recours_agenda : capture_317_constat_et_laps_apres_recharge | 374 | Gorm repart à 171 après constat ; quelle preuve rouvre ce trajet ? |
| recours_prioritaire : aide_capture_541_meme_monde_et_vue_laps_decoupes | 374 | Intention absente ; C, l'aide adoptée perd-elle ses moyens ou seulement sa cible localisée ? |
| recours_prioritaire : aide_historique_adoptee_independante_du_classement | 374 | Même absence d'intention ; C, quelle preuve conditionne sa reprise ? |
| reessai_obstacle : essayer_un_autre_moyen_ne_fait_pas_oublier_le_premier_obstacle | 374 | Même but repris après deux renoncements ; R. |
| reessai_obstacle : faim_renoncee_attend_un_moyen_dans_les_deux_captures_reelles | 374 | Sortie de l'attente sur les deux captures ; R. |
| reessai_obstacle : la_ronde_ordinaire_reverifie_sans_reprendre_le_coffre | 374 | Agenda remplace la ronde ; R. |
| reessai_obstacle : odon_pas_de_reprise_par_delai_ni_date_de_regard | 374 | Même agenda repris au seul délai ; R. |
| reessai_obstacle : odon_reprend_sur_absence_constatee_pas_sur_la_verite_cachee | 374 | Reprise avant constat d'absence ; R. |
| refus_retenus : mireille_ne_repropose_pas_l_impossible_puis_le_repropose_quand_elle_apprend_du_bois | 374 | Collision Hugues/Mathurine après `face_a_face` ; déplacement d'auteur sur case occupée ou collision préalable du moteur ? |
| signalements : hugues_auberge_11_devoir_sans_tache_restante | 374 | Inactivité non satisfaite ; quelle vérification est encore requise après la charge ? |
| signalements : auberge_3_un_rendez_vous_ne_relance_pas_la_tournee | 374 | Aucun cri pendant la recherche ; C, quelle substitution et quelle borne pour le rendez-vous ? |
| temps_reel : cas_reel_brune_renonce_apres_trente_minutes_de_guet | 374 | Fin à 19200 contre borne 18600 ; nouvelle préparation légitime ou remise à zéro de patience ? |

**Validation finale : trois méthodes adaptées vertes ; 35/37 tests verts** sur les
trois fichiers touchés, zéro échec et deux erreurs hors liste. Départ feutré : 6/6
(58,4 s, `adaptations-fichiers.json`) ; planification : 15/15 (81,1 s) ; MJ restes :
14/16 (57,6 s), `adaptations-finales.json`. Les deux erreurs (`DetailHorsDePorteeTests` :
`test_un_detail_d_un_objet_trop_loin`, `test_une_description_physique_d_un_objet_trop_loin`)
reproduisent leur même `KeyError: retour_moteur` sur la base exacte `d54d15ae`,
sans les adaptations (`complements/fin.json`). Elles restent hors périmètre : le
renvoi de forme doit-il remplacer le renvoi mécanique attendu par ces deux tests ?
Aucun fichier de production livré ; pas de banc de comportement pour ces seules adaptations.
Les 27 autres méthodes restent ouvertes, sans garantie de correction des décisions
du 374 ni d'absence générale de boucles. La fusion reste au superviseur.
