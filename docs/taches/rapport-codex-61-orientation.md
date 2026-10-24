# Lot 61 — Repères dans le regard courant

Branche `codex-orientation`, non fusionnée ; brief `1008f21`, intégration de
`origin/integration` `04bca30` au début du lot. Aucun changement de `main`.

Le défaut était une localisation relative admise d'après un souvenir sans tenir compte
du demi-tour de Corvus. `localisation._ecart` fournit maintenant l'écart commun des
distances et des directions ; `orientation_relative` le projette dans le regard courant
(produit scalaire avant/arrière, déterminant gauche/droite). `decrire` fournit ces
demi-plans pour les objets perçus ; `Monde.contexte` les recalcule sur la dernière position
mémorisée, sans lire la position cachée d'un personnage. Aucune direction relative n'est
figée dans la sauvegarde ; `vu_a` reste en mètres.

`narration.orientations`, appelé par `controler`, compare les locatifs explicites aux
repères publics, indépendamment du classement et des sources de l'auditeur. Il donne un
refus par locatif, avec segment, mots reçus, référence, directions admises et repère
absolu. Sans cible univoque, ou avec négation, il demande une reformulation absolue.
`reperes_demandes` relie une réponse pronominale à la cible publique unique de la demande.
`consigner` refait le contrôle avec le regard courant avant toute écriture. Les répliques
citées restent libres. « refus » est ajouté au garde existant de voix d'auteur ; aucun
nouveau mode, aucune donnée de scénario ni exception liée à une entité.

Vérification : dix tests nouveaux dans `test_orientation_narrative`, dont le cas réel
de la poutre et Ilse vue de face puis dans le dos, vraie console/MJ simulé, sauvegarde et
rechargement, texte refusé absent de la sortie et de la conversation, texte accepté
persistant, orientation/position et objets conservés. Gauche/droite sont aussi rejouées
dans la console ; l'absolu reste admis. Huit regards (et leurs alias), demi-plans latéraux,
verdict trompeur de l'auditeur, cible ambiguë, négation, citation et déplacement caché
sont contrôlés. 49 tests ciblés verts, puis 109 tests des huit fichiers concernés et les
dix tests finaux verts. Deux formulations de méta-refus sont aussi corrigées dans la console
et absentes de la sauvegarde rechargée.

Empreintes : Relais, 2 h, graines 1985/7/42/2024, contre l'intégration `04bca30` :
**chronique, mesures et état final complet identiques** nuit par nuit. Référence calculée
une fois et rangée dans le cache partagé. Bruts : `artifacts/orientation-empreintes.json`.

Suite complète unique (`tools/tests.py --processus 3`, priorité réduite) : **1 815 tests,
16 ignorés, aucun échec ni erreur**, 1 304,7 s. Les dernières retouches révélées par Luna
sont aussi couvertes par la reprise ciblée ci-dessus. Bruts : `artifacts/orientation-tests.json`.

Luna, **une passe**, trois scripts prescrits : 59 appels, 22 tours MJ, aucun repli ni erreur
technique/recharge. Appels/tour, première partie `main` archivée → branche : ambiance
4,00 → 2,67 ; Relais 3,00 → 2,50 ; atelier 3,91 → 2,82. Les temps archivés ne mesurent pas
le gain de ce lot. Le lanceur a tenté une référence non reconnue puis échoué sur l'import
`agendas` absent de `main` ; aucune seconde tentative. Comparaison relue directement dans
le cache de `42bb9c0` (scripts identiques, ancien lanceur et budget 200 contre 500, jamais atteint).
Sur l'orientation, « Tu l’avais vue […] derrière toi » a subi un **faux refus pronominal** ;
la réponse affichée donne l'absolu sans direction fausse. Le lien avec la demande, corrigé
ensuite, est rejoué avec MJ simulé pour la poutre et Ilse ; **pas de seconde passe Luna**.
Relais n° 22 : « Tu ne vois aucun pied-de-biche ici […] », sans commentaire sur un refus.
Atelier : repères absolus, aucun obstacle narratif. Bruts et textes affichés :
`artifacts/bancs-multi/20261025-003353-35432/`, `artifacts/orientation-luna-relecture.txt`,
`artifacts/orientation-luna-mesures.json`.

**Limites** : le contrôle géométrique est déterministe pour les locatifs reconnus ; il ne
garantit pas l'invariant sur toute prose française. Les directions implicites, la portée
temporelle et les pronoms restent en partie sémantiques. Le garde peut demander un repère
absolu à une phrase pourtant correcte avec plusieurs cibles ou une négation. Un souvenir
reprojeté ne prouve jamais une présence actuelle. Aucun changement du modèle Luna ni de
la comparaison des modèles, de `planification.py` ou d'`appel.py`.
