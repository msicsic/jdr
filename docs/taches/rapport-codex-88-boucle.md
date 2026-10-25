# Suite du lot 88 — Cause de la rafale de déplacements

Branche `codex-avis-reels`, **toujours non fusionnable** ; base `c9245dd`.
Diagnostic seul : aucun code moteur, scénario ou profil modifié ; aucune nouvelle
suite complète. Sans Luna, priorité réduite, au plus deux calculs simultanés.

**Cause établie.** Les **237 passages** de l'audit appartiennent à **Aubin**, entre
660 et 719 min (heure civile, comptage par PNJ). Son pire intervalle glissant
atteint même **292 passages entre 649 et 708 min**. Gorm et Ilse ne produisent pas
cette rafale. La violence déclenche la trajectoire, mais n'explique pas sa persistance :
à 680 et 690 min, Aubin n'a plus aucun auteur de violence actif et continue la boucle.

| Instant | Choix d'Aubin | Plan / raison |
| --- | --- | --- |
| 649:00 | chaleur | Prendre la torche de Brune pour rallumer le poêle ; violence, puis riposte de Gorm |
| 649:10,5 | fuir Gorm | Quitter le refuge pour la conduite |
| 649:22,7 | lumière | Rejoindre la galerie éclairée |
| 650:12,3 | pulsion | Retour au refuge pour l'inspection, période 32 min |
| 650:21,3 | lumière | Au palier noir, retour à la galerie |
| 650:30,3 / 36,3 / 42,3 | pulsion / lumière / pulsion | Même alternance, plusieurs fois dans la minute |

**Règle fautive.** `planification.eclairer(tenir=True)` tarife un séjour éclairé,
mais exporte ici seulement `aller galerie` : ce recours s'achève dès l'arrivée,
sans geste de progression de sécurité. `deliberation._plan_lumiere` ne propose
plus rien là où Aubin voit clair. `_plan_abri` ne fournit pas de relais stable
dans ce lieu sans compagnie fiable. `_candidats` retrouve alors l'inspection non
satisfaite ; `planification._pulsion` propose son trajet sans garantir qu'il résiste
au recours prioritaire de lumière. Au palier, la sécurité encore urgente rétablit
ce recours. L'inertie de `choisir` protège les recours d'un **même besoin**, pas
la ronde de devoir contre la sécurité. `pnj._avancer` rechoisit à chaque minute,
à la fin du plan et lors des éveils perceptifs : il n'attend pas une minute entière
entre ces demi-tours. L'inspection non exécutée reste due (`satisfaite`, visites),
donc le cycle se relance sans nouvel avis ni nouvelle violence.
À 650:12,3 : sécurité **99,973**, lumière crue **1**, ni montée ni menace d'eau ;
`_plan_abri` renvoie `None`, seule Ilse est fiable mais sa salle est inconnue.

**Comparaison à la base.** Premier écart de chronique à **102:25**, premier
déplacement décalé à **194 min** (une seconde) ; empreintes physiques identiques
à 240 min, différentes à 480 min, donc bien avant la violence de 649 min. Dans
la nuit normale de la base, Aubin est au refuge à 649–650 min, sans intention ni
danger ; aucune violence, pire heure **24 passages** (Gorm). Cette nuit ne boucle pas.

Le défaut est néanmoins latent dans son moteur : reprise de la **capture stable
à 645 min**, sauvegardée après un pas complet, avec `social.py` de c9245dd ou de
la branche (seule différence de code moteur entre les deux). De 645 à 675 min :
**128 passages d'Aubin** dans les quatre reprises, trente minutes d'un bloc ou
par quinze secondes sauvegardées/rechargées. **Monde complet et rendu identiques**,
SHA-256 d'état `a2279ca93dc544a59d81a6b6af1279849b37f47ff4923e1e5ee85540259fa868`.
Les **249 événements** de cette période retrouvent exactement la nuit réelle.
Cela prouve le défaut sur un même état, pas une boucle dans une autre nuit native
non mesurée de la base.

**Arrêt au diagnostic, point 3 du brief.** L'invariant à rétablir est la cohérence
entre un recours prioritaire, son état terminal et l'exécutabilité du plan suivant :
un plan inférieur ne doit pas défaire immédiatement ce recours, sauf s'il intègre
les moyens de le poursuivre. Cela concerne choix, prérequis de parcours, progression
et mémoire de recherche (`_entrees`), au-delà de la transmission des avis. Un délai,
une interdiction visant l'agresseur ou une priorité spéciale à cette ronde ne
corrigerait pas la boucle lumière/inspection. Pas de correction partielle livrée ;
ce contrat commun demande un lot distinct sur `deliberation.py`/`planification.py`.

**Audits 12 h refaits**, chroniques strictement identiques aux premières mesures :

| Version / graine | Pire heure civile par PNJ | Pire 60 min glissantes par PNJ | Avis / adoptions |
| --- | ---: | ---: | ---: |
| Base 2024 | 24, Gorm | 28, Gorm | 0 / 0 |
| Branche 2024 | **237, Aubin** | **292, Aubin** | 6 / 0 |
| Branche 500 | 22, Gorm | 32, Gorm | 16 / 0 |

Aucun plantage ni usurpation. Bruts, choix horodatés, capture, script de reprise
et bilans : `artifacts/88/suite-boucle/`. La boucle reste **non corrigée**.
