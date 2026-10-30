# Lot 306 — agenda d'évacuation du hameau

Branche **`codex-a5-agenda-hameau`**, non fusionnée, base initiale `7ec839e`.
Reprise laptop du 30 octobre 2026 : fusion sans rebase de l'intégration
**`19c9b6da`** (358 et 335), commit mesuré **`0c4663a2`**.
**Lot terminé, blocage levé ; intégration recommandée avec les limites ci-dessous.**

**Invariant.** Gorm reçoit `evacuer_crue`, `amener` vers `chambre_cloche`,
comme dans la crue, pour Ilse, Brune, Maël et Sève. Gorm accueille les évacués ;
Maël connaît Gorm, Sève connaît Aubin/Ilse ; ces deux évacués ignorent les salles
basses. Aucun mandat initial, lien, coût, savoir ou charge `informer` ajouté.
Aucune attribution forcée ni donnée ajustée après mesure ; moteur/MJ identiques
à l'intégration. Le conflit d'état-dev reprend l'intégration puis l'entrée 306.

**69 tests / onze fichiers verts, 149,283 s**, deux travailleurs réduits :
les neuf fichiers ciblés du 306, les huit régressions 358 et les sept tests 335.
Activation unique, Maël/Sève marchant après accord, monde/rendu après recharge,
temps entier/découpé contrôlés. Les deux assertions d'occasions sont strictes :
empreinte complète **85955d0e…**, puis **72a33d77…** en retirant le seul agenda
306 ; six autres empreintes inchangées. Ni suite complète ni Luna.

**Banc hameau 4 h, `main 0bad227` → branche `0c4663a2`.**

| Graine | Proposés / acceptés / refusés | Causes des refus | Galerie réf. → branche | Agenda atteint | Comptes rendus |
|---|---|---|---|---|---|
| 1985 | 6 / 0 / 6 | impossible 6 | 0 → 4 | min 51 | 0 |
| 7 | 5 / 3 / 2 | impossible 2 | 1 → 4 | min 151 | 3 |
| 42 | 8 / 3 / 5 | impossible 2, refus 3 | 1 → 4 | min 135 | 2 |
| 2024 | 0 / 0 / 0 | — | 2 → 4 | min 127 | 0 |

Sous-mandats inclus : **19 propositions, six acceptations, cinq comptes rendus**,
mandats atteints **0/3/3/0**, zéro confirmation/réaffectation. Les quatre personnes
sont à la galerie à t=240 pour chaque graine. **Aucun plantage ni usurpation** ;
quatre captures finales rechargées identiques (monde, rendu, scène, écoute).
Crue d'origine : **4/4 empreintes 2 h identiques** à l'intégration `19c9b6da`
(chronique, mesures, état complet). Les quatre références hameau exactes ont été
**relues du cache**, sans recalcul ; références crue manquantes seules rangées.
Calcul détaché terminé, deux travailleurs réduits, **625,502 s**, `fin.json ok=true`,
codes banc/empreintes **0/0** ; aucun calcul actif, aucun gain de performance déduit.

**Blocage de la première reprise levé.** Sur la capture originale 1985 à t=4200
(SHA-256 **1529ca9f…630c004a**, identique à la fixture 358), le refus de minute 6
bloque désormais l'étape conservée depuis minute 4 : `agir` renvoie **MANQUE**,
sans parole, geste ni modification d'état. Recharges monde/rendu/scène/écoute
et reprises sur deux minutes, en bloc ou quatre demi-minutes, identiques.
Les réessais à 4461 n'ont lieu que lorsque le refus ne tient plus, contrôlé par
espion. **La nouvelle nuit complète ne réexécute plus le mandat à 4200** :
propositions 20 → 19 ; disparaissent aussi les quatre écoutes de cette parole.
Les six acceptations et cinq comptes rendus restent acquis.

**Limites conservées.** Suspects 219 **0/0/0/0 → 0/0/0/0** ; retours à expliquer
**2/2/2/0 → 4/4/13/2**, passages horaires maximaux **12/7/5/8 → 20/25/29/38**.
Une bascule d'état en 1985. Avis et constats sont exactement ceux de la première
reprise (`2d696f65`) : aucune nouvelle alerte ; les **23 retours restent ouverts**.
Maël 42 : neuf réponses « J'arrive », dix « reste près », onze appels, avec des
rencontres et des entrées nouvelles ; leur causalité générale n'est pas certifiée.
Le brasero payé en 42 s'éteint physiquement à min 150, sans violation imputée au
prestataire. Aucun achat promis ni réclamation de Sève dans les quatre nuits.
Zéro suspect ne prouve pas l'absence générale de toute boucle. La comparaison
à `main` inclut les autres lots de l'intégration : aucune causalité exclusive
attribuée au 306. En 2024, aucun mandat jugé ; l'agenda réussit sans délégation,
ce qui ne permet pas de conclure à un refus d'autorité.

**Bruts et conclusion :** `C:/Users/msics/donjon/artifacts/agenda-hameau-306/reprise-358-335/`
(`tests.json`, `verification-capture.json`, comparaisons, captures finales,
`fin.json`, **`conclusion.json` : integration_recommandee=true**, limites explicites).
Première reprise conservée dans `reprise-integration/` et Git `fa537794`.
