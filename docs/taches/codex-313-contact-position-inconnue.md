# Tâche Codex 313 : une position de contact inconnue n'est pas une absence

Second des deux petits lots proposés par le diagnostic 308. Lis `AGENTS.md` et
`docs/taches/rapport-codex-308-services-apres-303.md` (Relais 7, second lot proposé). Captures et bruts dans
`C:\Users\msics\donjon\artifacts\services-308\`.

## Le constat
Relais 7, instant 856 : Gorm doit servir des vivres à Brune. Pour `servir vivres` et `prendre vivres_2`, l'approche
renvoie 0, puis le geste renvoie `False` : la source est hors de portée et aucune case n'est crue. Si l'on fournit
expérimentalement la case du contenant, une marche se déclenche (30 et 76 dixièmes). Le même défaut existe sur la base,
avant le lot 303.

## L'invariant
**Une cible ou une source sans case crue, ou trop loin, n'est pas une cible absente. L'approche prépare d'abord son
observation (aller dans son lieu cru, la chercher) ou hérite d'une position admissible connue (la case crue de son
contenant, du porteur ou du support). La charge est conservée jusqu'à un démenti réellement constaté.** Aucune
lecture de la position réelle d'un objet ou d'un personnage mobile non perçu. Une position héritée ne vaut que si la
croyance sur le contenant ou le porteur la donne.

Fonctions en cause : `pnj._case_crue`, `pnj._approcher`, `pnj._hors_d_atteinte`, `trajet_estime.approche`, et leur
contrat avec `Vue.case_objet` et `planification._mesurer_direct`. Le plan et l'exécution doivent lire la même règle.

## Vérification
- La capture Relais 7 rechargée : Gorm atteint la source et sert. Vérifie aussi que monde, rendu et scène sont
  identiques après recharge, et que le résultat est le même avec un laps d'un bloc ou découpé.
- Un autre cas de même nature (une source dans un contenant d'une autre salle).
- Une contre-épreuve où la source a réellement disparu : le démenti est constaté, sans boucle.
- **Banc rapide** : 4 h × quatre graines, Relais, auberge et mine, contre la référence de l'intégration (cache).
  Compte :
  - les gestes refusés à l'approche ;
  - les services ;
  - les suspects 219 par nuit ;
  - les boucles.

  Calcul détaché avec un fichier de fin.
- Pas de Luna, ni de suite complète.

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite. Un autre lot (312, sur le laptop) touche
`planification.planifier_tache` et `echanges.empeche` : ne les modifie pas.

## Livraison
- Branche `codex-contact-inconnu`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur : la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-313-contact-position-inconnue.md`.
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\contact-313\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
