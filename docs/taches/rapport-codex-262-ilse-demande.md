# Tâche 262 (diagnostic) : pourquoi Ilse ne demande pas une part à Gorm (crue 7)

Diagnostic seul, aucun code du jeu modifié. Bruts : `C:\Users\msics\donjon\artifacts\ilse-262\`.

## Reproduction

Mêmes captures que le 261 rechargées aux minutes 270, 400 et 600 (graine 7, Ilse en
`chambre_cloche`, joueur passif). Monde et rendu identiques après rechargement. Pour chaque
capture, `planification.gestes` est appelé depuis l'état initial d'Ilse avec le but `faim`
(`emplois = {"manger"}`), comme le fait `deliberation._plan_faim` via `planification.planifier`.

## Gestes proposés depuis l'état initial

- **270 min** (1 geste) : `aller` vers `beffroi`.
- **400 min** (1 geste) : `aller` vers `beffroi`.
- **600 min** (2 gestes) : `aller` vers `beffroi`, `chauffer` `poele_guet`.

Aucun `demander` de part de vivres à Gorm (marchand) n'apparaît à aucun des trois instants,
ni aucun `acheter`.

## Ce qui exclut la demande de part

Ilse croit les vivres à la réserve (`antichambre`, 2 portions à 270/400, 0 réel à 600 mais elle
n'en sait rien : aucun `etat` cru, donc `deliberation._disponible_cru` reste vrai), source
`savoir`, confiance 0,9. Gorm (marchand) est cru en `antichambre`. Elle est en
`chambre_cloche`. Les relations ne portent ni méfiance ni rancune (confiance 40, rancune 0) et
`deliberation.refus_retenu` pour `demander`/`acheter` sur les vivres vaut `None` à ces trois
instants : aucun refus retenu ne l'empêche.

Dans `planification.gestes`, les vivres sont « ailleurs » (salle `antichambre`) pendant qu'Ilse
se tient en `chambre_cloche` ; `_parts` est donc appelé. Dans
`planification._parts_calculer` (lignes de la branche non promise, `ou = v.salle(e, donneur)`),
la branche `demander` n'est offerte que si `ou == e.salle` (Gorm présent avec elle) ; la branche
`_chercher` n'est offerte que si `ou is None` (lieu de Gorm inconnu). Ici `ou` vaut
`antichambre`, connu et différent de `chambre_cloche` : aucune des deux branches ne s'applique,
donc aucun geste `demander` de part n'est généré depuis l'état initial. Atteindre Gorm exigerait
d'abord un déplacement, mais `Vue.route` de `chambre_cloche` vers `antichambre` vaut `None` : le
seul chemin passe par la porte `porte`, crue verrouillée (`verrouillee` vrai, source `essai`,
confiance 1,0), qu'Ilse ne peut ni ouvrir (pas de clé portée) ni crocheter (aucune capacité
`crochetage`). L'antichambre n'est donc pas dans les salles atteignables.

La condition excluante est donc la combinaison de deux faits crus cohérents : la localisation
connue et différente de Gorm (`antichambre`) et l'inaccessibilité de cette salle depuis le guet
(porte verrouillée sans moyen de l'ouvrir). Le modèle n'offre pas de demande à distance, et
aucun déplacement possible ne mène à Gorm.

## Verdict

Exclusion juste selon les croyances d'Ilse. Elle croit Gorm dans l'antichambre, croit le passage
verrouillé et n'a ni clé ni crochetage ; ces croyances sont exactes dans l'état réel. Aucun refus
retenu, aucune méfiance ni rancune, aucune croyance périmée et aucun vivre cru épuisé n'intervient
pour les portions (inconnues d'elle). Aucune règle commune n'est en cause : la demande de part
exige la co-présence, et le déplacement requis est impossible d'après ce qu'elle croit. Aucun
code modifié.