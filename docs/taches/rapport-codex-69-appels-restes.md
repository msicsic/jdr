# Lot 69 — Indices consommés dans la recherche d'une personne

Branche `codex-appels-restes`, non fusionnée, base `be90377` ; intégration déjà à
`4acc36c` au départ. Code signé `514de86`, puis `1d763cc`.

**Causes.** Mine 7 : sept premiers lieux, puis rappels après bruits du baraquement et
voix de Lucien (bureau, galerie, puits). `croire` rouvrait à chaque actualisation,
sans comparer le contenu. Auberge 7 : huit premiers lieux puis deux rappels après un
appel non compris au dortoir et des pas désormais situés dans le couloir, à 633–634.
Ces indices sont nouveaux : toute rafale n'est pas un défaut. Changer de but ne
réinitialisait pas la recherche ; la lacune commune concernait les indices réentendus
après explication ou éviction de leur souvenir.

**Contrat.** `deliberation.indice_recherche` garde le contenu perçu par personne et
lieu (`indices_recherche`) : présence, assurance, position, force du bruit, voix
reconnue. Ni répétition, ni date, confiance ou relais ne réarment une recherche.
`pnj._inspecter` consomme le point de départ avant le tour d'horizon ;
`recherche_vaine` consomme les indices de l'échec. `presence_recherche` conserve la
dernière localisation positive malgré l'absence : un retour appris reste nouveau,
sans oublier les anciens sons. Vue nouvelle et réponse adressée saisie rouvrent
localement (`contact_recherche`, `appel.entendre`). Aucun auteur caché de bruit retenu.

**Preuves.** Captures de `5c2ce81`, mine 7 à 470 et auberge 7 à 625 : dix minutes
d'un bloc ou en tranches de quatre et six ; monde complet, description et ouïe
identiques après recharge ; appels bornés par lieux et indices nouveaux. Sept tests
finaux verts, dont Gorm et le joueur, éviction, réponse, absence, bruit répété et retour.
Les 28 tests existants repris sont verts. Suite complète unique : **1 855 tests,
16 ignorés**, verte, 2 280,9 s ; deux cas ajoutés ensuite : **bilan consolidé
1 857 tests, 16 ignorés**, sans seconde suite complète.

**Rapide final.** `1d763cc` contre `4acc36c`, quatre scénarios × quatre graines × 4 h :
chroniques et mesures de jeu identiques ; zéro plantage, violation ou usurpation.
Seize références calculées une fois puis relues du cache. Ces lots successifs ne
constituent pas un comparatif CPU.

**Audit final : 12 h, branche seule.** Pic par même appelant/cible sur quinze minutes ;
passages maximaux par PNJ et heure.

| Nuit | Appels | Pic / 15 min | Passages / h max |
|---|---:|---:|---:|
| Mine 7 | 9 | 3 | 14 |
| Mine 1985 | 2 | 1 | 16 |
| Auberge 7 | 7 | 1 | 20 |
| Auberge 2024 | 14 | 4 | 38 |

Aucun plantage, usurpation ou rafale ≥ 5. L'audit ancien comptait 19/20/27/23 appels ;
les autres lots intégrés empêchent d'attribuer toute la différence au lot 69.

**Limites.** Des premiers lieux et indices nouveaux peuvent légitimement former une
rafale. Des sons identiques après changement non observé restent un seul indice ;
les indices anciennement évincés ne migrent pas. Faim, noir et vols restent observés.
La croûte de Lucien suit la consommation illicite (`manger`, `sans_temoin`, coût
d'honnêteté), distincte d'une demande refusée : cela seul ne prouve pas l'oubli du
refus du lot 57 ; aucun correctif hors lot.

Ni Luna, ni `main`, ni planificateur, signes ou scénarios modifiés. Budget de 45 min
dépassé : compléments du contrat et reprises ciblées, suite unique de 38 min. Calculs
finaux à priorité réduite, trois simultanés au plus. Bruts : `artifacts/codex-69/` ;
règle détaillée : `docs/plan-ouie.md`.
