# Lot 400 — S1g, vues des états matériels crus

31 octobre 2026 · `codex-s1g-etats-materiels` · base exacte `integration 8fa9e70e`.
Code mesuré : **`a3072b47`**. Intégration **`d23d081d`** fusionnée à la clôture.
**Lot clos, non fusionné ; aucun calcul en attente.**

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

**297/298 tests verts**, 23 fichiers (772,2 s), aucune erreur ni saut.
Les nouveaux tests contrôlent copies imbriquées, pureté,
absence/fin négative/propriété inconnue et capacité de lumière crue malgré
l'épuisement réel non appris, puis disparition de capacité après fin apprise.
Chaînes : service réel de torche du **cas 217**, puis service de serrure ;
deux minutes d'un bloc ou deux fois une minute avec recharges, égalité de l'état
complet et de l'ordre JSON, des lignes, du rendu, de la scène et des paroles.

Le seul rouge est `planification.MemoireTests.test_une_croyance_une_limite_ou_l_horloge_relancent_la_recherche` :
le plan inspecte l'échoppe plutôt que d'y demander les vivres au marchand.
Rejoué isolément sur **la base exacte `8fa9e70e`**, il échoue à la même assertion,
avec le même plan ; oracle conservé, aucune correction de comportement revendiquée.

**Empreintes : 16/16 identiques.** **2 h × quatre graines
1985/7/42/2024 × Relais/mine/auberge/crue**, référence exacte `8fa9e70e`,
branche `a3072b47` : chronique, mesures et état final complet
concordent, sans exclusion ni plantage. Les 16 nuits de chaque
côté sont rangées dans le cache. Avis auxiliaires identiques : zéro non justifié,
vingt à expliquer. Référence puis branche, priorité réduite, deux travailleurs
au plus ; aucun temps du cache comparé. Aucune suite complète ni Luna.

**Bruts et limites.** `C:/Users/msics/donjon/artifacts/s1g-400/` :
`tests-porte.json`, `tests-cibles.json/log`, `empreintes-base.json/log`,
`run400.py`, `fin.json`, `attribution-planification-base.log` et
`tests-apres-integration-corriges.log`. `fin.json` garde le code rouge des tests ;
`conclusion.json` consolide l'attribution et la clôture. Le contrôle AST reste
syntaxique/local, sans preuve exhaustive des flux interprocéduraux Python.
Pas de nouvelle politique de révision, d'oubli ou de jugement des capacités.
Aucune fonction de passage de 381 ni terminal de remboursement de 399 modifiés ;
recouvrement limité aux interfaces communes de perception/propositions.
`origin/integration d23d081d` fusionnée : correctif de raccord des émissions du
401 et documentation, sans recouvrement du moteur PNJ mesuré ; conflit du point
de reprise résolu en conservant les deux entrées. Les empreintes portent sur le
code PNJ inchangé ; **20/20 contrôles verts après fusion** (61,2 s), raccord des
émissions et inventaires. Aucun calcul ni contrôle ciblé restant.
