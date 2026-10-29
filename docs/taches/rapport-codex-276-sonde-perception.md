# Lot 276 — entrées perceptives de la sonde 219

29 octobre 2026, laptop. **Branche `codex-sonde-perception`, non fusionnée**,
base `406a795`. Outils seulement : aucun fichier de `donjon/` modifié,
aucune Luna ni suite complète.

**Invariant.** Une différence de perception invalide l'identité stricte des
entrées sans certifier la pertinence du retour. `relever_entrees` photographie
les entités effectivement perçues et leur place par l'API commune `percus`,
ainsi que les sources des croyances, sans réviser celles-ci. L'analyse compare
les sources sur les références structurelles du but et des plans de départ et
de retour, offres imbriquées comprises. Les dates de rafraîchissement seules
ne comptent pas. Aucun nom de personnage, scénario ou geste n'intervient.

`analyser_episodes` nomme les deltas dans `perception_diff_qr`. Si seules des
entrées perceptives changent depuis la sortie, à lieu inchangé, le retour est
`renouvellement_perceptif`. Un changement mêlé à d'autres entrées reste
`entree_nouvelle_a_expliquer`. Les preuves instrumentées, dont l'entrée publiée
employée du lot 271, gardent leur priorité. Le renouvellement n'entre jamais
dans les justifiés ; il entre dans `total_a_expliquer`, les synthèses CLI et
l'alerte `avis_a_expliquer` de l'audit. Sans changement, le suspect demeure.

**Cas réel.** Relais 2024, départ tiré, joueur passif `chambre_cloche`, 4 h :
retour d'Aubin à **117518** classé `renouvellement_perceptif`. Ilse devient
effectivement perçue ; `ilse.lieu` conserve sa valeur mais sa source passe
de **`entendu` à `vu`**. Captures à 117503 et 117518 : monde, rendu et scène
identiques après sauvegarde/recharge, relevés perceptifs également identiques.
Le défaut moteur de clôture à 117503 n'est pas corrigé par ce lot.

**Contre-épreuves.** Une seconde scène d'auberge change seulement la source
de localisation d'Odile ; une autre déplace une lanterne effectivement perçue.
Dans les deux cas, le renouvellement reste à examiner après recharge avec
monde/rendu/scène inchangés. Rafraîchir seulement la date ou changer la source
d'un objet hors des références ne lève pas le suspect. Les scènes existantes
du lot 271 et les contrôles de priorité conservent leur classe justifiée.
Mireille auberge 1985 à **36720** reste signalée
`repetition_sans_entree_nouvelle` à la relecture de l'archive 219 ; celle-ci
ne contient pas les nouvelles entrées perceptives, qui ne sont pas inventées.

**Vérification ciblée.** **37 tests verts, zéro échec ou erreur,
140,797 s**, dans `tests.json` et `tests-finaux.log` ; fichier de la sonde et
trois contrôles du socle agendas, un seul processus réduit.
Les méthodes existantes sont conservées.
Les premiers lancements ont révélé les restrictions Windows sur les dossiers
temporaires et un chemin d'import absent du lanceur ad hoc ; le lancement
final utilise les droits nécessaires et le chemin `tools` prévu par le dépôt.

**Campagne détachée en cours.** Vingt paires de 4 h, cinq scénarios × quatre
graines, moteur de cette branche sur l'intégration actuelle ; une exécution
avec sonde puis une sans, un seul processus réduit. Comparaisons exactes des
mondes, chroniques, mesures, empreintes, récits, souvenirs et vues après
recharge ; états et épisodes bruts archivés. Avant/après : les mêmes épisodes
sont analysés par la sonde de base et la nouvelle, sans rejouer de référence.
Le lot 271 fournit le repère archivé : **1 suspect, 15 à expliquer, 26 entrées
publiées utilisées, 495 cycles, 48 préemptions, 14 changements de moyen,
1 progression, 212 dérives, 4 pertes d'état payé**. Aucun résultat des vingt
paires de ce lot n'est encore déclaré acquis. Relire `bilan.json` et
`fin.json` avant validation du lot ; `fin.json` est écrit en dernier.

**Limites.** Horizon de 60 min et preuves de fin inchangés ; aucun certificat
causal ni identité exhaustive de toutes les entrées possibles du choix.
Une archive dépourvue de relevés perceptifs conserve son classement historique,
sans inventer les perceptions manquantes. La source est comparée sur les
cibles structurelles connues des plans ; aucune nécessité contrefactuelle
n'est démontrée.

Bruts : `C:/Users/msics/donjon/artifacts/perception-276/` : scripts et sources,
tests, relecture historique, `aubin.json`, vingt archives des paires,
`bilan.json`, `sources-campagne.json`, journal et **`fin.json` attendu**.
