# Lot 183 — Mécanismes sociaux dormants

`codex-mecanismes-dormants`, base `integration 1b0a778`, 2026-10-27.
Diagnostic seul, sans code/scénario modifié ni Luna. **49 archives relues**,
SHA-256 identiques au manifeste 174. Bruts, scripts, détails et captures :
`C:/Users/msics/donjon/artifacts/dormants-183/`.

**Déclenchement ne signifie pas réussite.** Sur les 49 nuits : **174 propositions,
14 acceptées** ; échecs : 83 `garde`, 44 `mefiance`, 15 `necessaire`, dix
`epuise`, quatre `persuasion`, trois `marche`, un `portee`. **18 promesses en
contrepartie : 17 `garde`, un `epuise`, aucune acceptée.** Une commission
sollicitée, refusée ; aucune dispute. Les travaux payés (`taches_proposees`)
ne mesurent pas les promesses. Sept crédits de service dans les huit mines
ne prouvent pas une intention de réparer la confiance.

| Mécanisme → contrat commun | Condition manquante, moment réel → donnée ou lot proposé |
|---|---|
| **Offre**, `pnj_propositions.recours` : refus/faute `sans_temoin`, après moyens ordinaires et demandes du préfixe ; interlocuteur cru dans la salle, contrepartie portée/pièces, chance améliorée, essai mémorisé. | Odon → Lucien, mine 1985 **0 min + 10,6 s** : outils contre pain, `mefiance` ; Gaspard → Lucien **118**, `epuise`. Captures `offre-1/2`. **Donnée** : bien cessible et contrepartie utile ; épreuve de marché, sans affaiblir les gardes. |
| **Promesse**, `propositions.taches_crues`, `recours`, `echanges.offre_sensee` : premier manque connu (feu, serrure, condition entendue), un devis autonome sans demande/délégation future, classement coût/chance. | Josse → Mathe, mine 1985 **205**, verrouiller `porte_reserve` contre `vivres` : `garde`, capture `promesse-1`. **Donnée** : réserve négociable et travail utile. Un seul candidat peut en masquer un autre ; aucune preuve ici que cela empêche un accord. |
| **Commission**, `devis_intermediaire/plan_recours` : refus retenu `mefiance/rancune`, dernier recours, attachement cible→porteur **cru**, porteur connu/joignable sans défiance connue ; un essai, coût comparé au service. | Mine 1985 **0**, Odon : aucun attachement cru (capture `refus_social-1`). Hameau 1985 **659**, Brune → Maël : `mefiance`. **Donnée** : triangle de liens perceptibles et porteur disposé. **A5**, distinct de cette commission : mandat de sous-but, autorité, compte rendu, réaffectation. |
| **Service**, `rendre_service`, `services.preparer/constater/don_utile` : après refus social et impasse/faute ; premier travail autonome ou don utile porté ; effet utile réellement perçu, auteur identifié, hors prestation convenue. | Odon/Lucien, mine 1985 **0** : aucune tâche connue, faim/chaleur non pressantes ; Odon/Gaspard **469** : lampe éteinte connue, devis autonome impossible (`promesse_autonome=False`, `services-candidats.json`). **Donnée** : moyens et droits réalisables. Captures `refus_social-1/2`. **3d manque** : but d'empathie général, empathie × (affection + 20)/100, après besoins pressants et avant routine ; le crédit du lot 120 ne crée pas ce choix. |
| **Avis/dispute**, `social._avis/_concerne/_auditeur/_contradiction`, `esprits.recevoir_prevision` : souci ≥ **100** (altruisme + empathie + affection), auditeur cru concerné, audition/créneau/registre ; adoption par poids, constat propre récent prioritaire. Dispute : avis contraire plus fort ; éclat si fierté > **60** ou colère ≥ **20**. | Crue 7 **84 min + 35,3 s**, Aubin → Gorm/Ilse : même prévision propre `vu`, conviction 1, `doute` ; captures `avis-1/2`, `dispute-1`. Nuit : **17 réceptions, 16 doutes, une adoption** ; 18 contrôles de contradiction, aucun auditeur contraire. **Donnée** : observations asymétriques, rencontre précoce ; dispute : estimations contraires étayées. |
| **Projets nouveaux**, `agendas`, table des cas | **A6 manque** : naissances par dette, occasion, vengeance/ralliement. A7 (réputation/punition), A8 (dissimuler/assassin) en dépendent ; aucun scénario ajouté pour simuler ces pièces. |

**Richesse observable S/F/D**, calculée sur les 49 nuits : signatures distinctes
`(famille, auteur, texte exact)` ; familles présentes ; moyenne des familles par
PNJ, inactifs compris. Dix familles : demande, offre matérielle, promesse,
travail payé, délégation, avis, dispute, service crédité, interposition, appel.
Promesse et offre matérielle exclusives ; service attribué à son auteur.

| Groupe (durée ; nuits) | S | F | D |
|---|---:|---:|---:|
| Relais (12 h ; 8) | 16,75 | 4,25 | 2,00 |
| Mine (12 h ; 8) | 61,25 | 6,88 | 2,89 |
| Auberge (12 h ; 8) | 70,75 | 4,63 | 2,39 |
| Crue (12 h ; 8) | 23,50 | 5,75 | 2,78 |
| Hameau (12 h ; 4) | 36,50 | 5,25 | 2,54 |
| Rixe / douce (8 h ; 4 chacune) | 14,25 / 15,25 | 3,75 / 4,00 | 1,81 / 1,81 |
| Renforcées auberge/crue/mine/Relais/rixe (8 h ; 1 chacune) | 23/12/31/12/12 | 3/6/5/3/3 | 1,25/2,50/1,86/1,50/1,50 |

Ajout proposé, non implémenté : agrégation pure dans `audit_nuits.analyser_nuit`,
avec détail par PNJ/issue. **Limites** : signatures, pas épisodes causaux ; même
texte fusionné, services sans transition de bande sous-comptés ; délégation ≠
commission. Changements de but causés et projets nés non mesurables avec ces
archives seules. Durées différentes séparées ; détails dans `richesse.json`
et `observations-typees.json`.

**Validation.** Trois reconstitutions ciblées de 12 h sur copie de `ee835d2`,
un seul processus de nuits à priorité réduite. Concordance à l'archive pour
chronique, mesures, empreintes, récit et souvenirs ; 18 captures sauvées/rechargées
deux fois, état et rendu stables (`diagnostic-*.json`). Dix suites de décisions
reproduites deux fois après recharge (`verification-captures.json`). Pas de suite complète
pour ce lot documentaire. Filtres non extrapolés aux 49 nuits ; aucune correction
ou garantie nouvelle du jeu revendiquée. Aucune clé de signature Git configurée.
