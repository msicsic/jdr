# Sauvegardes de régression du coût de calcul

États complets du banc, graine 7, départ tiré, capturés juste après le premier
certificat d'absence du besoin indiqué dans le fichier `meta` :

- mine, minute 365 : Rémy cherche à manger ; joueur dans la galerie ;
- crue, minute 349 : Brune cherche à manger ; joueur dans la chambre de la cloche.

Format de `Monde.sauver`, sans suppression de champs. La capture interrompt le
banc au retour de `_sans_plan`, avant la publication de ce résultat de recherche.
`test_cout_suite.py` les recharge, change les prix par le besoin, contrôle chaque
reprise avec `VERIFIER`, fait vivre cinq minutes et compare monde complet,
chronique produite, rendu et scène perçue après un nouveau rechargement.
