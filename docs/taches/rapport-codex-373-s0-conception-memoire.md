# Lot 373 — S0, conception de la mémoire unifiée

30 octobre 2026 · `codex-s0-conception-memoire` · base `integration b83f5a59`.
**Documentation seule, non fusionnée.** Aucun fichier de `donjon/`, `tests/` ou `tools/`
modifié ; ni Luna, ni banc, ni suite lancés. Analyse statique avec un seul processus
Python léger à la fois, interpréteur du dépôt principal.

**Livraison.** [Conception](../conception-memoire-unifiee.md), annexes A–C sémantiques et
[index mesuré](../conception-memoire-unifiee-annexe-acces.md) : toutes les lectures explicites
de mémoire, types/fenêtres/questions, méthodes de tests dépendantes ; registres et croyances,
clés, écritures, invalidations, validations existantes, lecteurs et signatures de recherche.
Les plans et rapports d’origine ont été lus ; l’historique a été consulté par recherches ciblées.

**Mesures de source.** 74 expressions `memoire` dans le moteur, dont trois homonymes du cache
de recherche : **71 accès à la mémoire des événements, 55 fonctions, 17 fichiers**.
**247 accès dans 106 fichiers de tests**, support compris ; 26 dans les outils, diagnostics
inclus. Ces chiffres comptent aussi écritures, migrations et validations ; ils ne prétendent
pas mesurer 71 décisions ni une couverture exécutée. Index des autres champs, y compris
les suivis de signes, émissions G15, obligations E1–E4 et preuves de garde 337.

**Invariant proposé.** Une preuve garde son identité et sa provenance au-delà de l’épisode
racontable. Un refus, une dette ou un fait appris ne disparaît pas avec le récit ; une parole
ne devient pas vraie par son admission. Trois couches et registre subjectif, un seul accès
contrôlé par AST ; le flux mécanique `emissions_parole` existant reste unique. `agendas` et
`biens` conservent l’autorité sur obligations, clôtures, droits et comptes réels. Le dossier
ne reçoit que les conséquences connues ; aucune connaissance distante depuis l’archive E2.

**Migration.** S1a–S1p, découpables encore selon la taille des accès, avec comportement
historique conservé, inventaire AST décroissant, tests ciblés et empreintes 2 h prescrites.
Les premiers lots conservent le stockage ; le changement final de schéma exige une projection
réversible de **tout** l’état, sans retrait arbitraire pour faire passer les empreintes.
Rétention âge/importance, contradiction commune et dossier/axes sont des bascules de
comportement séparées après S1, dans les sous-lots de S2 ou numéros intermédiaires explicites.

**Interfaces et arbitrages.** Position datée de 374 dans le fait de localisation, sans seconde
formule ni réarmement par un relais ; soupçon faillible distinct d’un portage établi ; colère
aiguë séparée du grief durable en S2 ; projection publique A1 sans dossiers privés. Cinq
questions avec recommandation : rétention/résumés, reprise des anciennes sauvegardes,
rattachement des réparations, contradictions à égalité, lecteur du grief dans les refus.
Les décisions déjà acquises ne sont pas rouvertes.

**Vérifications et limites.** Comptages recoupés avec `rg`, liens locaux et présence des
champs du socle contrôlés. Plusieurs suivis de signes et `violences_joueur` n’ont pas de
validation structurelle exhaustive trouvée : lacune déclarée, à fermer au portage. Les
formats finaux des branches concurrentes 372/374 sont absents de cette base et devront être
relevés à leur intégration. Aucune garantie nouvelle du moteur, de coût ou d’absence de boucle.
Bruts reproductibles : `C:/Users/msics/donjon/artifacts/s0-memoire-373/`.
