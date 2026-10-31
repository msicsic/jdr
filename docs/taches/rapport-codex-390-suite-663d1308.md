# Lot 390 — Attribution des rouges de 663d1308

Branche `codex-suite-663d1308`, base d'intégration `70b2fdfa`, PC fixe.
Code vérifié `a351d07d` ; lot clos avec les limites ci-dessous, aucun calcul actif.
Bruts : `C:/Users/msics/donjon/artifacts/suite-663d1308-390/`.

**Attribution.** Bissection des seules méthodes signalées, sur les arbres historiques
de la première parenté `e0826efc..663d1308`, deux travailleurs réduits au plus.
Les commits purement documentaires sont sautés ; versions historiques du moteur
et des tests, traces et bornes conservées dans `bissection/attribution.json`.
**27 bascules attribuées.** Deux méthodes supplémentaires, déjà rouges à la borne
initiale, relèvent explicitement du 375 : `intermediaires.test_deux_chaines_rechargees_et_meme_laps`
et `passage.test_cas_reel_acceptee_elle_s_ecarte_vraiment`. Elles restent intactes,
comme les autres méthodes du 375 et les cinq du 387. Le premier lanceur masquait
le namespace `tests` ; ses résultats invalides restent séparés des mesures corrigées.

**Contrat corrigé (V).** Une voix nette effectivement reçue est mémorisée dans
`ouie._au_joueur` avant le lien de l'échange et le rendu événementiel. Auparavant,
`ecoute.retenir` n'intervenait qu'en fin d'action : le rendu du 376 pouvait alors
nommer une identité cachée ou dire « personne inconnue », faute de référence vocale.
Le stockage existant, sa date acoustique et les contrôles de portée sont réemployés.
Aucun registre, exception de scénario, prompt ni nouvelle vérité sur le locuteur.

**Adaptations documentées (T).** Le test d'Hugues garde le savoir à l'instant de la
parole, sans lui prêter le nom appris ensuite (rapport 376). Le refus `patienter`
vérifie le champ reçu et la valeur admise (rapport 370). Le test d'examen fermé
retire explicitement le savoir initial de l'anneau introduit en 365 ; son refus
d'accès reste exigé. L'oracle du salut inclut la précision sonore annoncée en 379,
en gardant ses assertions d'effets, de relecture et d'absence de récit inventé.

Les noms ci-dessous sont ceux des méthodes ; les préfixes `test_` des fichiers
sont omis. V = correction de réception ; T = attente/prémisse adaptée ; Q = suite à ouvrir.

| Fichier / classe : méthodes | Fusion fautive | Cause ; traitement |
|---|---|---|
| appel_negocie/FormesTests : test_formes | 376 `69ae6101` | Référence vocale absente au rendu ; V |
| appel_negocie/JoueurHeleParUnPnjTests : test_j_arrive_puis_ne_vient_pas, test_qu_est_ce_que_tu_veux, test_viens_et_il_vient, test_viens_quand_il_ne_peut_pas_venir | 376 `69ae6101` | Même cause ; V |
| constater_rumeurs/ChercherQuelquUnTests : test_le_joueur_qui_ne_les_connait_pas_n_entend_que_des_voix, test_un_autre_appelant_reel_est_entendu_sans_reveler_son_identite | 376 `69ae6101` | Même cause ; V |
| voix/HelerTests : test_aubin_hele_gorm_a_travers_la_porte_etanche, test_hugues_hele_anselme_a_travers_la_porte | 376 `69ae6101` | Réception tardive / savoir ultérieur ; V, T |
| voix_inconnues/RepondreTests : test_cas_reel_corvus_repond_a_gorm_qui_le_hele, test_formes, test_ici_entre_guillemets_d_une_voix_connue, test_le_mj_ne_repond_qu_a_qui_vient_d_appeler | 376 `69ae6101` | Référence vocale absente au rendu ; V |
| voix_inconnues/VoirParlerTests : test_une_voix_qui_dit_son_nom_se_dit_ainsi | 376 `69ae6101` | Même cause ; V |
| rendez_vous/RendezVousTests : test_joueur_appelant_et_appele_reprise_sans_luna | 376 `69ae6101` | Même cause ; V |
| question_absent/QuestionAbsentTests : test_reponses_a_un_appel_gardent_leur_mecanique_distante | 376 `69ae6101` | Même cause ; V |
| refus/AttenduTests : test_patienter_dit_ses_champs | 370 `945be639` | Refus désormais précis ; T |
| refus/AttenduTests : test_objet_dans_un_contenant_ferme_demande_de_l_ouvrir | 365 `fdbc6ed0` | Anneau connu par prémisse ; T |
| luna_noms/NarrationTests : test_l_approche_structuree_ne_devient_pas_la_description_du_geste | 379 `3f50e6c2` | Compris sonore enrichi ; T |
| contact_position_inconnue/ContactPositionInconnueTests : test_contenant_dans_une_autre_salle | 376 `69ae6101` | Messages différents selon découpage ; Q1 |
| reprise_contact/RepriseContactTests : test_ilse_capture_141000_pas_de_reprise_par_la_minute | 376 `69ae6101` | Sons supplémentaires dans le bloc ; Q1 |
| etapes_chainees/EtapesTests : test_captures_mine_et_auberge_memes_plans_visites_monde_et_rendu_recharges | 376 `69ae6101` | Empreintes du monde changées ; Q1 |
| garde_ouidire/GardeOuidireTests : test_preuves_sans_porteur_salle_et_contenant_transmises_et_rechargees | 365 `fdbc6ed0` | Référence de lieu non admise dans le rendu ; Q2 |
| mandat_joueur/MandatJoueurTests : test_charge_du_banc_apres_information_sans_jet_force | 365 `fdbc6ed0` | Références du mandat refusées comme inconnues ; Q2 |
| occasions_scenarios/OccasionsScenariosTests : test_inverse_ne_retire_que_les_occasions_du_lot | 365 `fdbc6ed0` | Savoirs de prémisse ajoutés aux données hachées ; Q2 |
| intermediaires/IntermediairesTests : test_bien_durable_livre_par_le_meme_contrat | 377 `d1c3d1f9` | Bien durable non livré après réservation ; Q3 |
| livraison_inconnue/LivraisonInconnueTests : test_devis_plan_et_empeche_purs_independants_du_lieu_cache | 377 `d1c3d1f9` | Nouvelle copie validée, placement artificiel hors du sol ; Q3 |

