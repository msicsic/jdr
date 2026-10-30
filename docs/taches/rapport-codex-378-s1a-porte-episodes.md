# Lot 378 — S1a, porte des épisodes

30 octobre 2026 · `codex-s1a-porte-episodes` · base `integration eb84aad7`.
Intégration `d63d8fb7` fusionnée (`38a1cf2f`), puis `c63dd563` (brief documentaire) ;
seul conflit documentaire, aucun recouvrement de code.

**Invariant et code.** Toute insertion/éviction explicite de la liste d'épisodes passe
par `donjon/memoire.py`. `retenir_episode` conserve la séquence historique : registre
des dits, copie/date, indice et identité de preuve, ajout/plafond 40, crochet relationnel,
puis défense. Un ajout réentrant reste visible aux crochets suivants. `esprits.memoriser`
est une façade compatible ; `MEMOIRE_MAX` reste importable depuis `esprits`.
`evincer_episodes` filtre en place, sans copie des survivants ni crochet : migration des
présences et trois remplacements sonores d'`ouie` portés. Liste, clés, ordre et sérialisation
restent inchangés. Aucun changement des localisations, choix, délais ou paroles.

**Contrôle AST.** Inventaire fermé fichier/fonction/clé dans
`tests/fixtures/acces_memoire_s1a.json`, mutations structurelles détectées par indice,
méthode, alias local, clé constante indirecte, méthode détachée et retour brut ;
contre-épreuves négatives incluses. Homonymes de diagnostic, créations vides historiques
et fixture d'outil admis par expressions précises. Les 102 expressions gelées comprennent
outils, homonymes et quatre accès ajoutés au relevé du lecteur brut `defense.souvenirs` :
ce total ne se compare pas directement aux 71 accès narratifs seuls de S0.

**Tests.** Treize fichiers ciblés, 158 tests couverts : les 151 tests existants passent ;
les 7 nouveaux tests passent après correction de deux assertions de scénario. Le cri
d'aide n'impose pas de parole, et Gorm force la porte sans produire la ligne « va voir ».
Aucune correction moteur n'a été nécessaire après les mesures. Le socle vérifie copie,
dates, plafond, identité des survivants, ordre des crochets réentrants et migration.
Chaînes : Hugues appelé au couloir de l'auberge et Gorm au beffroi du Relais ; six minutes
d'un bloc ou trois fois deux minutes avec recharges. État complet et ordre JSON identiques,
puis rendu, scène et registre de paroles identiques après recharge ; le second parcours
contrôle aussi la confidence effectivement prononcée. Après fusion, **30 tests passent**
(socle, temps/état, ouïe commune ; 86,3 s). Aucun échec restant sur le périmètre vérifié.

**Empreintes.** 2 h × quatre graines (1985, 7, 42, 2024) × Relais/mine/auberge/crue :
**16/16 nuits identiques à la base exacte `eb84aad7`**, chronique, mesures et état final
complet, sans exclusion ; aucun plantage. L'ancien `main 0bad2272` diverge dès la minute 0.
Attribution recoupée : les états finaux de la branche sont identiques dans les deux
comparaisons, et les 16 états de la base divergent eux-mêmes de cet ancien main.
Références mises en cache ; aucune relance de référence. Pas de suite complète ni Luna.
Deux processus au plus, priorité réduite. Les empreintes précèdent la fusion des lots
376/377/379 ; elles ne sont pas présentées comme une mesure de cette intégration nouvelle.

**Bruts et limites.** `C:/Users/msics/donjon/artifacts/s1a-378/` :
`empreintes-main.json`, `empreintes-base.json`, `tests.json`,
`tests-socle-corrige.json`, `tests-apres-integration.json` et journaux.
Le contrôle AST suit les alias locaux explicites, pas tous les flux interprocéduraux
possibles de Python. Lectures mutables et modifications du contenu des épisodes restent
pour S1b–e ; aucune API du nouveau module ne renvoie le stock. L'oubli âge/importance reste
hors lot. Recouvrement 374 limité à l'import, la migration et la façade d'`esprits.py` ;
aucune modification propre au lot dans `pnj.py`, `echanges.py` ou `agendas.py`.
