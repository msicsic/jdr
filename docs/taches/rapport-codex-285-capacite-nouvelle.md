# Lot 285 — C1 mesurée sans gain, diagnostic clos

Base d'intégration `51d66e6`, branche locale effective `codex-capacite-nouvelle-1`
(le worktree fourni portait ce nom ; cible de livraison demandée :
`codex-capacite-nouvelle`). **Aucun fichier de code, test ou scénario modifié.**
Le gain préalable est de **0 %**, inférieur au seuil de 5 % du brief : arrêt avant
implémentation. La généralisation de `Vue.capacite` et `Vue.doublon` n'est pas livrée.

**Méthode.** Les captures historiques `tests/data/cout-12h/mine-1985-480.json.gz`
et `auberge-1985-480.json.gz` sont rechargées sur le moteur de la base. Pour chaque
PNJ doté d'un profil, trois recherches neuves sont appelées directement :
`a_mange` avec l'emploi `manger`, `rechauffe` avec `feu`, `eclaire` sans emploi
supplémentaire ; séjour compté pour les deux dernières. Mine : Bram, Gaspard,
Josse, Lucien, Mathe, Odon, Rémy ; auberge : Anselme, Hugues, Joss, Lucien,
Mathurine, Mireille, Odile, Tilo. Ce sont 45 recherches, chacune jouée avec la
règle actuelle puis avec un prototype temporaire, caches de résultats, graphes
et impossibilités vidés entre les appels, sans faire vivre la nuit.

La sonde sur `_suites` compte les états développés portant deux objets de même
catégorie, puis les dominations exactes. Le prototype ne change que `doublon`
en mémoire : lumière conservée ; clés comparées par serrures ouvertes ; outils
de crochetage équivalents, le seuil ne lisant aucune qualité de l'outil ; force
comparée par aptitude et coût des coups sur chaque porte/contenant connu, via
`force.adapte`, `coups`, `chance`. Un moyen porté contrarié ou sans permission
ne domine pas une candidate supposée reçue avec permission. Qualités d'arme de
saisie distinctes, usages supplémentaires et passages métriques sont conservés.
Les contenants restent hors prototype : les gestes lisent l'identité et l'accès
au contenu, sans besoin exact de capacité de transport établi. Consommables,
vivres et parts exclus, conformément au brief.

| Capture | Recherches par version | États observés | États avec deux objets de même catégorie hors lumière | Nœuds base → prototype |
|---|---:|---:|---:|---:|
| Mine, 1985, minute 480 | 21 | 2 868 | 0 | 3 185 → 3 185 |
| Auberge, 1985, minute 480 | 24 | 2 083 | 0 | 2 034 → 2 034 |

Choc, coupe, crochetage et clés : **0 % chacune**, avant même de comparer la
qualité des objets. Les 45 résultats complets (coût, étapes, état terminal)
sont identiques. Après chacun des 90 appels, monde, rendu et scène perçue sont
identiques à ceux d'avant la recherche après sauvegarde/rechargement. Aucun
plan exécuté dans le monde. Le diagnostic détaché, un travailleur réduit,
dure 12,809 s ; `fin-diagnostic.json` porte `ok=true`. L'échec d'import initial
est archivé ; démarrage corrigé et écriture d'un marqueur `ok=false` avec erreur
testés séparément.

**Portée et limites.** Les états observés sont les appels à `_suites`, pas tous
les nœuds examinés ni des états uniques ; les diagnostics de recherche donnent
séparément les nœuds du tableau. Les captures sont historiques : cette mesure
ne couvre ni une nuit actuelle de 12 h, ni d'autres graines/instants/scénarios,
ni l'arbitrage réel des besoins, les pulsions, devis ou engagements. Elle ne
prouve pas la sûreté générale du prototype, et l'invariant C1 reste non garanti.
Onze recherches épuisent leur espace (neuf mine, deux auberge), aucune ne
plafonne ; le maximum diagnostiqué est de 576 nœuds. Cela ne suffit pas à
attribuer le coût actuel de fin de nuit : aucun profil de nuit entière n'a été
fait ici. Les préparatifs ne sont pas synonymes de doublons. C1 est retirée des
pistes actives ; aucune accélération démontrée, aucun nouveau banc, test moteur,
suite complète, `VERIFIER` ou appel Luna lancé pour cette clôture documentaire.

Bruts : `C:/Users/msics/donjon/artifacts/capacite-285/` (`diagnostic.py`,
`mesures.json`, `bilan.json`, journaux et `fin-diagnostic.json`).
