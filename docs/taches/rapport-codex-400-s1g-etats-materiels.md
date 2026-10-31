# Lot 400 — S1g, vues des états matériels crus

31 octobre 2026 · `codex-s1g-etats-materiels` · base exacte `integration 8fa9e70e`.
Code à mesurer : **`a3072b47`**. **Vérification complémentaire en cours ; lot non clos.**

**Invariant et code.** Les preuves matérielles (`etat`, `fin`, `verrouillee`,
`lumiere`, `pieces`) passent par les vues pures de `memoire`. La façade
`esprits.croyance` renvoie désormais une copie profonde pour ces familles ;
ses filtres historiques restent appliqués. `etat_connu` conserve les propriétés
partielles : une propriété omise reste inconnue, une valeur `False` reste négative.
`fin_connue` distingue l'absence de preuve (`None`) d'une preuve datée de fin
négative (`valeur=None`). Aucune lecture ne complète la preuve depuis le réel.
L'admission reste la porte commune `admettre_fait`, via `croire` ; aucune nouvelle
écriture ni aucun registre. Clés, ordre et sérialisation historiques conservés.

Lecteurs portés : perception du joueur et constat de fin, estimation de force,
départ observé, besoins de secours/compagnie, services et propositions,
projection des sorties verrouillées et moyens monétaires. Les capacités de
`biens.capacites_crues` et les lectures de planification, lumière, gardes et
services utilisent déjà la façade ou les vues de S1f : elles bénéficient de
la protection contre les mutations des retours, sans changer leur règle métier.
Le détecteur des avis consulte aussi ses vues d'observation déjà disponibles sur
la base ; son changement entre dans la clé du cache des empreintes.

**Inventaire et tests acquis.** Le contrôle AST de S1f est conservé et renforcé
par des contre-épreuves sur chaque attribut matériel (clé indirecte, alias et
mutation de cellule). Inventaire gelé dans `acces_memoire_s1a.json` :
**398 → 168 expressions**, sans aucune addition à l'inventaire antérieur.
Restent les familles non portées de S1h–j, les schémas et homonymes historiques ;
la branche générique de `croyance` n'est empruntée qu'après exclusion explicite
des familles matérielles et de la localisation.

Première passe : **35/35 verts**, trois fichiers (54,6 s), porte matérielle,
socle et localisation. Les nouveaux tests contrôlent copies imbriquées, pureté,
absence/fin négative/propriété inconnue et capacité de lumière crue malgré
l'épuisement réel non appris, puis disparition de capacité après fin apprise.
Chaînes : service réel de torche du **cas 217**, puis service de serrure ;
deux minutes d'un bloc ou deux fois une minute avec recharges, égalité de l'état
complet et de l'ordre JSON, des lignes, du rendu, de la scène et des paroles.

**Calcul détaché à reprendre.** `run400.py` exécute séquentiellement les tests
ciblés (23 fichiers, deux travailleurs) puis les empreintes **2 h × quatre
graines × Relais/mine/auberge/crue**, cache, référence exacte `8fa9e70e`, branche
mesurée `a3072b47`. Référence puis branche, priorité réduite, jamais plus de deux
travailleurs ; aucun temps du cache comparé. Aucun résultat d'empreinte ni bilan
final des tests voisins n'est encore revendiqué. Le marqueur `fin.json`, écrit
en dernier, contient les codes de sortie ; lire aussi les rapports et attribuer
les éventuels échecs avant clôture. Aucune suite complète ni Luna.

**Bruts et limites.** `C:/Users/msics/donjon/artifacts/s1g-400/` :
`tests-porte.json`, `tests-cibles.json/log`, `empreintes-base.json/log`,
`run400.py`, `lanceur.log/err`, **`fin.json`** attendu. Le contrôle AST reste
syntaxique/local, sans preuve exhaustive des flux interprocéduraux Python.
Pas de nouvelle politique de révision, d'oubli ou de jugement des capacités.
Aucune fonction de passage de 381 ni terminal de remboursement de 399 modifiés ;
recouvrement limité aux interfaces communes de perception/propositions.
`origin/integration 4c160145` fusionnée avant livraison : seulement le brief 401
et sa mention dans le point de reprise, conflit documentaire résolu ; code mesuré inchangé.
