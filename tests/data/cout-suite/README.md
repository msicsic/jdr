# Sauvegardes de régression du coût de calcul

États complets du banc, graine 7, départ tiré, capturés juste après le premier
certificat d'absence du besoin indiqué dans le fichier `meta` :

- mine, minute 365 : Rémy cherche à manger ; joueur dans la galerie ;
- crue, minute 443 : Aubin cherche à manger ; joueur dans la chambre de la cloche.

Ces deux captures ont été régénérées après la fusion de `main` a7ecb50, avec les
axes des relations 3b. Les captures historiques avant fusion ne sont plus utilisées.

Format de `Monde.sauver`, sans suppression de champs. La capture interrompt le
banc au retour de `_sans_plan`, avant la publication de ce résultat de recherche.
`test_cout_suite.py` les recharge, change les prix par le besoin, contrôle chaque
reprise avec `VERIFIER`, fait vivre cinq minutes et compare monde complet,
chronique produite, rendu et scène perçue après un nouveau rechargement.

Les captures compressées `auberge-*-borne` viennent de deux contre-épreuves de
dominance sur la même base a7ecb50 : Lucien, graine 7 à 644 (abri), graine 42 à 627
(placer le ballot à l'étable). La recherche originale reste sans plan à 4 000 nœuds ;
le prototype de dominance trouve respectivement un plan de coût 130 et 130,5.
Le prototype n'est pas utilisé par le moteur. Le test conserve les résultats joués
et vérifie état complet, rendu et vie du monde après rechargement.
