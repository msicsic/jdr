# Lot 284 — Vérification d’intégration

29 octobre 2026, branche `codex-verif-integ-4`, commit `27ff8c4`, témoin `0bad227`.
**49/49 archives terminées** (`FIN.json`, `ok=true`) : audit 12 h 32, rixe 4,
rixe douce 4, `VERIFIER`/spatial 5 et hameau 12 h 4. Références 241/274 copiées
du PC fixe et relues, jamais rejouées. `donjon/` et `tools/` identiques au départ ;
aucune suite complète ni Luna (passe séparée par l’orchestrateur). Bruts :
`C:/Users/msics/donjon/artifacts/verif-integ-27ff8c4/`.

## Contrôles et alerte d’intégration

Zéro plantage, usurpation, mort, coup porté ou reçu ; les 22 pertes de service
du 227 sont toutes non fautives (19 cessations physiques, deux départs du
prestataire ou bénéficiaire, un service clos avant perte). Aucun écart `VERIFIER`
ni assertion spatiale dans les cinq nuits de contrôle. `VERIFIER` atteint 202
recherches bornées à l’auberge/42 (88 au 274) ; les 202 coûts contrôlés égalent
l’optimum enregistré. Les 15 frappes et six coups du témoin (crue/2024) ne
réapparaissent pas. La captivité n’est pas certifiable : l’audit ne conserve
pas l’état des captifs.

La sonde 219, avec `renouvellement_perceptif` (zéro occurrence), relève **112
suspects et 440 entrées à expliquer**, contre 7 et 170 au 274, qui ne comptait
pas cette classe. Le cas dominant est nouveau : hameau/1985, Aubin reprend 109
fois sans nouvelle entrée le but `rejoindre Sève au beffroi` entre 540 et 649 min.
Il reste relevé dans la crypte tandis que Sève est au beffroi ; sa chronique
compte **120 passages en une heure** autour des salles des vannes. Le même soir
de `0bad227` ne présente ni ces reprises ni une rafale de 64 passages/heure.

Second cas de même nature : crue/3, Gorm effectue **299 passages en une heure**
dans un circuit de cinq salles alors que son but relevé reste « informer Ilse » ;
le témoin de cette même graine ne dépasse pas le seuil de rafale. Six nuits
courantes dépassent 64 passages/heure (contre aucune nuit témoin). Le contrat
commun à instruire est la progression d’un plan de déplacement/reprise : un but
qui ne rapproche pas de sa cible ne doit pas reconduire un trajet cyclique sans
progrès. La cause précise n’est pas isolée à un lot ; ces deux cas réels justifient
un lot de diagnostic/correction général avant l’avancement de `main`.

## Mesures moyennes par nuit — `0bad227` → `27ff8c4`

Attente, noir et eau en PNJ·min ; bascules en moyenne, passages = maximum
PNJ/heure ; S/F/D selon le lot 183 ; mesures principales sur 12 h.

| Mesure | Relais | Mine | Auberge | Crue | Hameau |
|---|---:|---:|---:|---:|---:|
| Sans recours / attente | 0/548 → 0/407 | 0/1 208 → 0/497 | 0/339 → 0/65 | 0,6/1 138 → 0/409 | 0/1 062 → 0/353 |
| Noir / eau | 324/— → 339/— | 1 043/— → 393/— | 702/— → 756/— | 24/94 → 94/36 | 133/14 → 621,3/3 |
| Appels / aide | 1,9/0,3 → 2,5/0,4 | 16,4/3 → 12,6/1,9 | 17,5/2,3 → 66,8/2,4 | 3,8/1,4 → 17,4/1,1 | 2,3/1,5 → 45,8/1 |
| Bascules / passages max | 0,1/8 → 0,1/9 | 0/20 → 0,5/24 | 1/29 → 0,8/84 | 0,8/20 → 0,9/60 | 0,3/16 → 0,3/83 |
| Échanges | 54,6 → 57,5 | 159,1 → 166,3 | 197,9 → 230,3 | 59,6 → 63,2 | 109,5 → 127,8 |
| Propositions / acceptées | 7,8/3 → 9/3,4 | 10,4/0 → 7,6/0,3 | 8,5/0,4 → 5,6/0,3 | 7,5/1,1 → 7,1/1,1 | 11,3/2,3 → 10,8/3 |
| Avis / changements d’avis | 0/0 → 0/0 | 0/0 → 0/0 | 0/0 → 0/0 | 0,8/0,1 → 0,8/0 | 2,3/0 → 1,5/0,3 |
| Disputes / pertes de service | 0/1 → 0/1 | 0/0 → 0/0 | 0/0,1 → 0/0,3 | 0/0 → 0/0 | 0,5/0 → 0/0,5 |
| Constats / avertissements redits | 11,5/1,3 → 11,9/0,5 | 35,6/1,1 → 32,1/0,8 | 51,3/2,5 → 22,3/1,9 | 17,5/0,8 → 9,5/1 | 22,3/1,3 → 7,3/1,3 |
| S/F/D | 31,6/5,8/3,06 → 32/6/2,91 | 101,6/7,1/3,50 → 111,6/7,6/3,43 | 107/6,1/3,09 → 152,5/6,5/3,23 | 31,9/7,5/3,69 → 38,6/7,1/3,78 | 56,3/8,5/3,42 → 80,5/7,5/3,38 |

## Suivis

- **266/282 — hameau :** attente moyenne 1 062,5 → 352,5 et S 56,25 → 80,5 ; le noir monte de 132,5 à 621,3. L’attente varie fortement : graine 42, 485 → 750 ; les trois autres baissent. Les appels `appel_sans_reponse` mémorisés passent de 171 à 532 sur les 49 nuits (dont 376 en auberge) ; ce registre compte des observations par salle, pas des appels uniques.
- **277 — allumage :** cas naturel confirmé en crue/7 à 218 min : Ilse demande à Aubin d’allumer le poêle du guet, il accepte, allume le poêle et s’y chauffe dans la même minute. Aucun événement correspondant à cet instant dans le témoin.
- **273 — Aubin Relais/2024 :** le suspect du témoin à 195 min (`servir vivres à Ilse`) ne réapparaît pas.
- **Mandats :** aucun mandat oral naturel ; six activations naturelles d’`evacuer_crue` portent « mandataire estimé », plus une occurrence dans le rejeu `VERIFIER`.

**Verdict : intégration non propre pour avancer `main`**, tant que la boucle de
progression n’est pas instruite sur le cas du hameau et un second trajet de même
nature. Les compteurs S/F/D mesurent des signatures, pas une causalité ; les
rafales signalent un problème de comportement sans attribuer seules le lot fautif.
