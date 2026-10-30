# Lot 331 — achat de planches : une attente devenue périmée

29 octobre 2026. Branche `codex-achat-planches`, **non fusionnée**,
base `origin/integration 7e65907`. Bruts :
`C:/Users/msics/donjon/artifacts/planches-331/`.

**Verdict : changement légitime du lot 312, moteur inchangé.** Le test
d'audience attendait un refus parce qu'Aubin ne connaissait pas le lieu
de Corvus. Cette ignorance permet désormais une recherche de contact ;
elle ne prouve plus qu'une livraison soit impossible. Le débit de trois
pièces rémunère une livraison différée effectivement réalisée.

**Bissection sur les parents directs :** onze versions natives du test,
de son introduction `d60b80a` au point de départ du lot ; 127,301 s,
sur copies `git archive`. Parent direct **`2ddfbe0` vert**, fusion enfant
**`6be4bac` rouge** (`23 != 26`). Le changement de code vient de
`cf0adfd`, porté par la branche du lot 312. Résultats et journaux dans
`bissection.json`, `bornes.json`, `test-*.log` ; `fin-bissection.json`
porte `ok=true`.

**Cause prouvée par deux rejeux sans réseau.** La parole et sa proposition
restent identiques : `demande(planches, prix=3)`, destinée à Aubin.
Dans les deux versions, ses croyances ne localisent pas Corvus.
Sur le parent, `planification._devis_remise` exige d'atteindre la salle
connue du destinataire : devis `None`, part provisoire retirée, aucun
paiement, bourse à 26 après remboursement des deux pièces précédentes.
La fusion admet d'abord l'acquisition, puis `_localiser` prépare le
contact : prendre `planches_1`, aller à l'échoppe, inspecter en cherchant
Corvus. `echanges._remettre_part` réserve une part, inscrit l'engagement
payé et débite trois pièces ; `paroles._part_vendue` établit le fait de
livraison future, les comptes moteur affichent le paiement et la part
encore due. La sauvegarde contient la part et l'engagement. Dans le rejeu
actuel de la scène d'origine, Aubin acquiert la part à la première minute
et la remet à la troisième ; engagement soldé, propriété et possession
à Corvus, bourse à 23 sans deuxième débit. Sources : `cause-2ddfbe0.json`,
`cause-6be4bac.json`, `diagnostic.json`.

**Changement du test.** `tests/test_audience.py` déclare son lot
non transportable (`mobile=False`) : le refus attendu dépend maintenant
d'une impossibilité matérielle explicite. Toutes les assertions
historiques restent, dont bourse à 26, deux charges, deux appels MJ,
audience et texte ; absence de part détachée et d'engagement ajoutée.
Le nouveau test garde séparément la scène réelle avec lot transportable
et un achat de fagots à Joss dans l'auberge. Il rejoue d'abord la réclamation
réelle : sans elle, Aubin rembourse spontanément l'ancienne dette pendant
la livraison, indépendamment du prix de l'achat. Boucle console complète,
MJ simulé : débit et crédit exacts, charges, part réservée, engagement
payé, annonce visible, livraison en trois minutes, propriété, possession,
souvenir d'engagement tenu et absence de second paiement. État complet,
scène perçue et rendu comparés après recharge avant et après livraison.

**Vérification ciblée : 21/21 tests verts**, zéro échec, erreur ou saut.
Fichier entier `test_audience.py` (**10**), puis `test_parts_achetees.py`
(**5**) et `test_livraison_inconnue.py` (**6**), **185,931 s** au total.
`fin-verification-finale.json` porte **`ok=true`**.
Deux passes initiales conservées : neuf tests historiques verts ; nouveau
test arrêté d'abord sur le libellé de l'annonce, puis sur le remboursement
spontané de l'ancienne dette. Attente du libellé et séquence réelle du
nouveau test corrigées, sans modifier les assertions historiques.
Un seul travailleur de calcul, priorité `BelowNormal` vérifiée.
Ni Luna, banc PNJ, empreintes ni suite complète : aucun code moteur ne
change. Aucun recouvrement de code avec G17/326 : `paroles.py` et
`dialogues.py` restent inchangés.
Branche poussée vers origin, non fusionnée ; aucun calcul du lot actif.
`fin-lot.json` consigne le commit livré et le résultat de la poussée.

**Limites.** Le verdict porte sur cette trajectoire et ces deux achats,
pas sur toutes les livraisons ou toutes les interprétations libres.
L'absence de lieu connu reste une recherche incertaine ; elle ne garantit
pas une livraison universelle. Aucune modification du contrat du lot 312.
