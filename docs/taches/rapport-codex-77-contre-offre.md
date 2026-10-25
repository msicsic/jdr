# Lot 77 — Une condition annoncée avec le refus

Branche `codex-contre-offre`, non fusionnée, base d'intégration **38e5d7e**,
brief **c1cb020**. Aucun appel à Luna, aucun changement de `main` ou des scénarios.

`echanges.contre_offre` inscrit une `propositions.offre` commune avec le refus avant
affichage : premier prix positif où la réticence propre cesse, ou repas servi dont
une simulation prouve qu'il libère le bien nécessaire au plan. Méfiance, garde et
pulsion durable ne donnent pas de condition inventée. Aucun cas de scénario.

`pnj_propositions.plan_recours` intervient après les moyens ordinaires sans faute :
payer, ou planifier le service existant puis redemander. `deliberation.tient` conserve
la condition sans délai ni offre au hasard à sa place. `servir` garde la preuve
accomplie avec le refus, indépendamment de la mémoire courte ; un repas antérieur ne
compte pas. `demander` honore l'accord sans second jet. L'esprit vérifie la sauvegarde.

`planification.py` et `_entrees` sont inchangés : ce recours vit hors recherche.
La chronique conserve les annonces, conditions remplies et issues habituelles.

## Vérification

Sept tests nouveaux : deux biens payés, repas/prêt et autre clé, repas antérieur,
condition impossible, méfiance/garde, parcours autonome ; état et rendu après recharge,
même laps continu/découpé pour prix et service. Suite complète unique : **1 891 tests,
16 ignorés, 1 479,1 s**, trois processus à priorité réduite. Sept échecs et une erreur
d'anciennes attentes dans cinq fichiers : chronique enrichie, prix dit, condition
impossible retenue ; scènes solvable/insolvable explicitées. Ces cinq fichiers sont
repris verts (**72 tests**, dernier fichier **25/25** après correction d'une attente
de prix). Bilan consolidé vert, aucune seconde suite complète. La vérification a
prolongé le créneau initial du lot ; aucun code moteur changé pendant ces reprises.

Banc contre **38e5d7e**, **4 h × quatre graines × quatre scénarios**, trois processus,
référence jouée une fois et mise en cache. Totaux sur quatre graines, avant → après :

| Scénario | Contre-offres / remplies | Demandes accordées | Vols tentés | CPU moyen par nuit |
| --- | ---: | ---: | ---: | ---: |
| Relais | 3 / 3 | 3 → 6 | 2 → 0 | 10,05 → 7,84 s |
| Mine | 9 / 5 | 8 → 12 | 1 → 2 | 23,12 → 24,15 s |
| Auberge | 4 / 3 | 8 → 11 | 1 → 1 | 24,05 → 41,48 s |
| Crue | 1 / 1 | 2 → 3 | 8 → 8 | 30,63 → 30,03 s |

Aucun plantage, violation, usurpation, nouveau code d'audit ou cycle de contre-offre.
Les 17 conditions naturelles sont monétaires ; service vérifié par tests. Répétitions :
avertissements mine 1985 **0 → 1**, 7 **0 → 2**, 2024 **2 → 0** ; aide auberge 2024
**0 → 1** après épuisement des ressources. L'absence générale de répétition n'est pas garantie.

Réserve : auberge **2024, 26,89 → 100,95 s CPU**, recherches **297 → 287**, noir
**160 → 170 min·PNJ** ; les trois autres graines sont plus rapides. Fils dans
`artifacts/contre-offre-{banc-4h,mesures}.json` et `contre-offre-tests-*.txt`.

## Limites

Satisfaction corporelle immédiatement exprimable : repas servi seulement. Autres besoins
et repas insuffisant : aucune condition non démontrée. L'offre ne réserve pas le bien :
présence, stock, droits et faisabilité sont revalidés ; accord non garanti après disparition
ou nouvel empêchement matériel. Contenu typé du joueur et tâches promises restent à venir.
