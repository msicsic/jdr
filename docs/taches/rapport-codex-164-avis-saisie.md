# Lot 164 — Saisie des avis de menace

Branche `codex-avis-saisie`, **non fusionnée**, base `5bf8840` (intégration).

**Cause et correction.** Les six interprétations historiques du lot 153 donnent
avis/propos/avis puis propos/propos/avis. Dans chaque omission, la carte des
opérations est entièrement fausse : l'omission précède la revue, et le raccourci
des mots exacts l'admet sans contre-revue. Les traces n'expliquent pas le choix
interne de Luna ; elles ne prouvent pas qu'une revue a admis `propos`.
La définition commune exigeait une prévision « dans l'heure », absente des mots
du joueur, et pouvait faire confondre annonce du futur et opinion explicitement
marquée. `paroles.SENS_CONTENU.avis` définit désormais l'annonce d'une menace
future, même certaine et sans échéance. L'heure reste l'horizon du calcul du
prédicat disponible (menace d'eau), pas une condition de formulation. Cette
définition alimente le schéma, l'analyse des opérations et la fidélité.
Le contrôle commun existant refuse déjà un contenu `propos` qui omet une
opération reconnue ; aucun nouveau cas lexical, mode ou effet moteur ajouté.
`mj.py`, les `REGLES`, consignes, assemblage, narration, délibération et
planification sont inchangés. `main` n'a pas été touchée.

**Preuves.** Douze tests d'avis verts après correction d'une assertion qui
confondait réception et adoption : dans la scène réelle, Gorm peut opposer une
observation. Les trois saisies du banc passent par la console/MJ simulé, avec
paroles, réception attestée dans les faits dits, monde complet et rendu après
recharge ; deux lieux positifs et un avis négatif. Une parole ordinaire reste
`propos`, sans revue, et une prévision sur un lieu inconnu est refusée avec
`attendu` sans mutation. Le refus d'une opération reconnue omise est exercé sur
les trois formulations. Neuf tests voisins de parole également verts.
Une première tentative de tests sans élévation a rencontré les permissions des
dossiers temporaires Windows ; reprise avec les permissions nécessaires.
Suite complète unique : **2 224 tests, 254 fichiers, 2 270,737 s**, un worker
réduit, zéro erreur/ignoré, deux échecs MiMo historiques `6 != 5`
(`test_fournisseurs_jeu` et `test_restes_fusions`), identiques à ceux déjà
diagnostiqués aux lots 128/146 e ; aucun fichier fournisseur changé, aucun
nouvel échec. Aucune seconde suite. La vérification à un worker a dépassé le
créneau du petit lot.

**Luna, copies uniquement.** Deux passes d'`avis-joueur`, une de `noms-dialogue`
et `soir-appel`, `gpt-6-luna`, ChatGPT medium/libre, budget 200 : **6/6 avis**,
contre **3/6** dans le cache `cdaf371`. Quatre parties historiques exclusivement
relues, chemins et SHA-256 archivés ; aucun rejeu de référence.

| Script | Appels/tour MJ, référence → branche |
|---|---:|
| avis-joueur p1 | 5,00 → 5,33 |
| avis-joueur p2 | 3,33 → 4,67 |
| noms-dialogue p1 | 3,25 → 3,25 |
| soir-appel p1 | 4,00 → 5,50 |

Total **54 → 65 appels / 14 tours MJ**, soit **3,86 → 4,64**. Aucun arrêt,
incident technique, mention sans fondement ou erreur de recharge. Un repli
narratif sur l'achat de `soir-appel` : paiement et échange acceptés, issue
moteur restituée. Aucun repli sur les avis. Charges différentes : aucune
conclusion de vitesse. Deux exécutions Luna au plus ; suite à un worker réduit
pour cohabiter avec le calcul du lot 163 dans le plafond partagé de deux.

**Limites.** Le résultat 6/6 est une mesure, pas une garantie de toute saisie
libre. Une carte entièrement fausse peut toujours emprunter le raccourci ; le
contrôle déterministe garantit la couverture des opérations reconnues, pas leur
extraction sémantique exhaustive. L'ambiguïté de la définition est corrigée,
sans preuve de causalité unique ni résolution générale du jugement de Luna.
Le harnais Luna recharge les parties et conserve les projections et les textes,
pas le monde complet ; la preuve complète monde/rendu vient des tests console.
Pas de banc PNJ : aucune mécanique ni décision autonome modifiée.
Aucune clé de signature Git configurée ; livraison non signée, branche seule
poussée. Bruts exclusivement dans
`C:/Users/msics/donjon/artifacts/avis-164/` (fils, mesures, références, cause,
tests et suite).
