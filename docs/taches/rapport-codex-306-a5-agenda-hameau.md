# Lot 306 — agenda d'évacuation du hameau

Branche **`codex-a5-agenda-hameau`**, non fusionnée, base initiale `7ec839e`.
Reprise laptop du 30 octobre 2026 : fusion sans rebase de l'intégration
`c9b066bb` dans `0a12fd12`, commit mesuré **`2d696f65`**.
**Livraison close ; données et tests validés, banc non validé pour intégration.**
Un refus de mandat encore valable ne bloque pas sa réexécution différée.

**Invariant.** Gorm reçoit `evacuer_crue`, `amener` vers `chambre_cloche`,
comme dans la crue, pour Ilse, Brune, Maël et Sève. Gorm accueille les évacués ;
Maël connaît Gorm, Sève connaît Aubin/Ilse ; tous deux ignorent les salles basses.
Aucun mandat initial, lien, coût, savoir ou charge `informer` ajouté ; aucune
attribution forcée ni donnée ajustée après mesure. Moteur et MJ inchangés.

**54 tests / neuf fichiers verts, 143,892 s**, deux travailleurs réduits :
agendas/autorité du hameau, occasions, scénario hameau, faire/confier, devis de
l'observateur, compte rendu, réaffectation, récit d'agendas. Activation unique,
Maël/Sève marchant après accord, monde/rendu/scène/écoute rechargés et temps
découpé vérifiés. Passe retenue hors sandbox (temporaires Windows bloqués dans
le premier essai). Les deux assertions du conflit d'occasions restent strictes :
empreinte complète **85955d0e…**, puis **72a33d77…** en retirant le seul agenda 306 ;
les six autres empreintes sont inchangées. Ni suite complète ni Luna.

**Banc 4 h, référence `main` `0bad227` → branche `2d696f65`.**

| Graine | Proposés / acceptés / refusés | Causes des refus | Galerie réf. → branche | Agenda de Gorm atteint | Comptes rendus |
|---|---|---|---|---|---|
| 1985 | 7 / 0 / 7 | impossible 7 | 0 → 4 | min 51 | 0 |
| 7 | 5 / 3 / 2 | impossible 2 | 1 → 4 | min 151 | 3 |
| 42 | 8 / 3 / 5 | impossible 2, refus 3 | 1 → 4 | min 135 | 2 |
| 2024 | 0 / 0 / 0 | — | 2 → 4 | min 127 | 0 |

Sous-mandats inclus : **20 propositions, six acceptations, cinq comptes rendus**,
mandats atteints **0/3/3/0**, zéro confirmation/réaffectation. Quatre destinataires
comptés à t=240 ; aucune causalité exclusive attribuée au 306 face à `main`.
**Aucun plantage/usurpation**, quatre captures finales rechargées identiques
(monde, rendu, scène, écoute). Crue d'origine : **4/4 empreintes 2 h identiques**
à l'intégration `c9b066bb` (chronique, mesures, état complet).

**Limite bloquante instruite.** Graine 1985, sept tentatives `impossible` de
confier Sève vers la galerie, minutes 4–7. À **t=4200 (min 7)**, le plan conservé
depuis la minute 4 contient encore `confier` à Maël ; `refus_retenu` retourne le
refus de minute 6 pour exactement ce mandat, mais l'acte est réexécuté.
Relecture instrumentée limitée à **8 min**, chronique exactement préfixe du
banc ; sept captures et leurs recharges monde/rendu/scène/écoute identiques.
C'est un défaut du contrat commun de revalidation d'une action différée après
refus, à corriger dans un lot moteur distinct, interdit dans le 306.

**Autres observations.** Suspects 219 : **0/0/0/0 → 0/0/0/0** ; retours à expliquer
**2/2/2/0 → 4/4/13/2**, passages horaires maximaux **12/7/5/8 → 20/25/29/38**.
Une seule bascule d'état en 1985. Maël 42 : appels/rencontres répétés, entrées
nouvelles observées sans preuve causale générale ; 23 retours restent ouverts.
Aucun achat promis ni réclamation de Sève dans ces quatre chroniques nouvelles :
les deux défauts de l'ancien banc ne s'y reproduisent pas. Le zéro du détecteur
ne garantit pas l'absence de répétition continue, comme le montre t=4200.
En 2024, aucun jugement de mandat : les estimations varient déjà avant min 1
(direct 0,842 contre Aubin 1,575 à t=97 ; Aubin 0,772 contre direct 0,884 à t=147,
puis direct 0,260 à t=282). Préfixe de 1 min reproduit à l'identique ; ce relevé
ne prétend pas expliquer à lui seul les quatre heures sans délégation.

**Calcul terminé**, deux processus réduits, **936,969 s** sur le laptop ; les
quatre références hameau absentes ont été seules jouées puis rangées dans le
cache commun ; branche ensuite. Les quatre références crue manquantes ont été
rangées également. Aucun gain de performance déduit, aucun calcul actif.
`fin.json` conserve **ok=true** (achèvement technique) ; **`conclusion.json` porte
validation_integration=false**. Bruts : `artifacts/agenda-hameau-306/reprise-integration/`
(comparaisons, tests, captures, `diagnostic-repetitions.json`, `conclusion.json`).
Ancien rapport/mesures conservés dans Git `0a12fd12` et les archives du PC fixe.
