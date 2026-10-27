# Lot 177 — État final dans la contre-revue

Branche `codex-contre-revue-etat-final`, **non fusionnée**, base `integration`
`4cb4361`. Poste partagé avec les lots 175 et 176 ; deux travailleurs réduits
au plus. Bruts exclusivement `C:/Users/msics/donjon/artifacts/contre-revue-177/`.

**Invariant.** La fidélité porte sur l'état final établi par le moteur : les
déplacements et effets nécessaires au geste en font partie ; un état demandé
déjà vrai d'après le dossier ne demande pas une opération pour le rétablir.
`couverture_action.INSTRUCTIONS` demande une lecture commune du titre, de
l'information, des déplacements, des passages, des effets et des étapes. Les
départs/présences sont distingués des arrivées/états après opération. Une présence
ne prouve pas la fermeture d'une issue. Un changement étranger au geste ou un
état demandé absent restent des motifs de refus. Le dossier existant fournit
déjà les données nécessaires : aucune nouvelle projection, mutation ni exception
par action, lieu, personne ou formulation ; aucun effet moteur modifié.

**Constat de départ.** Les fils du lot 172 transmis par l'orchestrateur conservent
le faux refus du pas du joueur inhérent au traînage (deux passes), et le faux
besoin de déplacer Bram déjà dans le bureau (première passe). Leurs mesures
restent celles du lot 172 ; aucune mesure de Luna du présent lot n'est disponible.
Refus et SHA-256 des quatre fils consultés : `constat-172.json` dans les bruts.

**Vérification.** 16 tests ciblés finaux verts (40,771 s), fichiers `test_force_luna.py`
et `test_contre_revue.py`. Le cas réel Brune/seuil et un autre seuil vérifient les
deux déplacements ; Bram/bureau et Rémy/réserve vérifient la fermeture seule
sans déplacement de la personne. Dossiers sans mutation, console avec MJ simulé,
état complet et rendu après recharge. Un déplacement de tiers non demandé, une
mauvaise direction et une ouverture contraire à l'enfermement sont refusés avant
exécution, dans deux scènes. Deux premiers essais ont révélé une préparation
de test incomplète de la présence connue, corrigée en enregistrant l'observation
initiale ; aucun élargissement du dossier de perception. La suite a ensuite signalé
un échec dans la demande négative d'enfermement : le nom Rémy, inconnu de Corvus
dans cette scène, arrêtait la saisie avant la contre-revue. Remplacé par « cette
personne » pour tester le refus du plan, puis les deux fichiers ciblés repris
avec succès dans leur version finale. Aucune seconde suite complète.

Suite complète unique : **2 260 tests, 260 fichiers, 1 283,253 s**, zéro erreur
ou ignoré. Trois échecs : les deux MiMo historiques `6 != 5`
(`test_fournisseurs_jeu`, `test_restes_fusions`) et le test négatif décrit ci-dessus,
corrigé puis vert dans les **16 ciblés finaux**. La suite n'a pas été relancée.
Pas de banc moteur : seules les instructions de contre-revue et les tests
changent, aucun chemin d'exécution du moteur ni état de scénario modifié.

**Luna et limites.** Aucun appel modèle, conformément au brief. Commande exacte
dans `luna-a-jouer.txt`, avec `jouer_luna.py` dans le dossier des bruts : deux
passes traîner/enfermer, une passe des neuf autres bancs force et atelier/relais,
contre `cdaf371`, cache de référence réutilisé, une partie simultanée, priorité
réduite et nouveaux fils redirigés dans le dossier du lot. Le lanceur adapte
uniquement en mémoire le chemin de sortie du harnais, qui n'a pas d'option
`--sortie`. Les tests simulés prouvent le contrat et l'exécution, pas le jugement
de Luna : absence générale de faux refus, amélioration sémantique et critère des
trois appels **non certifiés**. Aucune comparaison de vitesse depuis le cache.

Aucune clé Git de signature configurée : commit non signé. Livraison de la
branche seule, sans fusion ni modification de `main`. Jonction temporaire des
traces automatiques retirée après les tests ; aucun brut conservé dans le worktree.
