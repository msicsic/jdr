# Lot 365 — Connaissance des entités dans les catalogues

Branche `codex-catalogue-connu`, base intégration `dea991a5` ; code final
`f8bf55b2`. **Lot validé, non fusionné.**

**Invariant.** Un mot commun à un nom/alias privé et au contexte ne constitue
pas un apprentissage. `_cites_du_contexte`, commun aux choix d'information,
accords et résolution des références, ne consulte plus le lexique pour faire
connaître une identité. Sources : répertoires perceptifs, souvenirs, termes
typés des missions publiques et engagements, mémoire de Corvus, renseignements
prononcés et entendus dans les résolutions typées des émissions. Aucun parcours
des liens physiques, dossiers privés des PNJ, brouillons ou récits cosmétiques.
Les prémisses déclarent dans `connus` l'anneau de la crypte, la cloche du Relais,
l'âtre, le coffre du marchand et les lits du dortoir de l'auberge ; aucun cas
particulier dans le moteur. Noms de personnes, positions et accès gardent leurs
contrôles distincts.

**Diagnostic.** Copies originales du 364 absentes du laptop : reconstruction
huile/verrou par ses mêmes fabriques, ancien lecteur relu au commit `197c0600`.
Le compteur exact de **seize n'est pas reproduit** : 42/47 sujets et 17 cibles
d'accord non perçus pour cette reconstruction et cet ancien lecteur. Identités,
références publiques et chemins lexicaux sont dans `diagnostic.json` et
`analyse-cloture.json`. Sur la base actuelle, les alertes de sujets sont :

| Scène | Admissions sans vue ni souvenir de position | Qualification |
|---|---|---|
| Huile | `atre`, `coffre_marchand`, `bourse_anselme`, `foin`, `paillasse_joss` | Deux savoirs de prémisse ; trois fuites lexicales |
| Verrou | `atre`, `coffre_marchand`, `bourse_anselme`, `foin`, puis Anselme, Hugues, Lucien, Mathurine, Mireille, Tilo | Deux savoirs de prémisse, six noms déclarés connus ; deux fuites |

« Ta bourse » ne désigne pas la bourse d'Anselme ; une mention de paille
n'identifie pas la meule du grenier. Les identités admises atteignent réellement
`information` et `accord` de l'état web et les formulaires, pas seulement une
liste interne. Après correction : zéro alerte huile ; six alertes verrou,
toutes les six des noms déclarés connus ; zéro cible d'accord inconnue.

**Vérification.** **154 tests distincts, 15 fichiers : 153 réussis, un saut**
(`jsonschema` facultatif absent), aucun échec restant. Scènes E6 et Relais,
homonymes, alias/clés techniques, conversation sans admission, liens privés,
choix forgés et renseignement entendu ; état complet, scène, fiche et catalogues
après sauvegarde/recharge ; voisins noms, projection, menus U-M/U-T et accords.
Les erreurs initiales de préparation et de sonde sont corrigées ; les deux
tests de choix du bien « bois » déclarent son souvenir, sans retirer leurs
assertions d'effet/refus. Consolidation par fichier, voisins verts non relancés.

Empreintes **2 h × quatre graines × Relais/auberge** contre `dea991a5` :
8/8 entièrement identiques sur `d21a9ee2`. Sur les données finales, nouveau
relevé des huit nuits : chronique et mesures identiques ; le seul delta de
l'état complet est l'ajout à `connus` des savoirs de prémisse ci-dessus.
Preuve : empreinte du résultat complet, puis empreinte d'une copie privée de
ces seuls ajouts, identique à la référence. Le monde joué n'est pas modifié.
Deux travailleurs réduits au plus, références en cache ; aucune comparaison
de temps CPU, suite complète ou Luna. Bruts :
`C:/Users/msics/donjon/artifacts/catalogue-365/`, `fin-reprise.json` : valide.

**Limites.** Pas de migration lexicale d'une ancienne mention uniquement en
prose ; un renseignement entendu reste un ouï-dire sans garantir sa vérité ni
l'accès à son objet. Pas de compilation libre E6 ni retrait de ses contrôles.
Recouvrement avec le 360 fusionné : `paroles.py`, lecteur de connaissance seul.
