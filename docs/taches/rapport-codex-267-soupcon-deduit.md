# Lot 267 — Soupçon déduit

Branche `codex-soupcon-deduit`, **non fusionnée**, base `7404d2d`.
Bruts : `C:/Users/msics/donjon/artifacts/soupcon-267/` ; correctif du
registre et vérifications en cours dans le sous-dossier `registre/`.

**Invariant corrigé.** Les indices d'une déduction ne prennent aucune des
quarante places de la mémoire commune. `esprits._retenir_presence` écrit
uniquement dans `indices_soupcon`, registre séparé qui réunit présences,
gestes datés, constats de biens, soupçons actifs et bornes d'oubli. Il n'ajoute
aucun souvenir ni nom et ne consulte aucune position cachée. Les dates fines
des gestes restent également dans ce registre : aucun champ ajouté au
souvenir commun, aucune modification de l'identité de sa preuve.

Présences et gestes sont chacun bornés à **40 entrées** ; les passages d'une
même personne dans un même lieu sont rafraîchis. `_purger_indices_soupcon`
retire ce qui précède le plus ancien constat utile de chaque lieu ; quand
cet intervalle avance ou disparaît, les anciens indices sont supprimés.
Une troncature de capacité marque l'intervalle incomplet : oublier un second
passant ne transforme pas le premier en suspect unique. Structure, dates,
lieux et bornes sont validés au chargement. Les anciens champs du 267 et ses
souvenirs de présence sont migrés ; un souvenir déjà évincé par une ancienne
version ne peut pas être reconstruit.

L'inférence conserve ses deux constats propres et son épreuve relationnelle
commune : un seul suspect, confiance **−6 à −18 selon PSY**, preuve **0,4**,
source `devine`, jamais un portage établi. Geste connu/propre et extinction
par épuisement exclus ; conséquences concomitantes regroupées. Retour,
réparation ou attribution apprise lèvent l'indice en compensant la seule
perte appliquée. Aucune naissance de `récupérer` sur ce seul indice.

**Vérifications ciblées : 121 tests, 120 verts, un échec préexistant de dette**,
onze fichiers, **51,858 s**, deux processus réduits. Les onze tests de scènes
existants passent, avec monde/rendu/scène rechargés, laps entier/découpé,
Gorm/réserve et Anselme/coffre et leurs contre-épreuves. Trois nouveaux tests
contrôlent l'absence d'éviction commune après saturation, la purge des
intervalles et le refus au chargement d'un registre trop grand, mal daté ou
d'un lieu inconnu. Captures `registre/{relais,auberge}.json`, traces
`registre/tests.json`. Ni suite complète ni Luna.

L'échec isolé de
`tests.test_relations_graduees.TempsEtContratsTests.test_dette_soldee_une_fois_par_demande_acceptee`
est déjà prouvé sur **7404d2d** et **61a1a67** : chacun 1 échec `40 != 20`,
ligne 325, aucune erreur, même fichier de test. Preuves `dette-base` et
`dette-branche` JSON/log ; le même échec subsiste dans les 121 ciblés.

**Banc du correctif à valider.** Comparateur commun, référence exacte
`7404d2d`, cinq scénarios × graines 1985/7/42/2024, **4 h**, départ tiré,
deux travailleurs réduits au plus, détachés. Les **vingt références sont en
cache** : le lanceur interdit leur rejeu et ne calcule que la branche.
Il conserve l'état final brut et une empreinte supplémentaire excluant
**uniquement `esprits[*].indices_soupcon`** ; aucun autre champ normalisé.
Critère : égalité des vingt chroniques, de toutes les mesures et des états
hors ce seul registre. États complets de branche archivés pour préciser
un éventuel écart restant. Contrôle du lanceur sur trois minutes simulées
réussi. Résultats attendus `registre/comparaison.json`, fichier écrit en
dernier **`registre/fin.json`** ; aucune identité encore déclarée.

Le diagnostic précédent contre la base (ancien code `61a1a67`) est conservé
dans `bilan-base.json` et `localisation-base/` : à **39 min 31 s**, Ilse
oubliait son abri après occupation de 11/40 places par les présences ;
neutraliser ce stockage rétablissait la base sur 40 min. Le banc contre
`main c870c8b` n'isolait pas le lot ; ses baisses de richesse ne lui sont pas
attribuables. Effraction limitée à une dégradation constatée, sans
crochetage invisible ni disparition distante inventée. `agendas.py`,
`echanges.py`, choix de délibération, scénarios et MJ inchangés.
