# Lot 117 c — Comptes du récit remesurés

27 octobre 2026 — `codex-comptes-recit-c`, **non fusionnée**, base `562b2b1`,
port du 117 b (`94a0782`) par `aa43c13`. Seul conflit documentaire, historique
actuel conservé ; contrats 113/116/142/143 gardés, aucun autre correctif.
**Invariant :** le moteur fournit les comptes ; l'auditeur choisit référence,
sens fermé et quantité, comparés par `narration.controler` ; `mj._appeler`
fournit le catalogue commun. Reconnaissance et jugement des termes sémantiques.

**Protocole :** deux passes des quatre scripts 117 b (comptes, soir-appel,
ressources, crypte) et des quatre références (relais, crypte, atelier, echanges),
sept scripts distincts. Luna `gpt-6-luna`, ChatGPT medium/libre, budget 200,
deux exécutions réduites au plus, copies temporaires. Les 14 parties `cdaf371`
sont exclusivement lues du cache, clés scripts/options et SHA-256 vérifiés ;
empreinte historique du harnais conservée. Charges différentes : causalité de
latence isolée non prouvée.

**Référence → branche**, tours MJ seulement ; refus = moteur/contre-revue,
obstacles = causes narratives, plusieurs par segment possibles.

| Deux passes cumulées | Quatre scripts 117 b, 36 tours | Ensemble, 80 tours |
|---|---:|---:|
| Appels ; moyenne / médiane par tour | 126 → 140 ; 3,50 / 4 → 3,89 / 4 | 270 → 287 ; 3,38 / 3 → 3,59 / 4 |
| Secondes par tour, moyenne / médiane | 11,95 / 11,66 → 17,39 / 14,64 | 11,23 / 10,68 → 14,78 / 13,43 |
| Relances / refus / replis | 5 / 6 / 0 → 13 / 3 / 3 | 14 / 22 / 0 → 21 / 24 / 3 |
| Obstacles narratifs | 7 → 54 | 19 → 68 |
| Jetons cachés | 522 240 → 648 832 | 1 383 040 → 1 402 240 |

Passes de l'ensemble séparées : appels/tour **3,33 / 3,43 → 3,78 / 3,40**,
secondes/tour **10,90 / 11,57 → 16,22 / 13,34**, obstacles **8 / 11 → 39 / 29**.
Sur les quatre scripts historiques : **11,88 / 12,01 → 18,11 / 16,67 s/tour**.

| Fonction, ensemble : appels cumulés ; s/tour moyenne / médiane | Référence | Branche |
|---|---:|---:|
| Interprétation | 92 ; 4,57 / 4,08 | 95 ; 4,72 / 4,14 |
| Audit narratif | 82 ; 3,52 / 3,16 | 87 ; 6,39 / 5,08 |
| Récit | 45 ; 1,49 / 1,96 | 45 ; 1,51 / 1,85 |
| Révision | 14 ; 0,56 / 0 | 21 ; 0,91 / 0 |
| Fidélité | 19 ; 0,69 / 0 | 21 ; 0,77 / 0 |
| Contre-revue | 18 ; 0,41 / 0 | 18 ; 0,47 / 0 |

Appels par fonction/tour, moyennes et médianes : `mesures.json/par_fonction`.
L'audit représente
**2,87 s** des **3,55 s** supplémentaires par tour. Sur les quatre scripts,
il passe de **3,64 à 8,71 s/tour**. Sa sortie double : **127 → 258 jetons/appel**
(10 408 → 22 427 jetons, 82 → 87 appels), cache d'audit **529 536 → 431 104**.
L'écart historique **14,0 → 20,5 s/tour**
se confirme dans son sens et sa hausse relative (**+46 %** ici) ; les obstacles
augmentent aussi, mais **3,5 → 27 par passe**, contre **11 → 60** au lot 117 b.

**Justesse :** aucune inversion explicite affichée relevée, référence comprise,
donc aucun gain naturel mesurable. Achat p2 ambigu (« tiens, les pièces sont
remises », pluriel des planches). Qualification humaine : **12 tentatives avec
faux refus comptable sur sept tours**, contre zéro relevée en référence : Brune,
remboursement/achat d'Aubin, offre de Gorm, propos sans compte liés aux soldes
absents ; autres faux refus exclus. Gorm/Aubin remboursent 2/2, Brune ne paie
pas 2/2 ; achat payé/livré 2/2 (référence : abandonné p1, abouti p2).

**Rejeu exact :** sources `91a4351` identifiées par SHA-256 (ordre de rangement
distinct des numéros de passes historiques). Cinq essais chacun : offre,
ambiance, possession **0/5 refus** ; inversion **5/5**, seuil 95 atteint,
mais trois refus de sens et deux de quantité sur compte absent. Livraison
future **5/5**, dont trois refus du seul hochement de tête : contenu comptable
non certifié par ce résultat. Aucun audit illisible/incident sur les 25 appels.

**Validation : 55 ciblés verts**, console/état/rendu rechargés, Gorm/Aubin/Brune
et deux biens. Suite complète unique : **2 168 tests, 244 fichiers, 1 251,69 s**,
deux échecs MiMo `6 != 5`, zéro erreur/ignoré ; mêmes deux échecs reproduits sur
la copie exacte de `562b2b1` (13 tests, 5,80 s), aucune régression nouvelle détectée.
Aucun incident technique/recharge
des bancs ; projections seules archivées, pas de preuve exhaustive du monde
rechargé par Luna. Limite sémantique maintenue. Décision de fusion à l'utilisateur,
`main` intact. Bruts, qualification, manifestes, mesures :
`C:/Users/msics/donjon/artifacts/comptes-117c-3vhx9bfb/`, copie vérifiée par
SHA-256 ; originaux `artifacts/117c/` du worktree, cache avant/après identique.
Aucune clé Git de signature configurée ; commits non signés, branche poussée seule.
