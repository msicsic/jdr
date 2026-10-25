# Lot 73 — Comptes de l'issue

25 octobre 2026 — Branche `codex-comptes-issue`, **non fusionnée**. Brief `6a18952`,
mise à jour initiale avec `origin/integration` (`fe85a44`), correctif signé **e219008**.

**Invariant et fonctions.** Un paiement ou une remise opéré par le moteur doit être
fourni avec ses rôles et sa quantité, puis restitué dans le récit accepté.
`biens.payer`, `echanges.remettre` et les remises de `echanges.proposer` alimentent
un journal dans la copie de travail de `paroles.preparer_parole`. Les essais abandonnés
ne publient rien ; le journal est retiré avant sauvegarde. Les remboursements ne sont
plus recalculés séparément par différence de soldes. Les nouveaux biens à livrer
viennent des engagements (`biens.livraisons_dues`), également lus dans les comptes
publics et leur panneau après recharge. Aucun compte privé entre PNJ.

`narration.controler` compare les comptes extraits à l'issue et à l'état courant,
puis exige la restitution de chaque compte rendu ou dû de l'issue, même dans une
réplique à portée aucune. Les inversions restent refusées ; l'absence explicitement
traitée garde le sens de la demande. `consigner` refait le garde avant enregistrement,
avec l'attendu du premier obstacle. Le schéma d'extraction distingue transfert opéré,
promesse et absence de créance ; raconter l'issue ne crée aucun transfert par la parole.

**Tests et mesures.** Trois tests nouveaux, cinq parcours : remboursement d'Aubin au
soir et de Gorm, omission puis inversion refusées ; achat différé d'une planche et
d'une part des fagots de Joss ; omission avant enregistrement. Le marché atomique
reprend la question préalable sur le bois du cas réel. Vraie console/MJ simulé,
argent, dettes, engagements, paroles, conversation et panneau après recharge.
**19 tests ciblés distincts verts**, dont les reprises.

Suite complète **une fois** : **1 868 tests, 16 ignorés, 187 fichiers, 2 152,2 s**,
trois processus à priorité réduite. Résultat initial : **un échec et trois erreurs**
dans deux méthodes de `test_audience` et `test_luna_restes` : leurs récits simulés
omettaient des transferts. Récits et audits complétés, assertions financières conservées,
quatre parcours repris verts. La simulation de l'échange immédiat de `prime-offre`
raconte aussi la part remise. **Bilan consolidé sans défaut restant connu**, sans
seconde suite complète.

Luna/ChatGPT, medium/libre, **une passe** soir-appel/ressources/comptes ; référence
`fbcf0ff` exclusivement relue du cache. **36 → 30 appels**, neuf tours MJ,
**4,00 → 3,33 appels/tour**, **trois → zéro relance**, **un → zéro repli** ; aucune
erreur technique/recharge. Par script : **19 → 15**, **11 → 9**, **6 → 6 appels**.
Le remboursement d'Aubin est raconté en quatre appels ; Gorm rembourse, Brune garde
les pièces. Aucune conclusion de vitesse entre charges différentes.

**Limites.** L'achat du soir n'est pas exécuté en ligne : la contre-revue de fidélité
oppose à tort la planche singulière au lot `planches`, puis demande une précision.
La baisse d'appels ne prouve donc pas l'acceptation en ligne du marché payé, validé
ici avec MJ simulé. Extraction et portée restent sémantiques : comparaison et
couverture sont déterministes sur le rapport reçu, sans garantie de toute paraphrase
ni exemption des autres contradictions. Ni `main`, ni `planification.py`/`obstacles.py`,
ni modèle ou prompt du MJ modifiés.

Bruts du worktree : `artifacts/validation-lot73.json`, `tests-lot73.json`, `suite.log`,
`comptes-issue-final2.log`, `reprise-audience.log`, `reprise-luna-restes.log`,
`mesures-lot73.json`, `relecture-lot73.txt` et
`bancs-multi/20261025-125209-36896/`.
