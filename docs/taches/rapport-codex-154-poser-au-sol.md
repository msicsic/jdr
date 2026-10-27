# Lot 154 — poser au sol (L8)

Branche `codex-poser-au-sol`, non fusionnée, base `0352f29`, moteur `8697169`,
présentation corrigée `040a9a1`. `main` intact ; aucune clé Git de signature,
commits non signés, branche poussée seule.

**Contrat commun.** `operations.compiler` résout `destination: "sol"` vers la
salle de l'étape : `deplacer`, `prelever`, séquences et effets d'improvisation.
Ancienne salle courante compatible ; autre salle refusée avec `attendu`.
`deplacement_objet.deplacer` conserve lieu réel et position ; le prélèvement
direct dépose aussi la pièce aux pieds de Corvus. Les consignes disent `sol`.

**Correction de la contre-revue.** Le premier passage exposait l'effet interne
vers `cour`, provoquant un faux refus du dépôt du couteau. C'était une lacune
de représentation du contrat commun, corrigée dans ce lot. `decrire_depot` et
`presenter_effet` fournissent le libellé « au sol, à tes pieds » et la destination
publique `{destination: "sol", position: "à tes pieds"}`. Titre et information
du plan, branches d'improvisation et dossier récursif de `couverture_action`
l'utilisent. La salle interne n'est plus présentée comme lieu du dépôt,
y compris quand une séquence change de salle. **Aucun effet exécutable modifié**,
aucune consigne d'audit ni exception d'objet ajoutée ; fournisseurs et PNJ intacts.

**Vérifications.** Sept tests propres au lot : console/MJ simulé, torche et
planche, prélèvement direct, séquence, improvisation, compatibilité et refus ;
état, scène et carte après recharge. Le nouveau test inspecte le dossier pour
chaque voie, réussite/échec compris, et vérifie sa lecture sans mutation du
monde ni du plan. **55 tests ciblés verts, quatre fichiers, 1,485 s**.
La reprise ne change que titre/information/dossier : pas de nouvelle suite
complète, conformément à la relecture. La suite initiale unique reste :
**2 174 tests, 245 fichiers, 1 285,395 s**, deux échecs MiMo historiques `6 != 5`
(`test_restes_fusions`, `test_fournisseurs_jeu`), zéro erreur/ignoré, deux
processus réduits. Banc initial Relais quatre graines × 4 h : états complets,
relevés, chroniques, récits, souvenirs et mesures **4/4 identiques** à `main`
`812ebe5` ; aucun plantage, trois `fige_presse` identiques par côté. Quatre
références absentes cachées une fois ; atelier absent de ce banc PNJ.

**Luna après correction : une passe demandée**, ChatGPT `gpt-6-luna`, medium,
réflexion libre, une exécution réduite, sauvegardes temporaires uniquement.

| Script | Appels/tours MJ | Appels/tour | Secondes/tour | Refus de destination |
|---|---:|---:|---:|---:|
| poser-sol-atelier | 4/1 | 4,00 | 9,6 | 0 |
| poser-sol-relais | 4/1 | 4,00 | 11,4 | 0 |
| atelier | 32/11 | 2,91 | 8,8 | 0 |

**40 appels/13 tours MJ**, couteau et torche réellement déposés ; dossiers
Luna archivés avec destination publique `sol`. Zéro repli, incident technique,
erreur de recharge ou mention sans fondement détectée. Atelier conserve deux
tours avec refus de matériau/portée, sans rapport avec le dépôt. Référence
`cdaf371` relue sans rejeu : atelier 39/11 (3,55 appels/tour, 10,9 s/tour).
Charges différentes : aucun gain de temps établi ni garantie sémantique absolue.

Première passe conservée : quatre scripts, 72 appels/21 tours MJ, faux refus
atelier et deux destinations de surface. Après correction, les deux dépôts
réussissent sans refus ; la confusion possible `cour_sol`/`antichambre_sol`
est signalée pour **L7**, sans traitement ici. Référence initiale intacte
(SHA-256 dans `mesures-luna.json`). Bruts : `artifacts/poser-sol-154/`,
complément `revue-luna/`, `revue-cibles.json` et `dossiers-revue.txt`.
