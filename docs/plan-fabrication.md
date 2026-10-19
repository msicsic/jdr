# Jalon : fabrication générale

Point de départ : seule l'échelle à barreaux existait, avec des matériaux que l'auteur du
scénario déclarait (`ressource`, longueur, charge, dans `scenario_atelier.json`). Le MJ ne
pouvait pas employer un objet existant comme matériau : les planches du Relais ne servaient à
rien. L'objectif est de sortir d'une fabrication scriptée.

## Décisions

- **Une description physique commune à tout objet** : une forme (barre, plaque, lien, bloc,
  étoffe), ses dimensions, une matière prise dans une table de conventions de jeu (densité,
  résistance), et un nombre de pièces pour un lot.
- **Le MJ décrit, le moteur vérifie et déduit.** Le MJ établit la description quand elle sert,
  d'après le nom, la description et le sens commun (on ne déduit pas des dimensions d'une
  masse). Le moteur vérifie la cohérence avec la masse connue (volume × densité) et déduit ce
  qui en découle : longueur disponible, charge supportée. L'audit physique juge la plausibilité.
  L'auteur peut fournir la même description d'avance.
- **Lots et prélèvement** : un lot fournit des pièces distinctes ; une barre se coupe à longueur ;
  un lien se consomme en longueur.
- **Assembler selon des usages modélisés** : le MJ propose pièces, jonctions et usage visé ; le
  moteur vérifie les contraintes de cet usage et crée l'objet. Il ne simule que les usages qu'il
  sait modéliser (monter, puis franchir un vide, caler…) ; toute autre construction reste un
  objet ordinaire.
- **Plus tard** : un carnet des cas non prévus (intentions sans règle), puis des règles
  déclarées par le MJ dans un vocabulaire typé et interprétées par le moteur. Pas de code du
  moteur écrit pendant la partie.

## Étapes

1. Description physique, qualification par le MJ (`etablir_faits`), contrôle par la masse et
   l'audit, affichage à l'examen ; les matériaux de l'atelier y sont migrés.
2. Lots, prélèvement et découpe.
3. Assemblage générique, usage « échelle » en remplacement de `fabriquer` ; vérifié sur
   l'atelier et avec les planches du Relais.
4. D'autres usages, un par un.

## Avancement

- Étapes 1 à 3 faites. `assembler` remplace `fabriquer` (gardé comme alias) ; `decouper`
  complète le prélèvement. Bancs `materiaux`, `lots` et `assemblage` (tests/data/bancs), 3
  passes avec Luna et avec Haiku.
- Écart : la vérification « avec les planches du Relais » n'a pas été faite en partie. Le
  Relais n'a que deux planches, propriété d'Aubin : de quoi deux montants, rien pour les
  barreaux. Un test assemble une échelle de planches décrites dans l'atelier et la recharge.

Les conventions physiques (densités, résistances) sont des règles de jeu, pas un calcul
d'ingénierie.
