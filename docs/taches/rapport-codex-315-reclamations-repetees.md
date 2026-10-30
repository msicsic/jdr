# Lot 315 — réclamations et contact du débiteur

**Réaccordance du 2026-10-30.** Fusion Git, sans rebase, de l'essai d'intégration
`8f410f7` dans le 315 `beaecc7`. Les deux intentions de `biens.regler/solder`
sont conservées : rétention durable du refus et ordre des comptes du 315 ;
dette non encore apprise, réalisation datée et remboursement unique d'E2.
Les références E1 et les points de réalisation E2 ne sont pas réécrits.
`dettes(..., connues_de=...)` fournit une lecture commune des seules créances
apprises à `planification.reclamer`, `echanges.executer` et `entrees_creance` :
une dette marquée `a_prevenir` ne prépare aucune demande et ne lève aucun refus.
Les comptes physiques et le remboursement volontaire gardent toutes les dettes.

**Validation de cette fusion.** 29 tests ciblés verts, dont deux régressions
de croisement exercées chacune sur l'huile remise et le verrouillage payé :
échéance dépassée, ancien plan silencieux, refus durable malgré une dette
nouvelle inconnue, réponse locale, remboursement volontaire et archive unique ;
monde, rendu et scène perçue comparés après recharge. Les 37 fichiers ciblés
des rapports 315/348/350 et des modules touchés sont en cours de validation.
Bruts : `C:/Users/msics/donjon/artifacts/reclamations-315/fusion-e1-e2/`.
Le point de reprise reprend l'essai, avec la seule entrée du 315 ajoutée.
Ni suite complète, ni Luna, ni nouvelles empreintes : cette fusion conserve
les contrats validés par les lots, dont les mesures et limites restent ci-dessous.

Branche `codex-reclamations-repetees`, base **c4f6d46**, moteur final
**faa5967**. **Lot terminé ; identité stricte non atteinte.**

**Invariant et cause.** Les sept retours de Sève 2024 du 306 ne suivaient
aucun refus : capture t=22057 rejouée sur la base jusqu’à 82, deux dettes
(Gorm 2 pièces, Brune 1), aucun `dette_niee`/`creance_vaine`. Le plan
`reclamer` s’arrêtait à `aller` ; arrivé dans la salle sans établir la
parole, le créancier repartait vers l’autre dette. La mémoire des réponses
aux dettes était en outre bornée et temporisée.

**Correction.** `planification.reclamer` termine par une demande typée ;
`echanges.executer` utilise la parole commune, passages audibles compris.
`biens.regler/reponse_creance_retenue/entrees_creance` et
`deliberation.retenir_refus/tient/moyens_crus` partagent une réponse durable
entre choix, règlement automatique et ancien plan. Aucun délai : obligation
nouvelle ou fonds appris, jamais position, date, diminution des moyens ou
bourse privée. Règlement spontané conservé. Aucun scénario/MJ modifié.

**Tests et recharge.** **127 tests distincts verts / neuf fichiers** :
85 résultats conservés, **42 verts en reprise** (44,936 s), dont six tests
nouveaux. Les deux régressions initiales sont corrigées sans toucher aux
tests existants : mémoire de décision sans second événement social
(`souvenir=False`), débiteur encore audible jamais déclaré absent pour
le seul changement de salle. Capture réelle avant 83 : deux remboursements
en **83/84**, quatre déplacements en seize minutes ; monde/rendu/scène et
textes identiques après recharge et laps entier/découpé. Refus réels au
Relais et à l’auberge conservés après délai et éviction des souvenirs ;
ancien plan neutralisé, fonds cachés sans effet, moyens nouveaux admis.

**Trois écarts d’empreinte qualifiés : effets voulus du contact accompli.**
Ce sont des **premières demandes remboursées**, pas des relances après
refus ; la rétention selon la cause est éprouvée par les tests précédents.
Les instants sont en dixièmes de seconde depuis le début de la partie.

| Nuit | Premier écart de choix ; premier écart raconté | Effet dans l’état, branche contre référence |
|---|---|---|
| Relais 7 | t=1188, demande ajoutée au trajet ; t=1255 (min 2), Aubin réclame au lieu de rester près d’Ilse | Gorm rend 2 pièces à t=1255 contre 1800 (min 3). Soldes Gorm/Aubin 52/3 → 50/5 ; dette 2 → 0. |
| Auberge 1985 | t=37505 (min 62), Mathurine réclame au lieu de proposer l’achat de soupe épuisée | Mireille rend 1 pièce à t=37505 contre 37800 (min 63). Soldes 7/5 → 6/6 ; dette 1 → 0. |
| Crue 1985 | t=2102, demande ajoutée au trajet ; t=2300 (min 3), Aubin réclame au lieu de négocier des vivres | Gorm rend 2 pièces à t=2300 contre 4800 (min 8). Soldes 52/3 → 50/5 ; dette 2 → 0. |

**Preuve causale :** six courts rejeux, horizons 5/65/10 min. Rétablir
uniquement l’ancien plan (avec son ancien lecteur de refus, inactif ici)
reproduit **exactement les trois préfixes de référence** ; le moteur final
reproduit exactement ceux de la branche. Un seul remboursement par dette,
conservation des pièces, aucune dette résiduelle, six recharges
monde/rendu/scène identiques. Bruts `qualification-preuves.json` et
`preuve-*-monde.json`. Les trois nuits 2 h restent non identiques :
chronique, mesures et état complet changent ; aucune égalité fabriquée.
Les treize paires initialement identiques sont conservées, sans relance.
Zéro plantage/usurpation/suspect dans les trois nuits corrigées.

**Hameau conservé sur b05bb80 :** quatre nuits 4 h, données 306 intactes,
suspects **0/0/0/7 → 0/0/0/0**, à expliquer **7/5/0/10 → 2/5/0/4**,
monde/rendu/scène rechargés identiques. Aucun refus de créance dans ces
nuits ; banc réussi non rejoué. Worktree temporaire retiré. Deux travailleurs
réduits au plus, références réutilisées, ni Luna ni suite complète.

**Limites.** Les conséquences ultérieures des trois nouvelles chronologies
ne sont pas certifiées bénignes une à une (dont dérives et tentatives de
prise) ; aucune absence universelle de boucle ni gain de coût revendiqué.
Anciennes sauvegardes sans refus durable : une demande peut précéder sa
rétention ; pas de migration inventant les moyens jadis connus. Prêts et
autres demandes inchangés. Recouvrement 314 : `echanges.py`, fonctions
distinctes (`executer` ici, `_remettre_part` pour 314 au relevé initial).
Bruts : `C:/Users/msics/donjon/artifacts/reclamations-315/` ; `fin.json`
et `fin-reprise.json`, **ok=false**, conservés ; qualification finale dans
`fin-cloture.json`, **identite_stricte=false**. Aucun calcul actif.
