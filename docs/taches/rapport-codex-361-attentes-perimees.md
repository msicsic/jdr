# Lot 361 — attentes périmées

Branche `codex-attentes-perimees`, base `integration 0b62a4fa`, 30 octobre 2026.
Lot terminé, non fusionné ; branche poussée vers origin, aucun calcul actif.

**Invariant.** Porter les seules prémisses et formes devenues périmées, sans
changer les garanties de sécurité, d'état et de reprise. Aucun fichier du jeu
modifié. Les preuves viennent de l'[attribution 356](attribution-codex-356-suite-rouge.md)
et des rapports d'origine, cités au droit des adaptations.

- [G5 / 323](rapport-codex-323-g5-perception.md) : `regarder` ajoute sa réponse
  exacte à la conversation attendue, sans enlever de champ à l'égalité du monde.
  Le harnais WebSocket partagé couvre crypte et atelier, fournisseurs et reprises.
  Les non-perceptions contrôlent maintenant le constat, sa sauvegarde avant
  affichage, l'absence d'effet et la recharge. La fouille ne réclame plus une
  contre-revue de perception seule ; le test d'avis après contre-revue propose
  un geste physique infidèle pour continuer d'exercer ce contrôle.
- [G16 / 345](rapport-codex-345-g16-information-parlee.md) : paroles directes
  du moteur, croyance datée observée dans la préparation réelle, ressources
  conservées avec la comptabilité. Les désignations libres sont exercées au
  tour suivant la même imposture, avec toutes leurs assertions initiales.
  Le rappel altère effectivement « Ilse. », sans dépendre d'une suite supprimée.
- [U-C / 325](rapport-codex-325-uc-consentement.md) : les cinq méthodes adaptées attendent
  la nouvelle mention de faisabilité ; aucune confirmation automatique d'une
  consultation ni assertion de non-exécution retirée.
- [G6 / 328](rapport-codex-328-g6-reperes.md) : distance métrique ajoutée au
  dictionnaire exact du souvenir ; [G7 / 343](rapport-codex-343-g7-deplacements.md) :
  mouvement mesuré et durée remplacent l'ancienne formule du pas feutré.

**Contrôle AST.** Sur les vingt fichiers existants modifiés : 872 assertions
initiales, **846 identiques**, 26 substitutions documentées et 32 nouvelles
formes/assertions, soit 878 finales. La liste explicite relue des exceptions
est comparée aux AST ; code du jeu et fichiers réservés au 360 contrôlés intacts.
`controle-ast.json` est vert ; détails et scripts dans les bruts.

**Mesures.** **31 méthodes portées sans incident**, contrôlées dans les
**190 tests / 21 fichiers entiers**, 370,690 s, deux travailleurs réduits :
19 fichiers verts, deux échecs antérieurs, zéro erreur ou saut. Préfixe KV :
ratio 0,819771819 contre > 0,85 ; scène N9 : zéro revue au lieu d'une. Mêmes
assertions et valeurs que `f014c80`, méthodes AST inchangées : aucune preuve
de changement voulu, donc aucun portage de ces régressions. La première
passe ciblée (111,362 s) garde une attente de titre public corrigée ensuite.
`jsonschema` déclaré installé dans les seuls artifacts ; les essais invalides
du bac à sable et ceux sans dépendance restent archivés et ne valent pas validation.
Ni suite complète, Luna, banc ni sauvegarde de partie de l'utilisateur utilisés.

**Réserve de périmètre.** La 32e méthode, `test_passage.DemanderLePassageTests.
test_cas_reel_acceptee_elle_s_ecarte_vraiment`, partage un fichier interdit
par le brief (`regressions-337.txt`) : aucune modification de `test_passage.py`.
Son attente « Tu avances d'un pas. » est également périmée depuis G7 : le rendu
actuel indique un pas vers ouest en 1,5 seconde. Proposition non appliquée
`passage-reserve.patch` dans les bruts, pour le 360 ou la fusion.
La suite globale n'est pas déclarée verte.

Bruts : `C:/Users/msics/donjon/artifacts/attentes-perimees-361/`.
