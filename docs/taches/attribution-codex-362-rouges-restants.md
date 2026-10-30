# Lot 362 — annexe des seize méthodes

Base courante `52b2a27c`. Toutes les méthodes ci-dessous sont **rouges** lors du
rejeu initial natif, sans saut ni erreur de test. Les corrections/portages de la
branche sont distingués des huit méthodes réservées ci-dessous.

Les six premières bascules et celles des trois anciens non-reproduits sont établies par bissection des commits
`--first-parent` depuis `7eb45ff`, code **et tests natifs** de chaque archive.
Les bascules anciennes établies par le 356 sont citées depuis son annexe ; une
preuve historique n'est pas un verdict courant. Bruts `initial-valide/`,
`bissection/<commit>/`, `fin-bissection.json`, `fin-bissection-anciens.json` ; la passe `initial/` sous bac à sable
n'est pas une validation exploitable.

| Méthode | Bascule ; parent vert | Branche | Cause au rejeu courant ; traitement |
| --- | --- | --- | --- |
| `test_contre_offre.ContreOffreTests.test_service_poursuivi_par_pnj_meme_laps_decoupe` | `19c9b6da` / 358 ; `d35e91f3` | **Réservé** | Plus de souvenir de prêt de clé après le refus conservé. Réservé : levée du refus après contre-offre à instruire. |
| `test_inventaire_public.InventairePublicTests.test_projection_fermee_sans_contenu_cache_ni_personne_non_percue` | `09c079b0` / 354 ; `df03dc2f` | **Vert** | Homonyme caché inféré connu depuis les mots du contexte, exposé dans les sujets/ressources. Correctif de provenance des identités. |
| `test_offres_materielles.OffresMateriellesTests.test_conduite_reelle_et_lampe_choix_effet_et_vues_apres_recharge` | `b46fd689` / 353 ; `078c771d` | **Vert** | La sonde matérielle compte les nouveaux gestes corporels. Son périmètre est porté au catalogue documenté du 353. |
| `test_pas_compagnons.PasCompagnonsTests.test_promesse_hameau_1985_annoncee_retrouvee_apres_recharge` | `650f4198` / 306 ; `19c9b6da` | **Réservé** | Service de torche absent du registre final, autre service d'évacuation présent. Interaction évacuation/service réservé. |
| `test_service_non_defait.ServiceNonDefaitTests.test_hameau_1985_prestataire_mobile_bloc_decoupe` | `650f4198` / 306 ; `19c9b6da` | **Réservé** | Sonde : service payé réalisé puis état perdu. Même famille réservée, sécurité non affaiblie. |
| `test_verifier_eau.VerifierTests.test_lucien_demande_la_lampe_vue_et_la_reference_le_trouve_aussi` | `19c9b6da` / 358 ; `d35e91f3` | **Réservé** | La vente attendue à Bram pour 17 pièces n'a plus lieu ; les assertions précédentes passent. Levée du refus et nouvelle contrepartie à instruire. |
| `test_cache_kv_local.PrefixeKVTests.test_partage_du_prefixe_entree_entre_tours_relances_et_audit` | `64130fa1` / G6, preuve 356 ; `ad0e5a85` | **Vert** | Préfixe 0,819771819 < 0,85 : `parole_prevue` variable précède les attestations stables. Ordre corrigé, seuil conservé. |
| `test_correction_parole.CorrectionParoleTests.test_n9_propositions_historiques_apres_preparation_refusee` | `f091c64b` / 341, preuve 356 ; `368bf6c8` | **Vert** | Archives sans clés mandat : refus de forme avant la revue ; puis réponse G16 différente du faux récit. Carte complétée, réponse moteur attendue. |
| `test_echanges_argent.PretTests.test_le_proprietaire_qui_la_redemande_la_recupere_sauf_si_elle_sert` | `078c771d` / 333 ; `29529710` | **Réservé** | `absent` au lieu de `necessaire` après trois minutes autonomes. Reproduit isolément **et fichier entier (12 tests)** ; aucune adaptation. |
| `test_enfermer.EnfermerTests.test_assommer_trainer_verrouiller_temoin_reveil_et_decoupage` | `29529710` / 332 ; `0ababa39` | **Réservé** | Pas de souvenir `operation=enfermer` chez Gaspard malgré l'événement physique. Reproduit isolément **et fichier entier (11 tests)** ; aucune adaptation. |
| `test_enrichissement.EnrichissementTests.test_boucle_jeu_enregistre_et_conserve_action_en_attente` | `37dccfa3` / U-C, preuve 356 ; `dc6da621` | **Vert** | Un seul tenter affiche le nouvel aperçu après admission ; il ne perd pas le plan. Second accord explicite et absence d'effet avant lui vérifiés. |
| `test_installation_gardee.InstallationGardeeTests.test_demande_plutot_que_bris_et_laps` | `0ababa39` / 313 ; `34964df6` | **Réservé** | Plan initial de demande valide, mais intégrité finale de la porte nulle. Reproduit isolément **et fichier entier (7 tests)** ; aucune adaptation. |
| `test_lumiere.MineTests.test_une_lampe_vide_se_remplit_d_huile_puis_s_allume` | `8d439542` / 330, preuve 356 ; `9237e142` | **Réservé** | La lampe reste allumée ; trajet au bureau et extinction non établis. L'essai de stimulus explicite reste rouge : portage retiré, fichier restauré exactement à la base. Diagnostic plus large requis. |
| `test_n3_reformule.N3Tests.test_correction_contestee_aussi_le_secours_prononce_les_mots` | `f091c64b` / 341, preuve 356 ; `368bf6c8` | **Vert** | Cartes archivées incomplètes : protocole courant ajoute les clés d'opérations à false ; mots, types et deux refus sémantiques conservés. |
| `test_n3_reformule.N3Tests.test_fil_reel_et_question_dans_une_salle_eclairee` | `f091c64b` / 341, preuve 356 ; `368bf6c8` | **Vert** | Même défaut de protocole, deux scènes ; carte complétée sans changer les assertions mécaniques. |
| `test_recit.RecitTests.test_discuter_conserve_la_proposition_jusqua_tenter` | `37dccfa3` / U-C, preuve 356 ; `dc6da621` | **Vert** | Normalisation de la copie adoptée pendant la discussion : nouvelle signature conservatrice, même plan. Deux accords et aucun appel modèle à la confirmation vérifiés. |

