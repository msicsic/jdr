# Lot 197 b — triage et crédit du froid

Reprise sur `47ac3f1`, base `116294e`. `services.conditions_manquantes` ajoute le
froid éprouvé du bénéficiaire avant geste, pour un foyer dans sa salle : même
condition d'entretien, constat d'effet, perception et épreuve `service_rendu`.
Aucun accès privé ajouté au choix de l'auteur. Les charges identiques sont
dédupliquées ; prestations convenues exclues du second crédit. Cas PNJ/joueur,
manque absent/distant, geste non vu/sans effet, preuve répétée et charge convenue
vérifiés après recharge. Peur hors lot ; aucun Luna, deux travailleurs réduits.

**313 tests ciblés / 26 fichiers, 278,440 s : quatre échecs, zéro erreur**
au bilan intermédiaire : deux MiMo historiques et deux régressions de références.
Le raccord autorisé est appliqué : trois lignes dans `echanges.detacher_part`,
installateur commun appelé dès création des portions physiques et comptées.
**Fusion avec le lot 198 : même fichier, seuls ces trois ajouts pour 197 b.**
Les comparaisons d'état complet sont vertes, secours actifs, aucun champ exclu.
Le test des lampes contrôle les deux preuves canoniques d'audience : Rémy peut
annoncer une lampe devant Lucien ; Josse n'a plus à la répéter. **33 ciblés
consolidés verts**. **Suite complète unique : 2 364 tests / 274 fichiers,
1 982,678 s, deux échecs MiMo historiques et une erreur nouvelle.** Cette erreur
de `test_agendas_socle` est corrigée dans `services.constater` : les états visibles
sont déjà enregistrés sous `etat` par le constat commun ; aucun attribut autonome
`allume` ne doit être ajouté. Cas réel inchangé et allumage complémentaire après
recharge : **24 tests / 3 fichiers verts, 19,304 s**. Bilan consolidé : seulement
les deux MiMo historiques, zéro erreur ; pas de seconde suite complète. Aucun
nouveau banc : les mesures de 197 a ci-dessous restent historiques. Bruts et captures : `C:/Users/msics/donjon/artifacts/empathie-197/b/`.

Les tests de contexte utilisent des profils d'auteur explicitement sans souci
spontané, jamais un patch du moteur. Seul le contrôle causal diagnostique utilise
une neutralisation temporaire, hors tests livrés. Le repas après appel est vérifié
plus strictement par réception et satiété. Le tableau en annexe classe chacun
des 34 constats initiaux, sous-cas compris, avec cause observée et décision.

---
# Lot 197 a — bilan historique de la livraison partielle

`codex-empathie`, non fusionnée, base finale **`integration 116294e`** (186 annulé,
194/180 intégrés). Ancien banc sur `9c1897f` et suite interrompue : **obsolètes**,
archivés sous `avant-integration-9c1897f/`. Aucun Luna, scénario ni fichier réservé
retouché après fusion. Bruts exclusivement `C:/Users/msics/donjon/artifacts/empathie-197/`.
Aucune clé Git de signature configurée : commit non signé.

**Changement.** `deliberation.secours` transforme faim/froid observés en conditions
communes `servir`/`allume`, tant que le bénéficiaire reste perçu. Souci du lot 80 :
altruisme + empathie + affection ≥ 100, rancune exclue ; poids empathie × (affection + 20)/100.
`Palier.SECOURS` suit besoins propres/maintien, précède routine/argent. Foyer connu
dans la salle crue du transi ; aucun besoin privé, droit ou mandat inventé,
aucune lecture nouvelle dans la recherche (`_entrees` inchangé).

**Vérification.** 26 ciblés consolidés verts : Mathe/Lucien sans charge, repas unique,
un crédit `service_rendu` ; transi PNJ/joueur, feu entretenu ; hostilité, souci faible,
dos/noir, absence/apaisement après choix, faim propre prioritaire. Monde/rendu/journal
rechargés, temps entier/découpé identiques. Charge historique de Mathe isolée des
secours concurrents ; oracle A0 sans nouveaux secours, éprouvés séparément. Deux
tests supplémentaires vue pure/mémo verts. **Suite finale unique : 2 361 tests,
274 fichiers, 1 887,048 s ; 30 échecs et 4 erreurs dans 24 fichiers**, dont deux
MiMo historiques. Anciens appels/demandes/vols/positions encore en échec, attribution
incomplète : **aucune validation générale de 3d**, aucun bilan vert revendiqué.