**Limite de livraison.** Les huit méthodes Q restent attribuées, sans oracle assoupli.
Q1 : à quel événement le bloc perd-il la parité acoustique, et quels champs expliquent
les empreintes ? Q2 : quelles connaissances publiques les scènes doivent-elles déclarer,
et comment comparer les données historiques sans retirer les savoirs décidés en 365 ?
Q3 : la commission réserve-t-elle deux fois son propre moyen, et quelles cases d'auteur
valides permettent de continuer le contrôle de pureté du devis ? Lots suivants bornés.
Recouvrements : `ouie.py` avec le socle S1 déjà fusionné ; aucun fichier de code de
374/380/381/389 modifié. Ni Luna ni suite complète ; fusion laissée au superviseur.

**Tests consolidés : 204/214 passent, vingt fichiers.** Les neuf fichiers du
correctif apportent 129 succès ; les onze voisins, 75/85 (161,1 s). Les dix méthodes
rouges produisent onze échecs de sous-tests et deux erreurs : les huit Q du tableau,
plus intermédiaires/laps et rendez-vous/capture, réservées au 375. Aucune nouvelle
méthode rouge ; **19 des 27 bascules corrigées**, dont les deux parcours d'appel de
`question_absent` et `rendez_vous` confirmés par les voisins. Première passe : deux
assertions de harnais corrigées, puis 30/30 sur ces fichiers et voisins sonores ;
les cinq fichiers déjà verts sont réutilisés. Relais/Aubin puis auberge/Hugues :
admission avant rendu, nom caché absent, même monde et mêmes lignes en bloc/découpé
avec recharges, état complet et scène relus identiques. Bruts `tests-premiere.json`,
`tests-corriges.json`, `tests-voisins.json`. Une tentative sous restriction Windows
a échoué sur les temporaires ; reprise autorisée sans adaptation du moteur.

**Empreintes : identité physique sur 12/12, état complet sur 4/12.** Deux heures
Relais/auberge/mine × graines 1985/7/42/2024, contre `70b2fdfa` : zéro plantage,
mêmes empreintes physiques à 5/60/120 min et à l'issue, chroniques, mesures, récits,
souvenirs PNJ, refus de contact, approches impossibles, avis et constats d'audit.
Les quatre auberges sont entièrement identiques ; Relais et mine divergent dans
le hash de l'état complet. Le code 1 du comparateur signale cette divergence stricte.
Diagnostic borné, graine 1985 : premier pas d'attente de cinq minutes comparé avec
la seule fonction sonore de la base. Au Relais, seuls changent les rendus publics
et le journal (« personne inconnue » → « voix inconnue »), ainsi que l'ordre des
numéros vocaux, désormais celui de la réception ; à la mine, seul le journal change ;
à l'auberge, aucun écart. **Limite : le comparateur n'archive pas les états complets
finaux ; ces préfixes n'attribuent donc pas intégralement les huit hashes de 2 h.**
Aucune garantie d'identité intégrale de ces états n'est revendiquée.

Douze références manquantes jouées une fois et rangées au cache ; branche ensuite,
deux travailleurs réduits au plus, aucune comparaison de coût, aucune nuit de
référence de 2 h relancée. `empreintes.json`, `analyse-cloture.json`, préfixes et
lanceurs archivés ; empreinte du moteur inchangée depuis la vérification.
`fin-verification.json` reste intact (`tests=1`, `empreintes=1`, `erreur=null`) ;
`conclusion.json` consigne la clôture partielle et ses limites. Branche poussée,
fusion et suites de correction au superviseur ; aucun calcul requis en attente.
