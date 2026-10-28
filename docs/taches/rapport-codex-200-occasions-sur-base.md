# Lot 200 — Occasions asymétriques sur la base actuelle

Branche `codex-occasions-sur-base`, **non fusionnée**, base `23aba63`.
Données des sept scénarios reprises de `18c52aa` sans galettes : bois propre
cessible, affection en triangle et observations inégales. Aucun moteur modifié,
aucun Luna. Deux travailleurs en priorité réduite au plus ; bruts exclusivement
`C:/Users/msics/donjon/artifacts/occasions-200/`.

**Contrat des scènes.** Les nouvelles occasions restent actives dans le jeu et
le banc. Les anciennes scènes de mécanisme déclarent leurs ressources et
positions antérieures via `tests/scenarios_contractuels.py`. Cette fabrique
n'inverse que les 54 différences de données du lot 186 : les projets 184/192
restent actifs. Un contrôle des sept empreintes structurelles compare ses
données à la base actuelle, indépendamment de la construction du monde.
Les assertions historiques ne sont pas relâchées.

**Mesure à base identique.** Quatre scénarios × 1985/7/42/2024, 4 h, départ tiré,
comparateur officiel instrumenté seulement pour sauver/recharger. La référence
`23aba63`, absente du cache, a été calculée une fois et rangée dans le cache
commun ; aucune référence existante rejouée, aucun temps comparé. S/F/D : fonction
`cats` exacte du lot 183, signatures famille/auteur/texte, PNJ inactifs inclus.

| Scénario | S base → lot | F base → lot | D base → lot |
|---|---:|---:|---:|
| Relais | 6,75 → 7,75 | 4,25 → 4 | 1,188 → 1,188 |
| Mine | 13,25 → 15 | 4,75 → 5,25 | 1,214 → 1,321 |
| Auberge | 6,5 → 6,5 | 2,75 → 2,75 | 0,625 → 0,625 |
| Crue | 17,25 → 16,75 | 6,25 → 5 | 1,938 → 1,563 |

Sommes des 16 nuits, base → lot : propositions/acceptées **58/15 → 71/18** ;
ventes proposées/acceptées **25/8 → 50/13** (demande de pièces contre bien/part,
souvenirs typés) ; commissions sollicitées/acceptées/abouties **0/0/0 → 4/0/0** ;
avis/adoptions **0/0 → 4/1** ; services crédités **3 → 3** ; travaux
proposés/acceptés/faits **7/0/5 → 2/0/4**. Projets de dette nés **12 → 12**,
récupérations **0 → 1**. Brune vend son bois dès la minute 0 dans les quatre
Relais ; Odon vend une part à Josse à 184 min (mine 42). Crue 7 : Brune prend
les bûches du guet à 151 min ; projet de Gorm né à 152, restitution demandée et
obtenue à 228, projet atteint. Ces états finaux et leurs rendus sont rechargés.

**Audit et recharge.** Zéro plantage/usurpation. `fige_presse` **4 → 3**,
`repetition` **2 → 0**, `voir_alterne` **3 → 0**, `appels_nombreux` **1 → 0**,
`noir_long` **1 → 1**. Bascules **3 → 1**, pire passage **46 → 50/h**.
Le lot 199 n'est pas fusionné sur cette base : pas de compteur d'audit des
changements d'avis à prétendre. **24/24 états complets et rendus identiques**
sur la branche : 16 fins à 4 h et huit étapes à 120 min (Relais/mine), avec
description, fiche/besace et sons. Les 16 fins de référence sont aussi vérifiées.

**Tri.** Reprise brute : 30 échecs et quatre erreurs, dans 32 méthodes
(auto-accusation : trois sous-cas), tous retrouvés sur la base actuelle.
Classe a : occasions légitimes ; les scènes gardent leurs assertions exactes.
Aucune régression moteur établie dans ces cas après restitution des données
d'auteur. Les traces distinguent les reprises initiales, les corrections de
préparation et la suite finale. **Livraison partielle : suite complète unique
en cours**, `tools/tests.py --processus 2`, 274 fichiers ; lire `suite.json` et
`suite.log` dans les bruts avant intégration. Ne pas assimiler son lancement
à un bilan vert. Reprises ciblées : aucune assertion en défaut sur 242 tests,
sept erreurs de préparation (suppressions de bois devenues redondantes et deux
imports locaux mal indentés), corrigées puis **87 tests verts**. Les nouveaux
contrôles de données et les fichiers non repris séparément passent encore par
la suite finale. Aucune seconde suite complète à lancer ; reprendre seulement
les fichiers qu'elle signalerait.

