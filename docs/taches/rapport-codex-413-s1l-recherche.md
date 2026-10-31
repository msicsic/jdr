# Lot 413 — S1l, recherche d'une personne par la porte commune

31 octobre 2026, PC fixe · `codex-s1l-recherche` · base exacte `integration 40f062d8`.
Moteur mesuré : **`dd80f067`**. **Tests terminés ; empreintes en cours, lot non encore clos.**

**Invariant et code.** Les trois registres historiques `recherches`,
`indices_recherche` et `presence_recherche` passent par `donjon/memoire.py`.
Les vues nommées rendent des copies profondes, ou un ensemble neuf, pour un
observateur explicite, sans création d'esprit ni acquittement. Les opérations
retiennent ensemble l'échec et ses indices consommés, admettent l'indice nouveau,
gardent le dernier repère positif malgré l'absence et rouvrent le lieu du contact.
Migration et validation sont portées ; les façades de `deliberation` restent
compatibles, y compris pour l'instrumentation. Les lecteurs de `appel`,
`echanges`, `planification` et deux outils utilisent les vues. La sonde des
empreintes charge sa propre porte pour lire aussi une référence sans cette API.

**Politiques conservées.** Même contenu, force, précision et voix définissent
l'identité des indices ; date, confiance, relais et absence seuls ne rouvrent pas
un lieu. Les retrouvailles et réponses effectivement saisies gardent leur effet
local. La consommation des hypothèses expirées du 374 reste dans l'interface
de croyances existante. Aucun nouveau registre, schéma de sauvegarde, choix,
parole, délai, tirage, classement ou appel modèle.

**Contrôle et tests.** Inventaire AST fermé **154 → 60 expressions** hors porte :
la déclaration exacte du schéma et 59 homonymes de diagnostic, **zéro accès au
stockage de recherche**. Contre-épreuves de clés indirectes, alias, boucles,
méthodes détachées, retours et mutations. Six nouveaux tests couvrent les copies
imbriquées aux frontières, l'éviction après 45 épisodes et les absences répétées,
les hypothèses consommées, la migration, les corruptions, l'inspection et le
contact entendu. Captures réelles : mine 7 à 470 (Odon/Lucien) et auberge 7 à 625
(Odile/Joss), dix minutes entières ou quatre puis six minutes avec recharges ;
comparaison de l'état complet, de l'ordre JSON, des lignes, du rendu, de la scène
et des émissions. **218 tests distincts sur 17 fichiers**, dont les six nouveaux
tests verts : les captures dans `tests-cibles.json`, les cinq autres dans
`tests-porte-finale.json` ; **129/129 voisins verts** (`tests-voisins.json`).
Les trois sous-échecs initiaux provenaient de deux nouvelles éprouvettes :
mutation du tableau passé à l'ancienne admission de croyance, puis confusion
entre le lieu inspecté et celui du contact. Oracles corrigés, moteur inchangé ;
les rouges initiaux sont conservés. L'import direct d'une classe de tests a
été remplacé par celui du module pour éviter sa double découverte.

**Empreintes attendues.** 2 h × graines 1985/7/42/2024 × Relais/mine/auberge/crue,
contre la base exacte `40f062d8`, sans exclusion d'état. Référence puis branche,
cache partagé, deux travailleurs réduits au plus ; aucun temps CPU à comparer
au cache. Pas de suite complète ni Luna. Le calcul long est détaché, avec
`C:/Users/msics/donjon/artifacts/s1l-413/fin.json` écrit en dernier.

**Limites et voisinage.** Contrôle AST syntaxique local, sans preuve de tous les
flux interprocéduraux Python ; politiques historiques conservées. Aucune
modification de `mj.py` ou `comprehension.py` (lot 412) ; le lot 402 reste un calcul
indépendant. L'avance documentaire `origin/integration d54d15ae` est à intégrer.
Le premier lanceur s'est arrêté avant les empreintes sur son chemin d'import,
puis sur le module homonyme `tools/tests.py` ; erreurs de lancement conservées,
aucun rejeu des tests verts ni des captures.
Bruts : `C:/Users/msics/donjon/artifacts/s1l-413/`.
