# Lots 117 et 117 b — Sens fermé des comptes du récit

26 octobre 2026 — branche `codex-comptes-recit`, **non fusionnée**, base
`6519588` ; code 117 b signé SSH **66fe151**, signature vérifiée.

**Cause et invariant.** Le dossier contient déjà les comptes publics du moteur,
mais l'ancienne extraction reconstruisait leurs rôles. Le lot 117 les remplace
par des références ; son seul jugement `restitue`/`contredit` laisse toutefois
passer une inversion réelle deux fois sur cinq. Le moteur doit comparer le sens
et la quantité attribués au texte, sans rôle libre réextrait de la prose.

**Changement 117 b.** `narration.schema_liens_comptes` demande pour chaque compte
un jugement, un sens parmi les deux orientations nommées par le moteur ou
`non_dit`, et un nombre ou `non_dite`. `sens_du_compte` construit les orientations
depuis les rôles et l'état du compte. `controler` compare sens et quantité :
inversion ou quantité différente refusées même sous `restitue`, sans contradiction
pour un champ non dit. Chaque refus identifie son champ, sa valeur reçue et
l'accepté ; les causes sens et quantité restent distinctes. Le jugement conserve
le contrôle sémantique des états et termes. Couverture de l'issue et relecture
canonique restent contrôlées ; anciens audits lisibles. Aucun rôle libre,
scénario, modèle, prompt narratif ou `echanges.py` modifié.

**Rejeu exact, cinq fois chacun**, même schéma fermé :

| Cas (passe 2, tour, audit) | Ancien / lot 117 / 117 b : refus sur 5 |
|---|---:|
| Crypte, 24, 2 : offre | 5 / 0 / **0** |
| Ambiance, 1, 1 | 4 / 0 / **0** |
| Soir-appel, 2, 4 : possession | 3 / 0 / **0** |
| Soir-appel, 2, 7 : inversion réelle | 5 / 3 / **5** |
| Soir-appel, 5, 7 : livraison future | 4 / 2 / **5** |

Le seuil demandé de quatre refus justes sur cinq est atteint. L'orientation
inverse est effectivement extraite dans les cinq audits de l'inversion.
Les trois faux refus surveillés restent absents. Le cinquième cas reste une
limite : jugements sur les termes et sur le geste introductif, malgré des sens
et quantités conformes ; aucune garantie sémantique générale. Le script
`comptes` conserve un repli sur Brune (association au compte inverse absent, états/termes et rappel).

**Console et recharge.** Gorm et Aubin : restitution admise sans relance,
inversion et quantité erronée refusées avant affichage même sous `restitue`,
paiement unique et conversation correcte après recharge. Brune reste débitrice ;
achat du soir et autre bien : pièces remises, bien encore dû, état et rendu
rechargés vérifiés. Liens conservés et recontrôlés, référence inconnue refusée.
**62 tests ciblés verts en 18,64 s**, puis **62 repris verts en 18,84 s**, six
fichiers, deux processus à priorité réduite. La suite complète unique du lot
117 reste : 2 035 tests, 16 ignorés, une erreur de générateur corrigée puis sept
tests repris verts ; aucune seconde suite complète, conformément à la reprise ciblée.

**Une passe Luna 117 b**, comptes / soir-appel / ressources / crypte,
référence 91a4351 à budget 200, quatre parties du cache, aucune rejouée :

| Ensemble, 18 tours MJ par variante | Référence → 117 b |
|---|---:|
| Appels / appels par tour | 71 / 3,944 → 69 / 3,833 |
| Relances / replis | 5 / 1 → 6 / 1 |
| Secondes par tour, moyenne / médiane | 14,024 / 12,690 → 20,495 / 18,735 |
| Obstacles narratifs | 11 → 60 |

Aucun arrêt, erreur technique ou défaut de recharge. **Aucun gain de délai** ;
le nombre d'obstacles augmente, y compris plusieurs refus pour un même segment.
Le seuil des cinq rejeux est acquis, pas une validation générale des faux refus.
Banc `artifacts/bancs-multi/20261026-081450-42584/` ; huit fichiers cachés
inchangés après la passe. Une seule passe ne sépare pas hasard et effet du lot.

**Historique 117.** Seize refus exacts rejoués : onze refus, cinq admissions.
Deux passes des quatre scripts : 149→129 appels, 13→6 relances, 2→1 replis,
14,723→15,335 s/tour ; validation alors refusée (inversion 3/5). Le 117 b
remplace ce candidat et satisfait le seuil ciblé, sans supprimer ses autres
limites sémantiques. Temps historiques et poste partagé : aucune causalité de
latence isolée. Bruts `artifacts/comptes-117/`, `rejeu-117b.json`, tests
`tests-117b-cibles.json` / `tests-117b-finaux.json` ; sources exactes et huit
parties cachées vérifiées par SHA-256. Un lancement initial avec budget 500,
arrêté après une partie de référence, est exclu et n'a pas modifié le cache 200.