| Test (préfixe `test_` omis) | Cause → décision (classe a) |
|---|---|
| `agendas_garder.deux_gardes_interposition_monde_et_rendu_recharges` | Échanges changent les relations avant le passage ; scène de garde antérieure. |
| `constater_rumeurs.ilse_dit_a_gorm_ou_brune_a_pose_ses_vivres` | Vente/commission déplace Gorm et accélère la reprise ; rencontres antérieures. |
| `crochetage_surenchere.maladroite_elle_attend` | Vente remplace le crochetage en attente ; stock historique. |
| `deliberation_evenements.une_reserve_ouverte_sous_ses_yeux_la_fait_choisir_aussitot` | Vente pour la dette concurrence la faim ; stock historique. |
| `dynamique_besoins.bram_va_prendre_la_lampe_du_filon_et_revient_garder_la_paie_eclaire` | Marché supplémentaire change les recours au bureau ; stock historique. |
| `echanges_suite.brune_refuse_et_la_dette_demeure` | Brune part vendre avant la réclamation ; bois antérieur. |
| `ecoute.colle_a_la_porte_on_entend_des_voix_derriere` | Nouvelle conversation audible ; interlocuteurs antérieurs. |
| `ecoute.loin_de_la_porte_ou_sans_ecouter_rien_ne_passe` | Nouvelle conversation audible ; interlocuteurs antérieurs. |
| `esprits.la_poutre_cache_le_joueur` | Vente déplace Gorm avant le constat ; scène visuelle antérieure. |
| `impressions_observer.observations_successives_rendent_les_impressions_sans_relancer` | Vente modifie les signes entre observations ; scène initiale sans nouveau bois. |
| `interposition.deux_gardiens_poste_parole_persistance_et_rendu_recharges` | Même scène de garde appelée directement ; données antérieures. |
| `marche.un_obstacle_sur_le_seuil_barre_le_passage` | Vente de bois choisie après le réflexe manqué ; ressources antérieures. |
| `mine.le_noir_gagne_le_camp_et_les_protecteurs_accourent` | Nouveau combustible prolonge la lumière ; stock historique explicite. |
| `ouie.demander_a_qui_n_est_pas_la_corrige_la_croyance` | Gorm bouge avant la réponse ; liens/ressources antérieurs. |
| `ouie_temoins.qui_veut_agir_sans_temoin_compte_ceux_qu_il_croit_a_portee_d_oreille` | Vente choisie plutôt que crochetage attendu ; stock historique. |
| `paroles.mensonge_dementi_par_ce_qu_il_voit` | Autres rencontres/paroles changent la confiance ; scène perceptive antérieure. |
| `perception_geste.ecouter_et_chercher_passent_la_revue_du_premier_coup_et_sont_sauves` | Paroles supplémentaires entendues ; interlocuteurs antérieurs. |
| `perception_geste.une_perception_corrigee_ne_devient_pas_un_geste_vide` | Paroles supplémentaires entendues ; interlocuteurs antérieurs. |
| `petits_correctifs.la_promesse_expiree_la_dette_est_reclamee` | Nouveau recours déplace le débiteur ; scène sociale antérieure. |
| `petits_correctifs.les_vivres_epuises_gorm_rend_les_pieces` | Achat de bois supplémentaire débite une pièce ; stock historique. |
| `petits_correctifs.moins_douce_elle_force_la_reserve_de_gorm` | Vente détourne Brune du bris ; stock historique. |
| `protection.gorm_voit_brune_prendre_les_planches_d_aubin_et_le_lui_dit` | Bois propre évite le vol ; stock historique. |
| `relations_socle.gorm_voit_ses_vivres_aux_mains_de_brune` | Gorm quitte la portée du joueur ; liens antérieurs. |
| `ressources.on_monte_se_chauffer_au_poele_du_guet_et_le_bois_reste_compte` | Brune peut alimenter le poêle ; stock/positions historiques explicites. |
| `securite.la_mefiance_inquiete` | Échanges déplacent les présences comparées ; scène sociale antérieure. |
| `securite.le_noir_inquiete_la_lumiere_et_la_compagnie_rassurent` | Échanges déplacent la compagnie ; scène sociale antérieure. |
| `social.la_rumeur_passe_de_main_en_main_puis_s_eteint` | Gorm quitte la rencontre pour un nouveau recours ; liens antérieurs. |
| `social.un_jet_rate_laisse_gorm_sceptique` | Nouvelle parole suit la rumeur dans la mémoire ; liens antérieurs. |
| `soi_meme.ancienne_rumeur_contre_soi_ne_se_retransmet_pas` | Nouveaux échanges rendent le marteau à Gorm ; scène sociale antérieure (trois sous-cas). |
| `tenir.joueur_tenu_ne_peut_pas_marcher_et_se_degage` | Une offre supplémentaire consomme le jet réservé au dégagement ; scène de coups antérieure. |
| `tensions.gorm_va_chercher_son_bois_et_recharge_le_feu_qui_baisse` | Bois de Brune disponible avant celui des vannes ; stock historique. |
| `tensions.un_feu_eteint_ne_rechauffe_pas_et_corrige_ce_qu_il_croyait` | Bois supplémentaire permet le rallumage ; stock épuisé historique. |

**Limites.** Ce lot de données ne garantit ni l'absence générale de boucles ni
un gain uniforme de richesse. Les défauts éventuels du moteur restent hors
périmètre et doivent être livrés comme tels avec leurs captures.
