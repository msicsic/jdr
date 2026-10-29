# Lot 329 — G20, signes et attitudes rendus par le moteur

Lot clos après lecture de la passe unique : **G20 partiel, validation réelle
en échec ; branche non validée pour intégration**. Branche `codex-g20-signes`,
**non fusionnée**, base
`origin/codex-g5-perception c4cd83f` (lot 323). Aucune fusion avec integration.

**Invariant de la voie portée.** Une description typée de signes n'apporte
aucune phrase du MJ : dans le mode `dialogue` existant, `texte.signes_de`
sélectionne les références publiques des personnages visés. Le moteur rend
leurs signes actuels et leurs impressions, toujours présentées comme faillibles.
`signes.textes` est commun à cette réponse et à `rendu.regarder` ; aucun nouveau
jet, geste, sentiment certain ou intention privée n'est produit. Une cible hors
de vue sans signe perceptible passe par le constat et le souvenir bornés de G5.
Les références privées, inconnues et les sélections mal formées sont refusées
avec un `attendu`, puis corrigées par le protocole commun.

**Écriture.** `narration.consigner` recalcule la sélection sur le monde courant,
avant la mémorisation de la conversation, la sauvegarde et l'affichage dans
`jeu.py`. Une préparation ancienne ne fige donc pas un signe disparu. La réponse
ainsi produite ne passe par aucun audit narratif ni extraction d'attitude.
La prose libre garde tous ses contrôles actuels. Le code d'extraction du lot 176
n'est pas présent dans cette base non fusionnée : aucun contrôle existant n'a
été retiré de la prose libre. Son banc `attitudes` et sa préparation sont repris ;
l'étape de repos utilise le constructeur commun actuel `_etape`.

**Vérification sans réseau : 119 tests, neuf fichiers, tous verts**, zéro échec,
erreur ou saut, 24,457 s cumulées, deux travailleurs à priorité réduite. Les huit
nouveaux tests couvrent Ilse et Gorm du banc 176, un autre PNJ (Brune), plusieurs
personnages, les impressions incertaines, la perte de signe et d'impression entre
préparation et écriture, la perte de vue, les identités inconnues et la correction
de sélection. Monde, esprits, lectures, horloge et paroles restent inchangés par
une description seule. Texte, scène, carte et état complet contrôlés après
recharge ; présence du texte sur disque vérifiée au moment de son affichage.
Les fichiers concernés de narration, schémas, G5, relances et bancs sont verts.
Ni suite complète ni banc PNJ.

**Luna : une passe achevée**, `gpt-6-luna`, commit `a0c583c`, 101,716 s,
code 0, 14 tours (11 avec MJ), 33 appels, 14 audits narratifs, un repli ; zéro
erreur technique/recharge et zéro mention signalée sans fondement par le banc.
Le succès technique `fin-luna.json ok=true` **ne valide pas l'invariant**.

| Script | Appels référence c9459ce / branche | Audits | Sélections typées | Replis |
| --- | ---: | ---: | ---: | ---: |
| signes-ecart | 8 / 6 | 3 | 0 | 0 |
| signes-guet | 6 / 4 | 2 | 0 | 0 |
| attitudes | indisponible / 23 | 9 | 0 | 1 |

La branche typée était présente dans les 16 requêtes d'interprétation :
**Luna ne l'a jamais choisie**. Les descriptions restent reformulées et auditées.
Zéro extraction `attitudes` est observé, mais ce champ était déjà absent de la
base : ce zéro ne prouve aucun transfert vers le moteur. Les huit états observés
des deux scripts de signes sont identiques à leur référence archivée (passe 1,
lue sans relance). Leur baisse d'appels n'est pas attribuable à la voie typée.
Aucune comparaison de temps entre charges ni gain général revendiqué.

**Contre-épreuves réelles.** Après la proposition de partage, la prose publiée
prête à Gorm un regard vers Corvus et une « expression bourrue », sans signe actuel
correspondant. Au tour suivant, « Aubin hausse brièvement les épaules » est
publié, sans signe ni résultat moteur qui établisse ce geste. L'audit admet ces
segments comme paroles et ne contrôle pas ces ajouts. La question « Comment
réagissent-ils à ma proposition ? » est en outre prononcée par Corvus à Aubin.
Le repli concerne la description physique de Gorm après un enrichissement refusé.
Sans référence `attitudes`, aucune régression nouvelle n'est attribuée au lot.

**Limites et intégration.** La fidélité de la sélection à toute saisie libre
reste le travail du MJ ; cette garantie porte sur le rendu typé testé avec MJ
simulé, pas sur toute prose française. L'adoption réelle du contrat de description
et les gestes accolés aux répliques restent à porter par le mécanisme commun ;
pas de consigne d'exemple ni de seconde passe ajoutée. Aucun audit existant retiré.
Recouvrements constatés avec `origin/codex-g6-reperes` (328/G6) :
`donjon/rendu.py`, `donjon/narration.py` et `docs/etat-dev.md` ; conserver les
deux rendus et l'ordre écriture → mémorisation → sauvegarde → affichage.
Bruts : `C:/Users/msics/donjon/artifacts/g20-329/`, notamment
`tests-cibles.json`, `references.json`, `analyse-luna.json`, `luna-branche/`,
`fin-luna.json` et `fin-cloture.json`. Code/tests inchangés depuis vérification,
empreintes contrôlées ; aucune relance de test ou de Luna à la clôture. Aucun
calcul actif. Livraison sur origin, sans fusion.
