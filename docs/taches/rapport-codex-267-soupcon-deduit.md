# Lot 267 — Soupçon déduit

Branche `codex-soupcon-deduit`, **non fusionnée**, base `7404d2d`.
Bruts : `C:/Users/msics/donjon/artifacts/soupcon-267/` ; correctif
d'intégration et traces ciblées dans `decoupage/`.

**Invariant.** Les indices de soupçon restent dans le seul registre
`indices_soupcon`, séparé des quarante souvenirs communs, sans lecture de
position cachée ni chronique. Présences et gestes bornés chacun à 40 ;
purge des intervalles dépassés, attribution interdite sur un intervalle
tronqué, validation au chargement. L'épreuve commune reste révisable :
confiance −6 à −18 selon PSY, source `devine`, jamais un portage établi ni
une naissance de récupération sur ce seul indice. Retour, réparation ou
attribution apprise compensent la seule perte effectivement appliquée.

**Correctif du découpage temporel.** Les 25 échecs de temps venaient des
dates fines prises au passage de la boucle (`3000` contre `3005`).
`esprits._date_indices_soupcon` fixe désormais le grain **minute des
croyances**, dans l'unité de stockage antérieure (600 dixièmes/minute).
Présences, gestes, constats, purge, bornes et preuves de déduction partagent
ce grain ; les présences de même date ont un ordre canonique lieu/personne.
Aucun pas supplémentaire ne rafraîchit une date à un autre dixième.
Deux constats dans la même minute ne constituent donc pas un intervalle
distinct pour une déduction. Aucun cas propre à une scène ni modification
des entrées du planificateur ou de la mémoire commune.

**Six hashes historiques.** Sur les quatre captures de complétion, le
retrait du seul champ ajouté retrouve exactement les anciens hashes.
`tests.support.sans_indices_soupcon_passifs` valide le monde complet,
puis n'exclut ce registre de l'oracle ancien qu'en l'absence de **toute
trace d'épreuve**, y compris un soupçon levé : état actif, preuves
relationnelles persistantes, motifs, souvenirs et chronique contrôlés.
Les hashes attendus restent inchangés. Les égalités intégrales du monde
avant/après recharge, plans, visites et rendus restent contrôlées, sans
projection du registre sur les tests de découpage. Contre-épreuve nouvelle :
la projection refuse un soupçon actif puis levé. Les deux captures mine et
auberge des étapes chaînées emploient la même projection restrictive.

**Vérification demandée.** Copie isolée de la fusion d'essai **732e26a**
avec le diff du correctif, pour conserver les autres lots d'intégration.
Tous les fichiers de `echecs-suite-732e26a.txt` (**18 fichiers**), plus les
onze fichiers ciblés du 267 : **29 fichiers**, deux processus réduits,
aucune suite complète ni Luna. Première passe : **314 tests**, aucun
échec de découpage ; seules les six comparaisons historiques ci-dessus
restaient rouges. Les trois nouveaux tests contrôlent les perceptions à
0/5/599 dixièmes et leur ordre après recharge, l'absence d'effet du registre
passif sur `_entrees_communes` et la mémoire, et le refus de la projection
après une vraie épreuve. Les dix-sept tests du soupçon passent séparément,
avec les deux scènes rechargées et leurs contre-épreuves.

Résultat final : **317 tests verts, 29 fichiers, 213,100 s**, aucune erreur,
aucun échec. Les 18 fichiers de la liste sont tous présents ; aucune
assertion de laps ou de recharge supprimée, aucun hash attendu remplacé.
Les six captures historiques retrouvent leurs oracles ; la comparaison
du registre complet fait partie des tests de découpage et de recharge.
Fichiers détaillés : `decoupage/fichiers.txt`, `tests-premiere-passe.json`,
`tests-finaux.json`, `sources-verifiees.json`, `correctif-source.patch`.
Copie de vérification retirée après archivage ; aucun calcul actif.

**Banc antérieur (`27e2aee`).** 20/20 paires 4 h contre `7404d2d` : chronique,
mesures et état final identiques hors seul registre, 20 références en cache,
zéro plantage/usurpation/soupçon né ; suspects 219 2 → 2. Preuves
`registre/identite-verifiee.json` et états bruts archivés. Ce banc précède
le présent changement de grain ; aucun nouveau banc relancé ici, comme
aucune suite complète. L'effet du soupçon est prouvé par les scènes ciblées,
sans bénéfice naturel démontré. Limites : pas de crochetage invisible,
ni disparition distante inventée ; une migration ne recrée pas un souvenir
anciennement perdu. `agendas.py`, `echanges.py`, choix de délibération,
scénarios et MJ inchangés.
