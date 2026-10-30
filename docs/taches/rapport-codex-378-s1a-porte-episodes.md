# Lot 378 — S1a, porte des épisodes

30 octobre 2026 · `codex-s1a-porte-episodes` · base `integration eb84aad7`.
**Implémentation livrée ; vérification détachée en cours, lot non validé.**

**Invariant.** Les insertions et évictions explicites de la liste d'événements
passent par `donjon/memoire.py`. `retenir_episode` reprend les opérations de
`esprits.memoriser`, qui reste une façade compatible : registre des dits,
copie et date, indice et identité de preuve, ajout puis plafond de 40,
crochet relationnel puis défense. L'ajout réentrant reste immédiatement visible
au second crochet. `evincer_episodes` filtre en place sans copier les survivants
ni appeler de crochet. La migration des présences et les trois remplacements
sonores d'`ouie` passent par cette porte. Aucun champ ni format nouveau.

**Contrôle des accès.** `test_memoire_socle` fige les accès restants par
fichier/fonction/clé et détecte les mutations structurelles par indice,
méthode, alias local, clé constante indirecte et retour brut. Contre-épreuves
négatives incluses ; les homonymes de diagnostic, créations vides historiques
et fixture d'outil sont admis par expressions précises, sans exemption de fichier.
L'inventaire gelé contient 102 expressions, outils et homonymes compris ; il
inclut désormais les trois appels au lecteur brut `defense.souvenirs` et son
retour conditionnel. Ce total ne se compare donc pas directement aux 71 accès
à la mémoire narrative seule de S0. Aucun lecteur du jeu n'est porté en S1a.

**Vérifications prévues et lancées.** Tests du socle : copie profonde, datation,
plafond, identité des survivants, ordre des crochets réentrants, migration des
présences. Chaîne historique d'Hugues appelé au couloir de l'auberge et autre
cas de Gorm au beffroi du Relais : six minutes d'un bloc ou trois fois deux
minutes, recharges, état complet et ordre JSON, rendu, scène et émissions.
Treize fichiers ciblés sont programmés après les empreintes : socle mémoire,
esprits, relations graduées, défense, temps/état, ouïe, ouïe commune/témoins,
appels restes, demander cause, constater soupçon, déjà dit et banc PNJ.
Empreintes 2 h × quatre graines × Relais/mine/auberge/crue, référence `main`
`0bad2272` en cache, puis comparaison à la base exacte `eb84aad7` pour attribuer
les écarts dus à l'intégration. Égalité brute attendue à la base, sans exclusion.
Pas de suite complète ni Luna. Deux processus au plus, priorité réduite.

**Résultats encore à lire.** Aucune réussite des tests ou identité des
empreintes n'est encore affirmée. Les deux comparaisons puis les tests tournent
sans agent en attente. Fichier final attendu :
`C:/Users/msics/donjon/artifacts/s1a-378/verification-fin.json`.
Rapports bruts : `empreintes-main.json`, `empreintes-base.json`, `tests.json`
et leurs journaux dans le même répertoire. Reprendre ces résultats et corriger
les éventuels échecs avant de déclarer le lot terminé.

**Limites et recouvrements.** Le contrôle AST suit les alias locaux explicites,
pas tous les flux interprocéduraux de Python. Les lectures mutables, mutations
du contenu des épisodes et leurs anciens retours restent gelés pour S1b–e ;
le module d'accès ne renvoie aucun stock. L'oubli âge/importance reste hors lot.
Recouvrement avec 374 : import de `MEMOIRE_MAX`, migration dans `installer` et
façade `memoriser` d'`esprits.py`, sans toucher les localisations. Aucun changement
dans `pnj.py`, `echanges.py` ou `agendas.py` (lots 376/377).
