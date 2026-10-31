# Lot 440 — attribution des rouges connus

31 octobre 2026, laptop ; `codex-rouges-connus`, base `integration 94fcffb9`.
Bruts : `C:/Users/msics/donjon/artifacts/rouges-connus-440/`.
**Code livré ; empreintes encore en calcul, validation finale non acquise.**

**Invariant.** Chaque méthode rouge garde une borne verte et sa fusion rouge.
Archives historiques indépendantes, bissection sur les fusions de première parenté,
puis contrôle du premier parent immédiat. Les trois attributions du 414 sont
réutilisées avec leurs témoins bruts, sans relancer leur bissection.

**Raccord moteur.** A5 doit conserver l'identité d'une référence, pas son orthographe.
`comprehension.verifier_reprise` compare les références décodables vers la même entité,
y compris les listes ordonnées ; les deux voies du MJ lui passent le monde.
Les paramètres sans référence restent identiques. Aucun identifiant inconnu ne devient
équivalent à un autre ; les gardes de référence fournie et de perception restent actives.
L'oracle historique des noms est intact. La console vérifie aussi un élément associé
à un personnage et un autre personnage à l'auberge, avec état et vues rechargés.

Les méthodes ci-dessous omettent seulement `test_` ; les commits sont des fusions.

| Fichier : méthode | Introduction | Classe, preuve et traitement |
|---|---|---|
| gardien_detresse : demander_un_moyen_pour_un_autre_besoin | `6e719746` | Voulu, [417](rapport-codex-417-obstacle-temoin-expire.md) / [419](rapport-codex-419-verification-contact.md) : suffixe descriptif `manger`, demande seule exécutable ; contenu exact adapté, consommation et recharge conservées. |
| paroles : luna_recoit_la_bande_et_les_croyances_pas_la_verite | `bcbfe112` | Voulu, [416](rapport-codex-416-a6-raccord-libre.md) : esprit privé réservé à la mise en voix ; croyance, traits et absence de tiers toujours contrôlés, absence des savoirs privés exigée à la compilation. |
| paroles : les_blocs_nommes_par_les_regles_sont_des_faits_citables | `bcbfe112` | Même contrat A6 ; citabilité selon la phase, revue d'action simulée explicitement. |
| connaissances : boucle_sauve_avant_affichage_et_reutilise_apres_redemarrage | `bcbfe112` | Même contrat A6 ; savoir sauvegardé retrouvé dans la mise en voix, absent du compilateur et du catalogue d'invention ; monde inchangé. |
| noms : frontiere_mj_refuse_l_id_devine_puis_accepte_la_reference_publique | `b1d74a71` | Défaut A5 : identité identique rejetée ; raccord ci-dessus, oracle intact. |
| refus_moteur : forme_persistante_ne_dit_pas_impossible | `42073c26` (410) | Voulu, [410](rapport-codex-410-a3-liaison-transport.md) : grammaire avant préparation, une correction puis repli ; deux appels, même précision publique et absence de mutation. |
| refus_moteur : deux_refus_distincts_dans_l_ordre | `b1d74a71` | Voulu, [415](rapport-codex-415-a5-reprise-fidele.md) : substitution `lire` → `allumer` rejetée avant préparation ; troisième réponse fidèle, seul refus du monde réellement établi affiché et sauvegardé. |
| refus_moteur : correction_en_prose_ou_avis_ne_remplace_pas_le_refus | `b1d74a71` | Même contrat A5 : un avis typé qui substitue l'action exige une reprise supplémentaire ; la prose ne remplace toujours pas le refus. |
| refus_moteur : refus_de_portee_en_correction_garde_le_premier_refus | `b1d74a71` | Défaut restant : la cible inexistante reste figée comme une cible valide absente ; oracle intact, lot R ci-dessous. |
| narration : messages_moteur_apres_deux_refus_sans_action_fictive | `b1d74a71` | Voulu A5 : même substitution ; seul le premier refus est établi, aucune explication libre ni action fictive. |
| empathie_peur : proximite_ne_sauvegarde_pas_un_suffixe_encore_suppose | `6e719746` | Voulu 417 : suffixe descriptif `rester` conservé ; liste exécutable réduite au préfixe, sans marqueurs supposés ; deux scènes et recharge inchangées. |
| empathie_peur : lecture_retenue_revisee_par_un_dementi_percu_et_non_par_le_regard | `c3f0c2d5` (374) | Voulu, [374](rapport-codex-374-position-hypothese-datee.md) : position entendue à 167 expirée à 203, regard sans cible, zéro jet. Exige absence de démenti, puis localisation fraîche entendue et vraie relecture ; assertions initiales conservées. |
| dynamique_besoins : lucien_rapporte_la_lanterne_de_l_etable_au_grenier_au_lieu_d_aller_et_venir | `c3f0c2d5` (374) | Défaut restant : neuf passages supplémentaires ; aucun réancrage de trajectoire, lot L. |
| dynamique_besoins : lucien_attend_une_information_apres_la_reprise_du_ballot | `c3f0c2d5` (374) | Défaut restant : recherche d'Anselme absente ; le 419 ne rétablit pas cet oracle. Lot L. |
| reprise_fidele : plusieurs_pieces_gardent_les_quantites_de_chaque_etape | `88f21002` (426) | Défaut voisin, reproduit sur la base ; premier parent `ce64ba7e` vert : catalogue de parts, `KeyError: nom_piece`. Oracle intact, lot F. |
| reprise_fidele : quantite_contestee_libere_operation_seule_et_preleve_une_piece | `88f21002` (426) | Même défaut K0, sous-cas fagots ; même paire verte/rouge vérifiée, oracle intact. |

