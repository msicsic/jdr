# Lot 74 — Gardes du récit : ne refuser que la contradiction établie

25 octobre 2026 — `codex-gardes-justes`, **non fusionnée dans main**, base intégrée
**fe85a44**. Lot 73 **29c9ae4** intégré à la demande de l’utilisateur par fusion signée
**c84dcf9** ; conflit dans `consigner`, deux validations conservées. `main` inchangée.

**Contrat.** `narration.voix_auteur` ne censure plus « refus » : ce nom commun, comme
« proposition », peut raconter une décision. Le vocabulaire technique existant garde
« le moteur refuse… ». L’interdiction générale du mot est retirée de la règle existante,
sans consigne ajoutée. `orientations` ne transporte plus une cible entre propositions
ou segments ; `sujet_locatif` borne la liaison à une attribution directe. Direction admise
acceptée ; cible, repère ou polarité indécidables laissés à l’audit sémantique. Le calcul
des positions publiques ne change pas ; aucune position cachée supplémentaire n’est lue.

Le refus du brasero venait de l’auditeur sémantique. `mj._echanger` distingue maintenant
`effet_percu` et `source_visible`. Le schéma commun extrait les `eclairages` affirmés ;
le moteur compare ces références aux contributions positives, même hors de vue de la
source, puis refait ce contrôle avant l’enregistrement. Un refus et son `attendu` par
source sans contribution ; anciens rapports sans extraction lisibles.

**Tests.** Sept nouveaux tests console/MJ simulé/sauvegarde/recharge : refus réel de Brune,
dette et or conservés ; autre refus ordinaire ; crochets et poutre ; négations distinctes,
pronoms ambigus ; brasero de crypte et lanterne posée du Relais hors de vue ; extinction
avant enregistrement. État et nouvelle lecture affichée après recharge contrôlés.
**66 tests ciblés verts**, seconde source revalidée ; **20 tests des deux lots verts après
fusion**. Première suite interrompue sans bilan pour attendre le lot 73. Suite finale :
**1 875 tests, 16 ignorés, 188 fichiers, 1 809,8 s**, trois processus à priorité réduite.
Une `PermissionError` sur le verrou temporaire de `test_connexion`, fichiers inchangés ;
reprise du fichier : **21 tests verts**, 1,7 s. Incident non reproduit, non corrigé ici ;
aucune seconde suite complète. Attente et validation réunie prolongent le créneau initial.

**Luna : une passe avant intégration du lot 73**, ChatGPT `gpt-6-luna`, medium/libre,
copies temporaires, référence **fbcf0ff** exclusivement lue du cache (première passe).

| Script | Appels/tour MJ, référence → lot | Relances/tour, référence → lot |
|---|---:|---:|
| crypte | 2,33 → 2,67 | 0 → 0,11 |
| comptes | 3,00 → 4,00 | 0 → 0,50 |
| relais | 2,50 → 2,75 | 0 → 0,25 |
| luna-restes-ambiance | 2,67 → 2,00 | 0,33 → 0 |

**55 → 60 appels / 22 tours MJ**, **1 → 4 relances** ; aucun arrêt, erreur technique,
erreur de recharge ou repli historique. Brasero admis ; aucun refus spatial déterministe
des crochets ; refus de Brune rendu en trois appels. Resserrements finaux validés ensuite
par tests, sans seconde passe Luna. Aucune conclusion de performance depuis ce cache.

**Limites.** Extraction lumineuse, antécédents complexes, portée des négations et verdicts
restent sémantiques : omission ou faux refus demeurent possibles. La crypte conserve un
faux audit d’approche/attente ; les comptes de cette passe, un refus de non-livraison
(antérieur au lot 73). « Le geste envisagé dépasse… » ne prouve pas lexicalement une voix
de procédure : méta-langage général non clos. Ni garantie absolue, ni exception de phrase.

Bruts du worktree : `artifacts/bancs-multi/20261025-125431-38764/`, `mesures-codex-74.json`,
`relecture-codex-74.txt`, `reprise-fusion-73-74.json`, `tests-codex-74-final.json` et
`reprise-connexion-74.json` dans `artifacts/`.
