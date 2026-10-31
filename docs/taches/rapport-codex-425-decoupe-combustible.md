# Lot 425 — découpe d'un combustible compté

31 octobre 2026 — `codex-decoupe-combustible`, base d'intégration `a874d646`.

**Cause reproduite sur la base.** Une planche du Relais qualifiée et prélevée
porte `charges=1`, `duree_combustion=90`, usage `combustible`. `artisanat.decouper`
transmettait l'usage et la durée au morceau, sans `charges` : `Monde.verifier`
rejetait l'état (« Combustible invalide »). Le diagnostic figure dans les bruts.

**Invariant et correction.** `matiere.partager_ressources` calcule sans mutation
les compteurs du morceau et du reste selon leurs masses. Les compteurs simples
(`charges` sans durée, `combustible` en minutes) se partagent ; une réserve à
durée par charge conserve **charges × durée**. Chaque fragment reste une portion
consommable : le nombre d'usages est hérité, la durée par usage se partage.
Ainsi une planche de 90 minutes coupée au tiers donne une charge de 30 minutes
et une de 60, sans créer de réserve. Les mêmes champs sont conservés. Les comptes
restent entiers : arrondi au plus proche, complément exact sur le reste ; une part
théorique inférieure à une unité est refusée avant arrondi, avec identifiant,
champ, reçu et accepté dans `attendu`. Une réserve épuisée est aussi refusée.

`artisanat.preparer_decoupe` vérifie ce contrat avant de proposer l'acte ;
`decouper` le vérifie encore avant toute écriture. Le morceau hérite aussi de la
substance et de l'état lumineux requis pour consommer sa part correctement.
La découpe se trouve dans `artisanat.py`, pas dans `operations.py` : aucun raccord
supplémentaire n'est nécessaire dans ce dernier ni dans `perception.alimenter`,
déjà commun au joueur et aux PNJ. Aucun scénario, prompt, audit ou registre d'esprit
modifié ; aucune nouvelle décision PNJ ajoutée.

**Vérification.** Sept fichiers ciblés, **56 tests verts**, au plus deux travailleurs
à priorité réduite (`tests-final.json`, agrégat des six voisins et du dernier
passage ciblé). `test_lots.py` n'existe pas sur cette base : couverture des lots
par `test_piece_de_lot`, `test_matiere` et `test_assemblage` ; les deux fichiers
`test_fabrication*` et `test_qualification` passent également. Vraie console avec
MJ simulé, confirmation, sauvegarde et recharge : prélèvement puis découpe de la
planche du Relais (30 + 60 minutes), bûche de l'auberge (11 + 34), alimentation du
foyer par le joueur puis par un PNJ, refus du réemploi d'une charge épuisée ;
torche (20 + 40 minutes), compte simple (3 + 6). Conservation des masses et des
réserves, dimensions, rendu des utilisations et minutes, refus des deux extrêmes
sans mutation ni création contrôlés après recharge.

**Empreintes.** Mesure Relais/auberge, 2 h × quatre graines, contre la base
d'intégration figée `a874d646` : **8/8 identiques**, chronique, mesures et état
final complet, aucun plantage. Référence jouée une fois puis mise en cache ;
aucun gain de temps revendiqué.

**Limites.** La répartition d'une quantité entière approche la proportion de masse
à une demi-unité près par compteur partagé ; le solde conserve exactement le total. Pour une réserve
à durée par charge, le nombre brut de portions peut augmenter à la découpe,
leur capacité cumulée ne change pas. Aucune suite complète ni appel à Luna,
conformément au brief.

**Bruts.** `C:/Users/msics/donjon/artifacts/decoupe-combustible-425/` : diagnostic
de base, tests (essais et bilan final), empreintes et commandes de reproduction.
`fin.json` enregistre la fin de la vérification et le commit poussé.
