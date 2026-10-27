# Lot 154 — poser au sol (L8)

Branche `codex-poser-au-sol`, non fusionnée, base `0352f29`, code `8697169`.
`main` intact. Pas de clé Git de signature configurée : commits non signés.

**Invariant moteur.** `operations.compiler` résout `destination: "sol"` vers la
salle de Corvus avant validation : `deplacer`, `prelever`, séquences et effets
d'improvisation partagent ce chemin. `deplacement_objet.deplacer` enregistre le
lieu réel et la position. Ancienne salle courante compatible ; autre salle
refusée avec `attendu`. Le prélèvement direct dépose aussi la pièce aux pieds
de Corvus, au lieu de conserver la position du tas. Deux lignes des consignes
désignent `sol`. Aucun assemblage de requêtes, fournisseur ou PNJ changé.

**Preuves déterministes.** Cinq nouveaux tests console/MJ simulé : torche,
planche prélevée puis posée, prélèvement direct, séquence, improvisation,
compatibilité et refus sans mutation. Après recharge : lieu, position, visibilité,
scène, légende et coordonnées de carte. Audit simulé conforme : son jugement
sémantique réel n'est pas prouvé. Reprise finale : **5/5 verts**. Suite complète
unique, deux processus réduits : **2 174 tests, 245 fichiers, 1 285,395 s**, deux
échecs MiMo historiques `6 != 5` (`test_restes_fusions` et
`test_fournisseurs_jeu`), zéro erreur/ignoré ; pas de référence rejouée pour ces
échecs déjà documentés. Banc rapide Relais, quatre graines × 4 h : états complets,
relevés, chroniques, récits, souvenirs et mesures **4/4 identiques** à `main`
`812ebe5`. Aucun plantage ; trois constats `fige_presse` identiques par côté.
Quatre références absentes rangées une fois, puis quatre nuits de branche,
un processus réduit ; temps non comparés. Atelier absent du banc PNJ, couvert
en console et par Luna.

**Luna, une passe**, quatre scripts, `gpt-6-luna`, ChatGPT, effort medium,
réflexion libre, sauvegardes temporaires seulement, une exécution réduite à la fois.
Référence `cdaf371` relue sans rejeu (SHA-256 dans `mesures-luna.json`).

| Scripts | Appels/tours MJ référence → lot | Appels/tour référence → lot |
|---|---:|---:|
| atelier | 39/11 → 39/11 | 3,55 → 3,55 |
| relais | 25/8 → 23/8 | 3,12 → 2,88 |
| poser-sol-atelier | — → 5/1 | — → 5,00 |
| poser-sol-relais | — → 5/1 | — → 5,00 |

Total lot : **72 appels / 21 tours MJ** ; aucun repli, incident technique du jeu
ou erreur de recharge. Secondes/tour : atelier 10,9 → 10,2 ; Relais 9,9 → 9,5 ;
épreuves ciblées 13,5 et 14,5. Charges différentes : aucun gain de temps établi.
Export HTML initial arrêté après écriture du JSON, import du lanceur corrigé,
HTML régénéré hors ligne : aucun script rejoué. Mentions sans fondement détectées
au Relais : 1 → 2 ; ce compteur n'est pas un audit exhaustif.

**Critère Luna sans refus de destination non atteint.** Atelier propose d'abord
`sol`, accepté par le moteur ; la contre-revue confond son effet interne vers
`cour` avec un dépôt ailleurs qu'au sol et le rejette. La correction `cour_sol`
est refusée par le moteur, puis Luna abandonne : couteau toujours porté.
Relais propose `antichambre_sol`, refusé, puis corrige vers `sol` et dépose
effectivement la torche. Pas de seconde passe ni d'exception de scénario ou de
consigne d'audit ajoutée. Le contrat typé du moteur est établi ; le parcours
Luna sans faux refus n'est pas garanti, la contradiction sémantique reste ouverte.

Bruts : `artifacts/poser-sol-154/` dans ce worktree ; quatre JSON Luna,
quatre HTML (premier régénéré hors ligne), analyse, mesures et résultats de tests.
Les sources en cache restent intactes. Branche poussée seule, sans fusion.
