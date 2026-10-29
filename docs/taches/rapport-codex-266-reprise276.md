# Lot 266 — raccord à l'intégration et cas historique 276

29 octobre 2026, branche `codex-rester-pres`, **non fusionnée**.
Fusion sans rebase d'`origin/integration` **`1852d6e`**, commit **`18c5523`**
(parents `6779d43` / `1852d6e`). Les deux historiques d'`etat-dev` sont conservés.
Dans `_percevoir`, ordre demandé : `_purger_indices_soupcon`, import de
`retenir_detresses`, agrégation de son changement, puis garde commune de réveil.
**Aucun autre correctif moteur dans cette reprise.**

**Première divergence constatée, Relais 2024**, départ tiré, joueur passif
`chambre_cloche` : **`t=288` (28,8 s)**, après quatre changements de décision
et 24 entrées de chronique identiques. Sur les deux côtés, Aubin cherchait à
nourrir Brune. Après le moyen manqué, l'intégration clôt ce parent et adopte
`proposition vivres`, achat à 1 pièce. La branche **conserve**
`pulsion {vivres, servir: brune}`, reprend par un achat à 2 pièces avec
`remettre_part: true`. C'est la correction commune « moyen manqué ≠ raison
démentie », appliquée ici à la faim. **Ce n'est pas une naissance de `pres`** :
la première intervient seulement à `130200` (217 min), après l'heure du retour
historique. Aucun personnage, tarif ou scénario n'a été corrigé spécialement.

**Le cas 276 relève du même invariant.** Sur l'intégration, avant `117503`,
Aubin porte `servir ilse`, raison `faim`, depuis 195 ; le geste `demander` reste
marqué manqué à cette minute. Ilse n'est plus perçue mais reste crue affamée,
et `_fin_demande` ne trouve pas de fin. Le parent est pourtant clôturé sur
`manque`, puis renaît à `117518` quand Ilse redevient visible. Sur **la même
capture avant choix**, le moteur actuel garde but, date d'adoption et raison,
en attente d'un moyen ; il ne recopie pas le geste manqué. Monde, rendu et
scène sont identiques après recharge. Cette preuve complète le diagnostic 272.
La disparition du retour est ainsi attribuée au maintien commun de la raison
de secours ; la capture avant l'ancienne clôture l'éprouve directement.

**Test de sonde désormais indépendant de la nuit.**
`tests/data/sonde-276-aubin-relais-2024.json.gz` contient le monde de
l'intégration **avant le choix à `117503`**, les états réellement observés après
`117503` / `117518` et les 30 épisodes bruts d'Aubin jusqu'au retour.
`test_aubin_relais_2024_perception_nommee_et_recharge` recharge les états et
réanalyse cette trace avec la sonde actuelle : **aucun classement figé**.
Les tuples de l'API perceptive sont restaurés après le décodage JSON.
**Ses dix assertions sont strictement identiques**, contrôle AST ; elles
exigent toujours Ilse perçue, provenance `entendu → vu`, classement à examiner
et identité des relevés/monde/rendu/scène après recharge. Le nouveau test de
`test_contrat_engagement` vérifie séparément le maintien actuel du parent.
Les deux preuves locales sont vertes.

**Validation terminée : 380 tests verts / 34 fichiers ciblés**, les 19 de la reprise 266,
la sonde 276 et les contrats communs d'appel/recherche/parts/rendez-vous du 275,
le socle agendas et le soupçon 267 qui croise le conflit perceptif.
**846,205 s, zéro échec, zéro erreur, zéro ignoré** ; `fin-verification.json`
porte le code **0**. Code de la fusion `18c5523`, capture et tests du commit
`98c6d2b`. Deux travailleurs détachés à priorité réduite ; **pas de suite complète**, pas
de nouveau banc : seulement les deux rejeux diagnostiques demandés, successifs.
Les erreurs DPAPI de `test_connexion` signalées par le superviseur sont hors
de cette sélection. Clôture sur lecture des résultats, sans nouveau calcul ;
la branche reste non fusionnée.

Bruts : `C:/Users/msics/donjon/artifacts/rester-266/reprise-276/` :
`integration/`, `branche/` (décisions, chronique, captures, retours),
`divergence.json`, `preuve-parent.json`, `assertions.json`, `tests.json`,
`tests.log`, **`fin-verification.json` (code 0)**. Aucun calcul actif.
