# Lot 178 — Personnes retenues après une opération de porte

Branche `codex-retenus-apres`, **non fusionnée**, base `integration dd815f4`.
Poste partagé avec le lot 179 ; deux travailleurs au plus, priorité réduite.
Bruts exclusivement `C:/Users/msics/donjon/artifacts/retenus-178/`.

**Invariant.** `tenir.retenus_apres` calcule sans mutation les personnes que
l'auteur croit retenir après un verrouillage. L'exécution `tenir.enfermer` et
`couverture_action._passages` partagent cette projection. Chaque opération de
porte expose `personnes_retenues_apres_operation`, avec les références publiques
des personnes déjà connues. Une fermeture sans verrouillage ne suffit pas ;
une autre issue libre ou de verrou inconnu interdit de conclure à l'enfermement.
Les positions et verrous distants réels ne remplacent pas les croyances.
La vue du joueur est actualisée sur une copie : un souvenir démenti n'est pas
une présence. Aucun prompt, scénario, effet physique ou choix de PNJ changé.
Les clés des victimes restent du ressort de leur captivité vécue, selon le
contrat du lot 140 ; le dossier décrit la contrainte qualifiée par l'auteur.

**Vérification ciblée.** **29 tests verts, trois fichiers, 44,046 s**, dont les
cas Bram/bureau et Rémy/réserve : fermer puis verrouiller, dossier sans mutation,
contre-revue simulée admettant le plan, événements d'enfermement enregistrés,
monde complet et rendu identiques après recharge. Autre issue libre ou inconnue :
aucune personne retenue et refus simulé du plan qui prétend enfermer, avant
exécution. Le verrou réel caché ne devient pas un verrou cru. Les épreuves
d'évasion et de captivité des lots 136/140 restent vertes. Deux reprises ont
corrigé uniquement les scènes nouvelles : géométrie réciproque des issues,
champ `porte: None`, retrait d'une connaissance initiale de Josse.

**Suite unique et non-régression.** **2 271 tests, 261 fichiers, 1 254,899 s**,
deux échecs MiMo historiques `6 != 5` (`test_fournisseurs_jeu`,
`test_restes_fusions`), zéro erreur ou ignoré ; aucune seconde suite.
Comparaison directe à la fonction `enfermer` extraite de `dd815f4` : **8/8
exécutions identiques**, deux salles, auteur joueur/PNJ, présence connue/inconnue,
état complet et événements, monde/rendu après recharge ; projection sans mutation.
Premier lancement de cette sonde arrêté avant exécution par un conflit d'import
`tests`/`tools/tests.py`, corrigé uniquement dans le lanceur externe.
**12/12 nuits 2 h identiques**, Relais/mine/rixe × graines 1985/7/42/2024 :
chroniques, mesures, récits, souvenirs, empreintes physiques et états complets ;
monde et rendu rechargés identiques. Références exclusivement relues : sorties
du lot 175 pour Relais/mine, cache `79594e4` pour rixe. Aucun rejeu de référence,
aucun temps comparé. Bruts : `suite.json`, `execution-base.json`, `empreintes.json`
et `mondes/`. Les traces automatiques des tests ont été déplacées et redirigées
dans `automatiques/` ; jonction temporaire retirée avant livraison.

**Luna et limites.** Aucun appel modèle, sur instruction. Les fils réels du
lot 177 conservent le refus demandant de déplacer Bram déjà dans le bureau ;
le nouveau dossier fournit maintenant la conséquence manquante. Les tests
simulés prouvent le contrat transmis, pas le jugement sémantique de Luna.
Amélioration sur les fils réels, absence générale de faux refus et critère
des trois appels non certifiés. La commande exacte est dans `luna-a-jouer.txt`
et son lanceur `jouer_luna.py` : deux passes enfermer/traîner, puis une passe
des neuf autres bancs de force, référence `cdaf371` par cache, une partie
simultanée à priorité réduite, nouveaux fils dans le dossier du lot.

Aucune clé de signature Git configurée : commit non signé. Livraison de la
branche seule, sans fusion ni modification de `main`.
Poussée bloquée par la revue automatique : destination et confiance de `origin`
jugées insuffisamment établies, risque d'exfiltration de code privé. Repli demandé
appliqué : commit local uniquement, aucune nouvelle tentative de poussée.