Les huit méthodes réservées ne deviennent pas vertes par un changement d'assertion.
La suite globale n'est pas déclarée verte.

## Suites précises à ouvrir

- **358, deux méthodes** : tracer le refus reconnu par `refus_geste` pendant le plan
  conservé et déterminer le fait ou la contrepartie qui devrait le lever. Un nouvel
  accord ne doit ni contourner un refus toujours valable, ni être bloqué par celui
  d'une demande différente. Préserver prêt, paiement et termes exacts.
- **306, deux méthodes** : porter la règle déjà décidée « ne pas défaire un service
  payé » aux déplacements de sa source lors de l'évacuation, avec l'utilité crue
  pour le bénéficiaire. La règle ne promet pas d'entretien ; ces tests ne permettent
  pas de conclure qu'un départ du prestataire clôt légitimement le service.
- **313, installation** : attribuer le geste qui détruit la porte après le plan de
  demande, puis contrôler revalidation et responsabilité crue du prochain geste ;
  la bascule seule ne prouve pas que Brune est l'auteur du bris.
- **332, enfermement** : contrôler orientation et perception effectives de Gaspard
  pendant fermeture/verrouillage. Décider si la scène établit encore un témoin ou
  si le suivi du regard détourne légitimement celui-ci ; ne pas fabriquer sa connaissance.
- **333, rappel du prêt** : tracer les positions/perceptions après les trois minutes
  autonomes ; le contrat de rappel exige-t-il ici une approche préalable ? Ne pas
  remplacer le refus `absent` par un transfert à distance pour verdir le test.
- **330, lampe** : dater remplissage, allumage, changements de but et lumière perçue
  au bureau. Établir le stimulus réel de l'extinction avant de porter son oracle ;
  le seul placement sous une source de niveau 2 n'a pas suffi dans la reprise.