**Banc final : 20 paires de 4 h**, cinq scénarios × 1985/7/42/2024, même base exacte ;
références absentes constituées une fois. **21 repas d'empathie dans 13/20 nuits**,
aucun entretien de feu sous ce motif en nuit libre. Zéro plantage/usurpation.
Vingt sauvegardes/rendus stables après préparation : en crue 2024, `sauver` complète
seulement `references_personnes/planches_1 = 48` avant écriture ; rien au rendu ni
à la recharge. Rejeu ciblé : nuit/chronique identiques, aucun champ exclu.

| Scénario | Repas / nuits | Sans recours, base → lot | S/F/D moyens (définitions 183), base → lot |
|---|---:|---:|---|
| Relais | 1 / 1 | 60 → 0 | 6,75/4,25/1,188 → 8,5/4,25/1,625 |
| Mine | 8 / 4 | 55 → 0 | 13,25/4,75/1,214 → 23/4,75/1,857 |
| Auberge | 8 / 4 | 65 → 80 | 6,5/2,75/0,625 → 11/4/0,969 |
| Crue | 1 / 1 | 220 → 60 | 17,25/6,25/1,938 → 18/6/2,438 |
| Hameau | 3 / 3 | 235 → 0 | 20,5/6,25/1,542 → 23,5/6,5/2,042 |

Sans recours **635 → 140 min** ; hausse auberge : biens de Lucien (+15 min).
Nouvelles alertes : charges immobiles, alternance de bruit ; Gorm/crue 7, neuf
réveils d'agenda ; Brune/crue 2024, huit sommeils. Hameau : Brune attend avec froid
pressant 135 min (1985), reste dans l'eau 80 min (7), dans le noir 95 min (42).
Pics de passages/h : 9/10/15/46/52 → 10/9/18/38/27. **Absence de nouvelle boucle
non démontrée** ; minutes causalement apaisées par autrui non mesurées ; aucun CPU comparé.

**Souci initial.** Relais : Gorm 55/Ilse 65 → tous + joueur ; Aubin 45 → Gorm/Brune/Ilse ;
Brune 40 → personne. Mine, tous à 50 : tous → tous + joueur sauf Bram (exclut
Odon/joueur) et Odon (Gaspard/Josse seulement). Auberge, tous à 50 : tous + joueur,
sauf Anselme (personne). Crue/hameau : tous + joueur, empathie 50, Maël/Sève 65.
« Tous » exclut soi. **Aucun profil ≥ 70** : le critère « aucun secours sans
empathique ≥ 70 » n'est pas satisfait ; aucun nouveau seuil ni scénario ajouté.

**Reste.** Peur : terminal de proximité, maintien/fin sur signes perçus, coûts et
clés cohérents. Crédit commun du froid corporel sans pulsion/agenda à étendre dans
`services.py`, sans exception d'empathie ; froid prouvé seulement en scènes ciblées.
**L'invariant complet 3d reste ouvert.** Deux travailleurs réduits au plus.


## Lot 197 b — triage des 34 constats de la suite 197 a

Contrôles causaux diagnostiques : chaque méthode rejouée avec secours actifs puis neutralisés uniquement dans la sonde ; seules les deux assertions MiMo restent fausses sans secours. Les tests livrés utilisent des données explicites, jamais cette neutralisation. Captures initiales dans `b/diagnostic-initial.zip`, décisions détaillées dans `b/triage.json`.

