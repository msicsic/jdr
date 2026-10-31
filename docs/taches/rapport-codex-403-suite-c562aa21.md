# Lot 403 — Rouges de c562aa21

Branche `codex-suite-c562aa21`, base `integration d23d081d`, laptop.
**Terminé, non fusionné. Code vérifié `e5f5befb` ; branche poussée sur origin.**

**Invariant.** Les 19 méthodes sont encore rouges sur la base actuelle. Bissection
des méthodes historiques sur la première parenté `663d1308..c562aa21`, bornes
vertes et rouges conservées : 14 bascules au 388, quatre au 380, une au 390.
Aucun rouge déjà résolu n'est adapté. Les deux premières passes de harnais
(`avant`, namespace masqué ; `initial`, temporaires interdits) sont exclues.

**Moteur (V).** La réception anticipée d'une voix du 390 laissait son auteur
dans `entendus` après sa mort. `corps.mourir` retire désormais l'interlocuteur
par `ecoute.retirer_interlocuteur` ; `ecoute.retenir` refuse de le réadmettre
quand les sons antérieurs sont relus en fin d'action. Bruits et souvenirs
vocaux restent intacts ; le validateur n'est pas assoupli. Le cas réel de
Brune passe. Brune et Joss couvrent aussi réception hors champ, mort commune,
recharge complète, rendu/fiche/scène, conservation des mots et rejet du rejeu.

**Adaptations documentées.** R : le [388](rapport-codex-388-rembourser-dette.md)
fait du remboursement volontaire un geste choisi. Les épreuves comptables
exécutent son vrai plan local et son vrai geste via `tests/remboursements.py`,
sans sauter de trajet ; elles gardent les assertions de versement unique,
dette restante et recharge. I : isoler la créance de la motivation monétaire
personnelle du scénario, comme le fait le 388. A : ajouter le remboursement
au rang exact de l'oracle A0, avant réclamer/acquérir, sans filtrer ce candidat.
S : un champ sans sens peut être absent d'une forme stricte ; son injection
reste refusée sans mutation avec `attendu`. U : confirmer les remises U-C,
selon le [394](rapport-codex-394-don-consentement.md), en conservant transfert,
homonymie, plans et vues ; seule la bordure blanche des sorties UI est normalisée.
L'oracle exige un plan pour un geste léger, deux plans identiques lorsque le
consentement impose aperçu puis revalidation du choix public à la confirmation.

Les noms de méthodes ci-dessous omettent uniquement le préfixe `test_`.

| Fichier : méthode | Fusion d'origine | Cause / traitement |
|---|---|---|
| accord_date : part_tache_reelles_a_temps_et_retard_remboursement_unique | 388 `224d972d` | R |
| agendas_socle : achat_apres_abandon_conserve_la_piece_due_puis_la_solde | 388 `224d972d` | R |
| agendas_socle : tache_payee_acceptee_puis_abandonnee | 388 `224d972d` | R, aucun versement pendant l'attente imposée |
| contenus_parole : schema_et_validateur_partagent_tous_les_champs_sans_sens | 388 `224d972d` | S, forme dédiée de rembourser |
| echelle_choix : ecarts_egalites_et_routines_issues_des_besoins_pressants | 388 `224d972d` | A |
| echelle_choix : memes_actions_monde_et_textes_apres_rechargement | 388 `224d972d` | A |
| echelle_choix : scenes_tous_les_paliers_et_rechargement | 388 `224d972d` | A |
| inventaire_terminal / Console : chaque_geste_parite_plan_texte_monde_fiche_scene_carte_recharges | 380 `20989ed9` | U |
| inventaire_terminal / TUI : chaque_geste_parite_plan_texte_monde_fiche_scene_carte_recharges | 380 `20989ed9` | U |
| nom_non_relie : nom_relie_le_geste_part_au_mj_et_la_fiche_persiste | 380 `20989ed9` | U |
| parole_corrections : meme_nature_au_contact_et_par_la_parole | 380 `20989ed9` | U, aperçu sans don aussi contrôlé |
| petits_correctifs : le_joueur_est_rembourse_et_le_lit | 388 `224d972d` | R |
| realisation_datee : compte_reel_cache_a_distance_puis_remboursement_visible | 388 `224d972d` | R |
| realisation_datee : huile_remise_aux_trois_bornes_et_jamais_rechargee_par_la_livraison | 388 `224d972d` | R |
| realisation_datee : tache_ponctuelle_aux_trois_bornes_remboursement_unique | 388 `224d972d` | R |
| reclamations_repetees : bourse_privee_et_dates_ne_levent_pas_la_reponse | 388 `224d972d` | R |
| reclamations_repetees : contact_et_reglement_laps_entier_ou_decoupe | 388 `224d972d` | I ; parité du monde et des lignes inchangée |
| reclamations_repetees : echeance_inconnue_ni_plan_ni_ancien_plan_puis_reponse_et_paiement_uniques | 388 `224d972d` | R |
| tuer : joueur_ligote_cri_temoin_nouvelle | 390 `4e14dc02` | V, interlocuteur devenu défunt |

**Mesures et limites. 19/19 méthodes initialement rouges sont vertes.**
Bilan consolidé des 15 fichiers : **151 réussites, un saut sur 152 méthodes,
zéro échec ni erreur**. Le saut est le contrôle facultatif `jsonschema`, absent
de l'environnement. La passe de fichiers (1 837,059 s) avait deux méthodes
d'inventaire rouges au dernier oracle de comptage des préparations ; elles
passent entièrement après adaptation, console en 471,0 s et TUI en 586,0 s.
Les autres résultats, dont l'autonomie du 388, sont conservés : aucun autre
fichier de test ni code moteur n'a changé depuis cette passe. Transferts,
homonymie, plans, monde, textes et vues rechargées passent sur les deux UI.
Le meurtre réel et la nouvelle méthode de parole/décès sont verts aussi.
**Empreintes 2 h Relais/auberge × quatre graines : 8/8 identiques** à
`d23d081d`, chronique, mesures et état final complet ; aucun plantage.
Huit références manquantes calculées une fois et rangées au cache, puis huit
nuits de branche ; aucune comparaison de coût entre ces phases successives.
Les empreintes du code vérifié correspondent aux sources livrées ; la dernière
reprise vérifie aussi les empreintes de tous les fichiers de test concernés.
Deux travailleurs réduits au plus, phases séquentielles. Aucun Luna ni suite complète.
Pas de registre ajouté. Production limitée à `ecoute.py` et `corps.py` ; aucun
fichier de production annoncé par 381/399 touché, aucun accès matériel S1g modifié.
Pas de rouge restant ni de calcul actif ; fusion et suite d'intégration laissées au superviseur.

Bruts : `C:/Users/msics/donjon/artifacts/suite-c562aa21-403/` ; attribution
`bissection/attribution.json`, `fichiers-final.json`, `empreintes-final.json`.
Les deux anciens témoins rouges restent intacts. **`fin-inventaire.json` :
`ok=true`, `sources_identiques=true`** ; il consolide les reprises complètes
`inventaire-final/fin.json` et les sources de `sources-inventaire.json`.