**Lots séparés proposés.** R : une référence invalide libère seulement son champ
contesté, sans libérer l'opération ni les autres paramètres (`refus.inaccessible`,
producteurs de `champs_corrigeables`, reprises A5). Le raccord d'identité ne prétend
pas corriger une cible inexistante. L : attribuer chaque nouveau départ de Lucien à
sa preuve disponible, puis conserver la consommation des pistes jusqu'à une preuve
neuve (`planification.preparer_contact`, `_chercher`, `_entrees`, `pnj._agir`,
reprise de l'intention dans `deliberation`). Le ballot ne doit pas exiger une fouille
de toutes les salles si cette fouille contredit le contrat du 374 ; établir d'abord
le parcours légitime et vérifier renoncement, vol, monde et rendu après recharge.
F : le catalogue public doit parcourir tout monde valide sans prélever une pièce
dont le contrat physique n'est pas établi (`accords_publics`, candidats de
`dialogues`, `echanges.detacher_part`, `matiere.prelever_piece`). Distinguer la part
consommable de la pièce comptée, sans inventer un `nom_piece` pour masquer le manque.

**Validation.** Quatorze rouges demandés attribués, **onze résolus, trois différés**.
Treize fichiers : **167 méthodes, 162 vertes, un échec et quatre erreurs sur cinq
méthodes** (les trois différées et les deux voisines de K0), zéro ignoré.
Les fichiers noms, paroles, connaissances, narration, empathie, gardien, raccord A6,
projection A1, non-perception et reprise des références sont verts.
`bilan-tests.json` consolide les dernières passes ; bornes dans `fin-attribution.json`,
`preuves-414/` et `fin-catalogue.json`. Le premier lancement bloqué par les droits
temporaires et les fixtures intermédiaires rouges sont exclus du bilan.
Deux travailleurs réduits au plus, aucune suite complète ni Luna.

**Calcul restant.** Empreintes 2 h, Relais/auberge × 1985/7/42/2024, référence
`94fcffb9` puis branche, un travailleur ; référence cachée par commit, sans rejeu de
`main`. Le témoin attendu est `C:/Users/msics/donjon/artifacts/rouges-connus-440/fin-empreintes.json`,
publié après tous les bruts. Ne pas déclarer l'identité acquise avant lecture de
`empreintes.json` ; aucun coût comparé à un cache. La comparaison de références
couvre le registre, pas l'équivalence de paraphrases libres ; les cinq méthodes
différés gardent leurs assertions. Les déplacements de Lucien restent à attribuer
à leurs preuves avant de les reclasser comme voulus.