| Test / sous-cas initial | Classe | Cause constatée | Décision, sans affaiblir le contrat |
|---|---|---|---|
| `test_appel_negocie.IciViensTests.test_cas_reel_gorm_croit_la_porte_fermee_aubin_vient` | a | Gorm veut servir Aubin spontanément ; sa marche vers les vivres modifie le premier appel attendu. | Souci de Gorm absent ; réponses, immobilité pendant la parole et appel unique conservés. |
| `test_appel_negocie.JArriveTests.test_qui_cherche_l_appelant_vient` | a | Gorm poursuit le repas pour Aubin et change le rendez-vous, ce qui fait rappeler Aubin. | Souci de Gorm absent ; mêmes assertions de rendez-vous et de repas demandé. |
| `test_attente.AttenteTests.test_un_appel_entendu` | a | Aubin inspecte pour nourrir Brune ; cet événement interrompt à 30 s l’attente prévue plus longue. | Aucun souci spontané dans cette scène ; faim d’Aubin, appel audible et durée restent contrôlés. |
| `test_avis_redits.AvisReditsReelsTests.test_mine_2024_deux_lampes_homonymes_restent_deux_faits` | b | Les secours créent biscuits_1 et vivres_1 ; leurs références 67/68 sont attribuées à la sauvegarde dans un ordre dépendant du découpage. Mécanique, chronique et rendus identiques. | Raccord commun autorisé appliqué à detacher_part ; comparaison complète inchangée. Puis (a) : Rémy annonce une lampe devant Lucien ; deux identités et deux preuves d'audience explicites, dont celle entendue, remplacent l'attente d'une redite de Josse. |
| `test_boucles_pnj.GesteDefaitTests.test_odon_ne_rouvre_pas_ce_que_mathe_vient_de_refermer` | a | Mathe sert Odon ; sans elle, Josse/Gaspard/Lucien/Rémy peuvent encore tenter de le nourrir et rouvrir pour une autre tâche. | Scène sans souci spontané de tous ; charges et motivation d’Odon inchangées, bornes de gestes conservées. |
| `test_combat.CombatTests.test_meme_laps_y_compris_embuscade_en_cours` | b | Les achats de portions pour aider Brune créent vivres_2 ; la référence 48 existe seulement après la recharge du chemin découpé. Aucun autre champ ne diffère. | Raccord commun autorisé appliqué à la création ; capture avant/après et comparaison intégrale vertes, sans exclusion de champ ni suppression du secours. |
| `test_constater_rumeurs.ChercherQuelquUnTests.test_le_joueur_qui_ne_les_connait_pas_n_entend_que_des_voix` | a | Hugues nourrit Mireille ; Tilo cherche aussi des vivres pour elle. Mireille rassasiée ne cherche plus Odile. | Hugues/Tilo sans souci dans la scène commune ; assertions de voix inconnues et absence de fuite nominale intactes. |
| `test_constater_rumeurs.ChercherQuelquUnTests.test_mireille_appelle_odile_dans_le_grenier_noir` | a | Hugues donne ses biscuits à Mireille avant son appel ; la cause de sa recherche disparaît. | Hugues/Tilo sans souci ; faim et recherche d’Odile dans le noir restent réelles. |
| `test_constater_rumeurs.ChercherQuelquUnTests.test_qui_se_mefie_ne_repond_pas` | a | Le même repas de Hugues supprime l’appel dont le test doit éprouver le refus. | Même scène explicitement sans secours de Hugues/Tilo ; refus de répondre inchangé. |
| `test_constater_rumeurs.ContenantFermeTests.test_brune_trouve_la_reserve_refermee_a_cle_et_la_croit_toujours_pleine` | a | Gorm nourrit Brune : elle n’a plus à chercher ses crochets après le constat du verrou. | Souci de Gorm absent ; croyances de serrure, vivres et prise des crochets toujours contrôlées. |
| `test_crochetage_surenchere.CrochetageDuJoueurTests.test_son_bruit_tient_a_son_jet` | a | Ilse/Aubin cherchent une part pour Brune ; leur activité acoustique fait venir Gorm indépendamment du crochetage. | Ilse/Aubin sans souci ; les deux jets et les mêmes bornes de bruit/examen restent vérifiés. |
| `test_defense.ForcerNEstPasAgresserTests.test_un_temoin_de_l_effraction_ne_la_fuit_pas (temoin='marchand')` | a | Le témoin Gorm nourrit Brune avant l’effraction : aucun coup illicite à observer. | Témoin sans souci ; effraction réelle, souvenir vu_agir et absence de fuite/riposte restent exigés. |
| `test_depart.DivergenceDuBancTests.test_le_depart_tire_fait_diverger_les_nuits` | a | Les demandes/achats d’Aubin pour Brune tirent des dés indépendants du départ ; deux empreintes fixes remplacent une. | Seulement dans cet oracle, profils sans souci comme marchés/nouvelles déjà isolés ; égalité fixe et diversité tirée inchangées. |
| `test_echanges_suite.PretReclameTests.test_rendue_a_temps_rien_ne_lui_est_reproche` | a | Gaspard part chercher du pain/vivres pour Rémy/Odon ; il n’est plus à portée de main pour la restitution. | Gaspard sans souci avant les deux minutes ; contrôle de portée et restitution à temps non contournés. |
| `test_fournisseurs_jeu.ParcoursFournisseursTests.test_mimo_correction_avant_action_sur_deux_scenes (cas='atelier', fournisseur='mimo')` | b historique | 6 appels MiMo au lieu de 5 ; même échec avec secours neutralisés dans le contrôle diagnostic. | Exception historique expressément autorisée ; test et fournisseur inchangés. |
| `test_garde_plan.GardeDuPlanTests.test_mine3_capture8_service_sans_urgence_et_recharge` | a | Mathe sert Odon et Rémy nourrit Lucien : la charge propre de Mathe n’a plus de repas à servir à Lucien. | Dans cette seule fabrique, absence de souci libre avant les 8 minutes ; charge de Mathe, état complet/recharge et bornes de fermeture intacts. |
| `test_intermediaires.IntermediairesTests.test_cible_mefiante_echoue_sans_boucle` | a | Gorm donne librement une part à Brune malgré l’échec de la commission : stock 7 au lieu de 8. | Scène sans souci spontané ; refus, absence de livraison et nombre de demandes du mandataire inchangés. |
| `test_intermediaires.IntermediairesTests.test_deux_chaines_rechargees_et_meme_laps (auberge=False)` | a | Le fournisseur sert gratuitement Brune/Joss en plus de la commission ; Odile/Mireille peuvent proposer un autre repas : deux portions. | Scène sans souci libre, charges et liens conservés ; un seul transfert, commission aboutie et temps découpé identique restent exigés. |
| `test_intermediaires.IntermediairesTests.test_deux_chaines_rechargees_et_meme_laps (auberge=True)` | a | Le fournisseur sert gratuitement Brune/Joss en plus de la commission ; Odile/Mireille peuvent proposer un autre repas : deux portions. | Scène sans souci libre, charges et liens conservés ; un seul transfert, commission aboutie et temps découpé identique restent exigés. |
| `test_parole_voix.RejointTests.test_s_il_le_cherche_aussi_il_va_vers_lui` | a | Gorm poursuit un secours au lieu du trajet historique. Sans ce souci, la part est réellement achetée après contre-offre, formulation condition remplie exclue par l’ancien détecteur. | Gorm sans souci ; demande conservée et attendu renforcé : souvenir nourri de Gorm et faim sous 70, plutôt qu’une seule phrase d’accord. |
| `test_petits_correctifs.PartPayeeTests.test_la_promesse_expiree_la_dette_est_reclamee` | a | Aubin cherche Gorm pour nourrir Ilse ; ses appels déplacent aussi Ilse. La promesse expire bien, puis Ilse rejoint Gorm et obtient déjà les 2 pièces dans la même minute : dette soldée, bourses 8/50, au lieu de dette encore ouverte 6/52. | Aubin sans souci ; expiration, montant exact de dette et remboursement continuent d’être vérifiés. |
| `test_proposer_recours.RecoursTests.test_crue_offre_avant_faute_et_part_acceptee_deux_auditeurs (autre='marchand', confiance=10)` | a | Le fournisseur Gorm/Aubin sert Brune spontanément ; rassasiée, elle n’a plus à crocheter après l’offre refusée. | Scène sans souci spontané ; ordre offre avant faute, stock, finances et réussite/refus du marché inchangés. |
| `test_proposer_recours.RecoursTests.test_crue_offre_avant_faute_et_part_acceptee_deux_auditeurs (autre='aubin', confiance=10)` | a | Le fournisseur Gorm/Aubin sert Brune spontanément ; rassasiée, elle n’a plus à crocheter après l’offre refusée. | Scène sans souci spontané ; ordre offre avant faute, stock, finances et réussite/refus du marché inchangés. |
| `test_refus_retenus.PartImpossibleTests.test_ilse_ne_redemande_pas_puis_redemande_quand_elle_sait_la_cle` | a | Aubin recherche/achète pour Ilse et Gorm agit sur les vivres : moyen nouveau légitime, donc une redemande promise apparaît avant la clé injectée. | Aubin/Gorm sans souci ; même refus mémorisé puis réouverture uniquement sur clé apprise. |
| `test_rendez_vous.RendezVousTests.test_capture_reelle_auberge_42_une_retrouvaille_et_la_demande_reprend` | a | Tilo/Mathurine/Mireille entreprennent de nourrir Joss et modifient les mouvements de la capture ; aucune retrouvaille historique. | Ces trois tiers sans souci ; deux replays, annonce unique par replay, état/rendu complets et demande restent exigés. |
| `test_rendez_vous.RendezVousTests.test_relais_appele_qui_vient_et_l_appelant_ne_le_cherche_plus` | a | Gorm initie un repas pour Aubin : les nouvelles rencontres/déplacements produisent deux annonces. | Souci de Gorm absent ; une seule retrouvaille et absence de rappel restent exigées. |
| `test_ressources.CrueTests.test_on_monte_se_chauffer_au_poele_du_guet_et_le_bois_reste_compte` | a | Gorm entreprend d’entretenir le poêle pour un autre transi ; le foyer reste allumé. | Scène de chauffage propre sans souci libre ; même comptage de tous les stocks et vérification de l’accès au poêle. |
| `test_restes_fusions.RestesFusionsTests.test_mimo_rejets_et_actions_sur_deux_scenes_apres_reprise` | b historique | Même assertion MiMo 6 != 5 dans le parcours partagé, encore fausse avec secours neutralisés. | Exception historique autorisée ; aucune modification du test. |
| `test_social.DesespoirTests.test_sinon_elle_attend_que_personne_ne_la_voie` | a | Ilse/Gorm cherchent à nourrir Brune ; après la part, son intention de vol disparaît. | Ilse/Gorm sans souci ; Brune reste affamée et doit attendre une vraie absence de témoin. |
| `test_tensions.PartTests.test_brune_demande_d_abord_et_gorm_la_sert` | a | Ilse/Aubin demandent et servent aussi Brune ; plusieurs sorties du stock, au lieu d’une livraison seule. | Scène sans souci spontané ; demande promise, une portion, réserve verrouillée et satiété inchangées. |
| `test_tensions.PartTests.test_ilse_sans_le_sou_retient_la_condition_sans_redemander_avec_le_temps` | a | Gorm sert Ilse et Aubin lui achète une autre part : stock 2 au lieu de 4 malgré son refus personnel. | Scène sans souci libre ; refus/contre-offre et seuil de redemande restent inchangés. |
| `test_tensions.PartTests.test_refusee_brune_se_tourne_vers_le_vol` | a | Les tiers Ilse/Aubin/Gorm agissent sur les vivres pour Brune ; son parcours de refus/vol est remplacé. | Scène sans souci libre ; même refus effectif, but manger et faute sans_temoin exigés. |
| `test_voix.HelerTests.test_aubin_hele_gorm_a_travers_la_porte_etanche` | a | Gorm poursuit le repas pour Aubin, modifiant le premier aller-retour et le nombre d’appels. | Gorm sans souci ; un appel, réponse à travers la porte, nourriture et voix inconnue inchangés. |
| `test_voix_inconnues.VoirParlerTests.test_voir_gorm_repondre_a_aubin_fait_connaitre_sa_voix` | a | Gorm/Ilse entreprennent le repas pour Aubin ; la réponse n’est plus prononcée sous les yeux du joueur. | Gorm/Ilse sans souci ; demande et apprentissage effectif des deux voix restent exigés. |

### Erreur découverte par la suite finale 197 b

| Test | Classe | Cause | Décision |
|---|---|---|---|
| `test_agendas_socle.ChaineTests.test_tache_payee_acceptee_puis_abandonnee` | b | Un allumage utile à un témoin transi fait enregistrer `allume` comme attribut de croyance autonome dans `services.constater`, en plus du bon `etat`. La copie suivante rejette ce monde invalide. | Conserver le constat commun des états visibles, ne créer de croyance autonome que pour les autres effets. Test historique inchangé, sous-cas complémentaire d’allumage et recharge ; 24 ciblés verts. |

Capture de la promesse expirée : `b/expiration-originale.json` et monde complet associé ;
la dette y est réellement créée puis remboursée. Suite brute : `b/suite-finale.json` ;
correction ciblée : `b/correction-allumage.json` ; bilan composé traçable :
`b/bilan-consolide.json`. Commit non signé : aucune clé Git configurée.
