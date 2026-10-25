# Lot 92 — mesurer les arrêts utiles avant de filtrer

Branche `codex-aller-utile`, **non fusionnée**, base `56581f1` : moteur identique
à **9810f4a**. **Arrêt après mesure, aucune règle P3 implémentée.** Aucun appel
à Luna, changement de scénario, du MJ, de `choisir`, de `main` ou du dépôt principal.

**Protocole.** Auberge 1985, départ tiré, 12 h, tranche **[480, 720] min**
(720 incluse dans ce premier relevé ; le lot 92 b utilise strictement `[480, 720[`).
Un témoin sans comptage, puis observation des expansions et des gestes par
`tools/mesurer_allers_utiles.py` ; deux processus au plus pour ce lot, priorité
réduite. Le témoin n'est pas rejoué. Les points d'observation sont injectés dans
une copie en mémoire de `_explorer_etats`, sans éditer le moteur. Le relevé
structurel couvre aussi les états arrêtés à la profondeur maximale ; sa préparation
des objets est isolée de celle de la recherche pour ne pas anticiper la lumière.

**Décomposition.** Sur la tranche, **1 055 783 expansions**, découvertes comprises
(diagnostic de la dernière passe : 1 051 132 nœuds). Les listes parcourues par la
recherche, reprises de graphe comprises, contiennent **6 321 251 successeurs/groupes** :
`aller` **5 612 068 (88,78 %)**, `ouvrir` **152 292**, `alimenter` **146 869**,
`prendre` **107 309**, groupes différés **105 125**, `manger` **67 870**,
`inspecter` **49 535**, `demander` **46 410**. La génération neuve, distincte des
reprises, produit 4 226 260 gestes/groupes, dont 3 589 733 `aller` (**84,94 %**).

Parmi les 801 724 expansions dont les successeurs sont parcourus, **356 902**
n'ont aucun autre successeur retenu et n'atteignent pas le but (**33,80 %** de
toutes les expansions). **275 973** arrivent par `aller`. Conserver aussi toute
présence d'objet agissable non porté, de porte connue ou de PNJ connu ramène ce
dernier compte à **120 732 (11,44 %)**. Les 254 059 états sans liste parcourue ne
sont pas supposés vides : le majorant structurel sur **toutes** les expansions,
buts et gestes portés encore inclus, est **189 512 (17,95 %)**.

**Pourquoi arrêter.** L'absence de geste ne suffit pas à prouver la domination
d'un arrêt. `trajet_estime.parcours` minimise `cout_route`, alors que
`Vue.prix_route` ajoute la pression de chaque salle : une route plus longue,
sélectionnée en deux trajets, peut coûter moins sous pression. `mesure_aller`
écrit aussi les portes ouvertes/déverrouillées ; l'eau impose passage et retour.
Sans preuve locale de domination, ces situations doivent rester d'intérêt.
Un filtre conservateur écartant toute pression potentiellement variable,
admissibilité d'eau ou effet de porte connue ne laisse **au plus 5 237 états
(0,496 %)**, bien sous le seuil de ~15 %. **184 275** des candidats structurels
sont retenus pour la pression. Les portes inconnues, buts et gestes portés
réduiraient encore ce majorant. Cela ne prouve pas que toute P3 serait inutile :
une preuve locale plus fine sous pression reste à construire, sans gain établi.

**CPU sans instrumentation.** Nuit **371,72 s**, dont **324,52 s entre 8 et 12 h** ;
recherches de la tranche **301,16 s**, soit **285,24 µs/expansion** (préparation,
mémoire et preuves incluses). Principaux PNJ/buts :

| But | CPU recherche | Expansions |
|---|---:|---:|
| Tilo/faim | 65,13 s | 247 522 |
| Lucien/placer:ballot | 47,39 s | 136 214 |
| Joss/faim | 43,02 s | 361 221 |
| Lucien/garder:grenier | 35,98 s | 123 844 |
| Odile/feu:atre | 35,98 s | 76 030 |
| Mathurine/faim | 27,97 s | 36 172 |

**Contrôles et livraison.** Témoin et deux relevés : mêmes empreintes, monde,
chronique, récit, tous les résultats d'appels logiques et 1 175 083 nœuds sur
12 h. Diagnostics identiques hors durées ; monde, regard et scène identiques
après recharge. `empreintes_nuits.py comparer --calcul` : **une nuit, zéro écart**
(affichage CP1252 repris en UTF-8 sans rejouer). Compilation des deux outils et
`git diff --check` verts. Pas de suite complète, de banc CPU à trois versions,
d'empreintes 16 nuits ou de `VERIFIER` : arrêt diagnostique demandé, moteur inchangé.
Une seule nuit ; temps sans affinité, autres lots sur le poste. Les temps des
relevés instrumentés ne mesurent aucun gain moteur.

Bruts : `artifacts/aller-utile/{temoin,comptage,comptage-structure,bilan}.json`,
mondes rechargés et fichiers `*-comparer.json`. Reproduction : lancer l'outil
sans `--compter` vers `temoin.json`, puis avec `--compter` vers
`comptage-structure.json`, enfin `tools/bilan_allers_utiles.py artifacts/aller-utile`.
Piste suivante à mesurer : **P2, pertinence des préparatifs** `ouvrir`, `prendre`,
`alimenter` par rapport au but, notamment faim ; aucun gain P2 démontré ici.
