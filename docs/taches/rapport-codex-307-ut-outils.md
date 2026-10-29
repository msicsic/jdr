# Lot 307 — U-T outils et destinations

Branche `codex-ut-outils`, **non fusionnée**, base `d7302a4`, reprise sans
rebase de `43440c6` (305 inclus). Correction des offres après la suite
sur `9457ea5` ; vérification finale en cours.

## Invariant et changement

Un choix avec outil ou destination n'est proposé que si le moteur connaît
la capacité nécessaire au couple choisi. Le descripteur U-D conserve les
références exactes ; le moteur revalide l'accès, les droits et l'exécution.

`moyens_materiels.py` réunit les prédicats utilisés par l'arbitrage et les
formulaires : clé adaptée, outil de crochetage, impact ou coupe établie,
réserve de combustible compatible et contenant ouvert/dépôt dans une
source rechargeable. Impact et coupe utilisent `force`, les combustibles
utilisent `perception`. Les surfaces fixes ne sont pas des outils
manipulables. Les vérifications du moteur et du compilateur d'opérations
appellent ces mêmes prédicats ; aucune liste de verbes propre au terminal.

Chaque formulaire du catalogue nomme son aptitude. `ressources_publiques`
projette les références compatibles vers les seules cibles actuellement
vues ou portées, en excluant aussi les biens privés des PNJ. Web et
terminaux filtrent sur ces couples admis ; le web cache un sous-menu sans
candidat. La fabrication 305 garde ses formulaires et sa description
physique distincte. Aucune propriété inconnue n'est inventée pour rendre
un choix disponible ; une saisie explicite garde sa voie d'admission.

Les libellés terminaux affichent les désignations publiques, avec un rang
pour les homonymes, sans identifiant opaque ni coordonnées de carte. Le
numéro sélectionne toujours le descripteur exact figé, sans analyseur ni
modèle. Aucun changement du MJ ou des mécaniques PNJ.

## Vérification et mesures

Cas réel de la conduite, depuis la fixture `test_attendu_designable` :
**39 → 11 offres**, suppression des outils sans capacité, de `[personne_4]`
et des coordonnées. **3 touches** pour éteindre la lanterne. Second cas :
lampe à huile, remplissage avec le second combustible homonyme, monde,
scène, fiche et carte identiques à la boucle U-D après sauvegarde/recharge.
Les premiers tests de régression de la conduite et de `FormeTests` passent.

Validation finale détachée : interfaces/outils/inventaire, fabrication 305,
TUI existante, opérations, capacités, lumière et moteur à cases, nouveaux
cas de capacités, `test_attendu_designable` et `test_luna_restes.FormeTests`.
Syntaxe Node et callbacks réels de `tests/clic_page.js`. Aucun résultat
anticipé : fichier attendu `fin-correction-offres.json`.

Les tests vérifient les mauvaises ressources absentes des deux interfaces,
la matière incompatible, la réserve épuisée, la forme inconnue, la surface
fixe et un usage moteur modifié sans ajouter de verbe. Un choix capturé
avant fermeture, perte de capacité ou disparition reçoit toujours le refus
exact du moteur, sans substitution. Plans, textes et vues rechargés sont
comparés ; analyseur et appels du modèle interdits sur les choix directs.

## Limites et livraison

Une capacité connue ne garantit ni accès, ni accord, ni succès. Le moteur
ne définit toujours pas de capacité maximale des destinations. Le ciblage
par saisie reste disponible pour demander une admission physique distincte.
Ni Luna réel, ni banc PNJ, ni suite complète ; deux travailleurs réduits
au plus, sur copies hors du bac Windows. Bilans précédents conservés :
98 tests initiaux, puis 105 sur `958a5cc`, sans cumul avec la correction.
Bruts : `C:/Users/msics/donjon/artifacts/ut-outils-307/`.
