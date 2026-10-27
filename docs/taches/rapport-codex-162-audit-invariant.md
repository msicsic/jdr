# Rapport 162 — schéma invariant de l’audit narratif

27 octobre 2026 — branche `codex-audit-invariant`, **non fusionnée**, base `c22541b`.

**Invariant.** `narration.schema_audit` expose une liste de qualifications portant
un indice entier, les douze variantes nature/portée et les trois extractions
(rappels, comptes, éclairages) à chaque appel. Les sources sont des chaînes.
`controler` ramène cette liste au même contrôle de couverture que les anciens
rapports par clés : indices uniques, entiers, ordonnés, aucun segment étranger
ou manquant ; les reprises exactement établies sont prouvées de nouveau.
Sources inconnues toujours écartées, mécanique sans source refusée avec
`attendu`, contradiction sans source illisible. Verdict canonique, contrôles
mécaniques et relecture à l’enregistrement conservés. La seule adaptation de
consigne décrit la liste avec indices ; aucune nouvelle règle narrative.
Aucun changement de `mj.py`, `consignes.py`, sources, fournisseur ou scénario.

**Preuves déterministes.** Deux scènes console, crypte et Relais, textes libres
et mélangés aux attestations : schémas identiques malgré des indices/dossiers
différents, état et texte conservés après recharge. Indices invalides et sources
inconnues comparés aux rapports anciens, jusqu’à la console et la sauvegarde.
Relecture des **86 audits de référence : 86 décisions identiques**, zéro erreur,
**14 refus** recensés. Les 14 références `cdaf371` sont des copies des parties
cachées ; correspondances et SHA-256 vérifiés, aucun rejeu de partie de référence.

**Mesure du schéma**, `tools.mesure_prompt.mesurer`, mêmes 86 appels archivés :
**50/72 variations → 0/72**, outils après mutualisation **22 422 → 22 107
caractères** en moyenne. Le **44/74** du lot 158 concerne ses propres parties,
indisponibles ici ; il n’est pas assimilé à ce corpus `cdaf371`. Projection hors
réseau, pas une mesure de cache acquis ni de délai.

**Deux passes Luna**, sept scripts demandés, 84 tours MJ par variante :

| Mesure | Référence → branche |
|---|---:|
| Appels / appels par tour | 282 / 3,36 → 288 / 3,43 |
| Secondes par tour | 11,13 → 11,49 |
| Audits / secondes par audit | 86 / 3,41 → 90 / 3,56 |
| Relances / refus moteur-contre-revue | 13 / 23 → 22 / 27 |
| Audits refusés / illisibles / replis | 14 / 0 / 0 → 23 / 1 / 2 |
| Variations réelles de l’outil d’audit | 50/72 → **0/76** |

Zéro arrêt, erreur technique ou défaut de recharge. Jetons cachés par voie :
interprétation **720 256 → 913 792**, audit **555 776 → 826 368**, révision
**105 088 → 276 096**, contre-revue **16 896 → 1 408**, récit **4 352 → 0**,
fidélité zéro. **Aucun gain de vitesse démontré.**

**Réserve de validation : critère des refus non déclaré atteint.** Quatorze
audits refusés, cinq rejeux par version, **140 appels**, zéro erreur technique,
deux illisibles côté branche. Trois pertes brutes dépassent un refus : pierre
non perçue **3→1**, approbation accompagnant une parole **3→0**, description de
conduite/éclairage **4→2**. Le premier est une confusion non-perception/absence ;
les autres mêlent gestes, ambiance et motifs discutables. Aucun tri opportuniste
ni nouveau rejeu ne retire ces écarts du bilan ; la conservation de chaque cause
juste n’est pas démontrée. Les contrôles déterministes restent identiques sur
les rapports archivés ; aucune correction particulière ni consigne narrative
supplémentaire pour ces exemples.

**Suite et empreintes.** Suite unique : **2 214 tests, 253 fichiers, 1 899,24 s**,
un travailleur réduit, zéro erreur/ignoré ; deux échecs MiMo historiques `6 != 5`,
reproduits avec `narration.py` intact de `c22541b` (les autres fichiers du jeu
sont inchangés). **73 ciblés**, puis **17 ciblés** et **trois tests finaux verts**,
dont les refus en console/recharge. **4/4 empreintes Relais × 2 h identiques**
à `main` `812ebe5` : chronique, mesures, état complet ; quatre références relues
du cache sans rejeu, temps non comparés. Aucune seconde suite complète.

**Limites.** Invariance du contrat et couverture déterministes ; choix de la
nature, extraction et justesse sémantique restent dépendants de Luna.
Références historiques et poste partagé : aucun gain causal de vitesse garanti.
Pas de serveur local mesuré, fournisseur inchangé. Les fils Luna ne contiennent
pas le monde complet ; sa conservation est prouvée par les tests console. La suite tourne à un seul
travailleur réduit pour cohabiter avec le lot voisin ; deux exécutions Luna au
plus, copies seulement. Les journaux produits par défaut par les tests ont été
déplacés puis redirigés hors du worktree. Bruts et scripts exclusivement dans
`C:/Users/msics/donjon/artifacts/audit-162/`. Aucune clé de signature Git
configurée : commit non signé, branche seule poussée. `main` intacte.
