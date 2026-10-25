# Lot 83 — Cohérence typée de l'audit et références des comptes

25 octobre 2026 — Branche `codex-verdict-coherent`, **non fusionnée**. Brief
`13ae231`, intégration du lot 82 `7cce974` reprise par fusion signée `b1dbf65` ;
correctifs signés `b2be935`, `be8e175`. **Validation partielle : N4 corrigé ;
N2/N3, signalés dans le seul motif libre, restent hors de la garantie.** Aucun
changement de `main`, de Luna `gpt-6-luna`, des prompts, scénarios ou du planificateur.

**Invariant et fonctions.** `narration.controler` rend illisible un verdict
`mecanique` avec une portée `sans_fondement`/`contradictoire`, ou un verdict
`invention_protegee`/`contradictoire` avec une portée `etablie`. La boucle commune
redemande une fois l'audit du même texte ; deux rapports illisibles ne valident
jamais ce texte. `consigner` refait le contrôle avant écriture.

`noms.references_fournies` résout les références des comptes avant comparaison
par `monde.reference_exacte` : identifiants, noms publics, formes avant virgule
et alias. Son catalogue réunit sans écrasement les objets, interlocuteurs,
personnes connues, souvenirs visuels fournis et le nom du joueur, y compris
hors de vue. Les termes imbriqués suivent la même résolution ; montants, états
et prose restent intacts. Une ambiguïté rend l'audit illisible, aucune identité
privée n'est devinée. Le dossier archivé permet le même contrôle à l'enregistrement.

**Tests.** Sept tests nouveaux : console puis recharge, absence et orientation,
audit redemandé puis texte corrigé, rapports cohérents inchangés, audits restant
illisibles jusqu'au repli, garde à l'enregistrement ; remboursements Gorm/Corvus
et Aubin/Corvus, comptes hors de vue, or, dettes et rendu rechargés ; objets,
offres imbriquées, ambiguïté, nom variable du joueur et sources cumulées.

Suite complète unique : **1 914 tests, 16 ignorés, une erreur**, 195 fichiers,
trois processus à priorité réduite, **1 755,2 s**. Ancien test
`test_scenarios_libres.test_empreinte_crypte_visible_apres_rechargement` :
`StopIteration` des saisies simulées en mode hors ligne, où ce nouvel audit
n'intervient pas. **Reprise finale : 63 tests verts sur six fichiers, 82,75 s**,
dont ce fichier inchangé et les sept tests finaux du lot. Incident non reproduit,
cause non établie, aucune correction de contournement. La suite avait exécuté
six tests du lot avant l'ajout du septième ; bilan consolidé **1 915 tests,
16 ignorés, aucun défaut restant reproduit**, sans seconde suite complète.
Premiers lancements ciblés bloqués par les permissions des temporaires Windows,
puis deux erreurs de chargement de scène corrigées avant la suite.

**Luna, une passe.** ChatGPT medium/libre, copies temporaires, priorité réduite.
Trois références `882907c` exclusivement lues du cache, contenu vérifié par
SHA-256 : signes-noir **2 → 2 appels**, crypte **21 → 28**, comptes **8 → 8** ;
**31 → 38 appels / 12 tours MJ**, **2,58 → 3,17 appels/tour**, **14,6 → 16,1 s/tour**.
Une relance narrative dans chaque variante, refus **1 → 3** ; aucun arrêt,
erreur technique/recharge ni repli détecté. Temps historiques sous une autre
charge : aucune conclusion de performance.

Textes affichés : Ilse non vue sans absence affirmée ; Gorm au sud-ouest sans
« face à toi » ; « Gorm te rend les deux pièces, sans détour », sans relance,
or **24 → 26**, dette soldée au tour rechargé suivant ; Brune conserve sa dette.
L'extraction nouvelle utilise déjà les identifiants : N4 est également prouvé
par le rejeu exact de son ancien audit nominatif et les chaînes simulées.
Demande de prime en crypte non exécutée après des refus de fidélité, hors lot.

**Limites et bruts.** Les rapports historiques N2/N3 restent admis au rejeu :
verdict et portée positifs, contradiction dans le seul motif libre. Aucune
liste de mots ni revue supplémentaire ; leur non-reproduction dans cette passe
ne les clôt pas. Vérité et extraction restent sémantiques. Compléments finaux
(alias sans premier mot inventé, références hors de vue cumulées) vérifiés par
tests, sans seconde passe Luna. Le harnais capture les marqueurs des panneaux ;
les tests console vérifient leur rendu. Bruts du worktree : `artifacts/lot83/`
et `artifacts/bancs-multi/20261025-181806-44712/`.
