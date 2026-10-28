# Lot 267 — Soupçon déduit

Branche `codex-soupcon-deduit`, **non fusionnée**, base `7404d2d`, code
`27e2aee`. Bruts : `C:/Users/msics/donjon/artifacts/soupcon-267/` ;
correctif du registre et vérifications terminées dans `registre/`.

**Invariant corrigé.** Les indices d'une déduction ne prennent aucune des
quarante places de la mémoire commune. `esprits._retenir_presence` écrit
uniquement dans `indices_soupcon`, registre séparé qui réunit présences,
gestes datés, constats de biens, soupçons actifs et bornes d'oubli. Il n'ajoute
aucun souvenir ni nom et ne consulte aucune position cachée. Les dates fines
des gestes restent également dans ce registre : aucun champ ajouté au
souvenir commun, aucune modification de l'identité de sa preuve.

Présences et gestes sont chacun bornés à **40 entrées**. Les présences
répétées sont rafraîchies ; `_purger_indices_soupcon` supprime ce qui précède
les intervalles utiles. Une troncature interdit l'attribution sur l'intervalle
incomplet : oublier un second passant ne désigne pas le premier. Structure,
dates, lieux et bornes sont validés au chargement ; anciens champs et
souvenirs de présence du 267 migrés.

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
contrôlent saturation sans éviction commune, purge et refus des registres
invalides au chargement. Captures `registre/{relais,auberge}.json`, traces
`registre/tests.json`. Ni suite complète ni Luna.

L'échec isolé de
`tests.test_relations_graduees.TempsEtContratsTests.test_dette_soldee_une_fois_par_demande_acceptee`
est déjà prouvé sur **7404d2d** et **61a1a67** : chacun 1 échec `40 != 20`,
ligne 325, aucune erreur, même fichier de test. Preuves `dette-base` et
`dette-branche` JSON/log ; le même échec subsiste dans les 121 ciblés.

**Banc validé : 20/20 paires identiques hors seul registre.** Référence exacte
`7404d2d`, cinq scénarios × graines 1985/7/42/2024, **4 h**, départ tiré,
branche `27e2aee`. Comparateur commun : **vingt références lues dans le
cache, aucune rejouée ; vingt nuits de branche calculées**. **20/20
chroniques, toutes les mesures et les états finaux hors registre sont
identiques**. Les états bruts diffèrent dans chaque paire uniquement par
**`esprits[*].indices_soupcon`**, absent de la base. Aucune autre exclusion
ni normalisation. Recalcul indépendant des empreintes des vingt états
complets archivés : hash brut conforme à la capture ; après retrait du
seul registre, hash exactement égal à celui de la base.

**Zéro plantage/usurpation, zéro soupçon né dans chaque nuit** ; aucun
effet hors registre observé sur ce banc. La preuve du soupçon vient des
scènes ciblées, sans gain naturel démontré. Suspects 219 **2 → 2**, sans
hausse par nuit (auberge 2024 et crue 7 : 1 → 1 ; autres : 0 → 0), à expliquer
**55 → 55**, dérives **233 → 233**, cycles **489 → 489**. Richesse S/F/D
identique, puisque les chroniques sont inchangées. Calcul détaché réduit,
deux travailleurs au plus, **349,601 s**, `fin.json` code **0** ; aucun
calcul actif. Preuves : `registre/comparaison.json`, `registre/fin.json`,
`registre/identite-verifiee.json` (empreintes et chemins exclus par nuit),
`registre/etats-branche/*.json.gz`, `registre/banc.log`.

Ancien défaut d'Ilse à **39 min 31 s** corrigé par l'isolement du registre ;
diagnostic conservé dans `localisation-base/`. L'ancien banc contre
`main c870c8b` n'isolait pas le lot. Limites : identité vérifiée sur ces
vingt nuits, migration incapable de recréer un souvenir déjà perdu ;
effraction par dégradation constatée seulement, sans crochetage invisible
ni disparition distante inventée. `agendas.py`, `echanges.py`, choix de
délibération, scénarios et MJ inchangés.
