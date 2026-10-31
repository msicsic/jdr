# Tâche Codex 440 : attribuer et résoudre les rouges connus de l'intégration

Plusieurs lots fusionnés ces dernières heures ont signalé des tests rouges **reproduits sur leur base**, donc présents sur
l'intégration et non causés par eux. Liste connue (rapports 419, 427, 428, 429, 432, 433) :

- `test_gardien_detresse.GardienDetresseTests.test_demander_un_moyen_pour_un_autre_besoin` : le contenu du plan porte
  `suite_conditionnelle`, l'oracle ne l'attend pas ;
- `test_paroles.ExpressionTests.test_luna_recoit_la_bande_et_les_croyances_pas_la_verite` (KeyError
  `esprits_interlocuteurs`) et `test_paroles.CitationTests.test_les_blocs_nommes_par_les_regles_sont_des_faits_citables` ;
- `test_connaissances` : une erreur liée à `connaissances_pnj` dans le contexte public (rapport 428) ;
- `test_noms` : `test_frontiere_mj_refuse_l_id_devine_puis_accepte_la_reference_publique` (sous-cas Aubin/Gorm,
  `RefusDeForme` puis `StopIteration` du fournisseur simulé) ;
- `test_refus_moteur` : quatre méthodes (rapport 432) ;
- `test_narration.test_messages_moteur_apres_deux_refus_sans_action_fictive` (rapport 427) ;
- `test_empathie_peur.CompagnieTests` : `test_lecture_retenue_revisee_par_un_dementi_percu_et_non_par_le_regard`,
  `test_proximite_ne_sauvegarde_pas_un_suffixe_encore_suppose` (relais, mine) (rapport 419 : démenti empathique, deux
  égalités rejetant le suffixe descriptif du 417) ;
- `test_dynamique_besoins` : lanterne et ballot de Lucien (rapport 419).

Lis `AGENTS.md`, `docs/etat-dev.md` (court), les rapports cités, et les rapports 403 et 414 (même exercice sur des suites
antérieures : méthode à reprendre).

## Invariant (un seul)
**Chaque rouge est attribué à son commit d'introduction (bissection bornée sur les fusions) et classé : changement
voulu dont l'oracle est périmé (preuve citée du rapport du lot fautif ; l'assertion est adaptée sans affaiblir ce
qu'elle protège), ou défaut du code (corrigé par le contrat commun, oracle intact).** Aucun test ignoré ni supprimé,
aucune assertion de sécurité affaiblie. Une correction de code qui dépasse un petit raccord devient un lot à part :
dans ce cas, laisse le test rouge et décris le lot (invariant, fonctions).

## Contraintes
**Poste : le laptop.** Lots en cours : 431 (admission préalable, `mj.py`, `portee_narrative.py`), 435 (S1o), 437
(`planification.py`), 438 (`agendas.py`, `deliberation.py`), 439 (diagnostic). Touche leurs fichiers le moins possible.
Deux processus au plus, priorité réduite. Pas de suite complète, ni Luna.

## Vérification
Chaque fichier concerné vert (ou rouge restant justifié, avec le lot proposé) ; voisins verts ; pour une correction de
code, cas réel et autre cas après recharge, et empreintes 2 h, quatre graines, scénarios touchés et Relais.

## Livraison
Branche `codex-rouges-connus`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
l'utilisateur ; poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-440-rouges-connus.md` (tableau :
test, commit d'introduction, voulu ou défaut, preuve, traitement) ; entrée « non fusionnée » de 8 lignes au plus dans
`docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves). Bruts dans
`C:\Users\msics\donjon\artifacts\rouges-connus-440\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou
`QUESTION : …`.
