# Lot 328 — G6, repères de position

29 octobre 2026 — Lot clos, branche `codex-g6-reperes`, **non fusionnée**, base
`origin/codex-g5-perception c4cd83f` (lot 323). Aucune fusion d'intégration.

**Invariant porté.** La requête typée `reperer` consulte le repère public
courant ou mémorisé et fait écrire sa réponse par le moteur. Elle emploie
l'enveloppe d'action existante, disponible aussi en commande locale, sans
outil, jet, temps écoulé, effet physique ni rotation vers la cible.
`Moteur.executer` recompile le plan depuis sa proposition : ni une justification
inventée ni un texte de plan modifié ne fournissent une position.

`localisation.phrases_positions` formule les axes métriques et les demi-plans
du regard courant, avec une distance euclidienne approximative au décimètre.
Le capteur calcule `distance_metres` comme les axes, depuis la position perçue
ou mémorisée. Le souvenir est explicitement une dernière observation, jamais
une présence actuelle ; dans un autre lieu, seule sa salle connue est donnée.
Sans cases, aucune métrique n'est inventée. `rendu.position` lit la projection
publique, qui masque les noms inconnus ; faute de repère, la non-perception G5
ou un refus moteur répond, sans lecture de la position privée de la cible.

La voie des perceptions canoniques G5 exécute la requête sans contre-revue
d'action ni narration. Les phrases moteur rejoignent les attestations communes :
leur reprise exacte évite l'audit sémantique et est recalculée à l'enregistrement,
y compris si seule la distance a changé. Toute reformulation libre conserve
ses contrôles antérieurs. Publication et conversation utilisent la sauvegarde
existante avant affichage ; aucun registre de positions supplémentaire.

**Vérification locale : 162 tests distincts verts, quinze fichiers.** Le premier
passage (64,665 s) avait un seul échec : l'attendu exact d'un souvenir du test
d'orientation omettait le nouveau champ `distance_metres`. Ajout de la valeur
attendue 1,0, sans changement d'assertion ; les deux fichiers concernés repassent
ensuite **18/18**, 7,809 s. Dix nouveaux tests couvrent le mur du cas 171
(2 m nord, 3 m ouest), Aubin à 1 m, rotation, souvenirs d'objet et de personne
déplacés hors de vue, cible sans repère, identité inconnue, texte de plan
falsifié, reprise exacte périmée, mode sans cases et affaire portée dans le noir.
La vraie console, un MJ simulé sans réseau, l'état du monde, le texte, la scène
et la carte après recharge sont vérifiés ; le disque est relu pendant l'affichage.
Les premiers essais en bac Windows ont échoué sur l'accès aux dossiers temporaires ;
la validation ci-dessus est exécutée hors bac, deux travailleurs réduits au plus.

**Luna : une passe achevée**, `gpt-6-luna`, ChatGPT, medium, réflexion libre,
96,320 s écoulées, code 0. Deux processus réduits vérifiés au démarrage ; aucun
calcul actif. Vingt tours, dont quinze avec modèle, **43 appels**, zéro erreur
technique/recharge, repli ou mention sans fondement signalée par le banc.
Références historiques `c9459ce` déjà archivées par le 323, lues sans les rejouer :

| Script | Appels référence → branche | Résultat |
| --- | ---: | --- |
| atelier | 32 → 26 | 14 états observables comparables identiques ; premier état absent de la référence. |
| noms-dialogue | 13 → 17 | 5 états observables identiques, routage des paroles conservé. |

Dans les quinze premiers dossiers MJ comparables, noms connus et souvenirs
spatiaux identiques, hors ajout de `distance_metres`. Aucune relance ne refuse
un repère géométrique. Les cinq obstacles narratifs concernent la météo (deux),
une liste exclusive de visibles, des gestes inventés d'Aubin et « ouest » extrait
comme identifiant de source lumineuse. Le mur d'atelier reste en dialogue libre :
trois appels, dont un détail distant refusé puis un audit de la réponse corrigée.
**Aucune requête `reperer`, aucune reprise de position canonique dans cette passe.**
Luna ne démontre donc pas l'adoption de G6 ; la garantie des voies typées repose
sur les tests avec MJ simulé. Aucun gain d'appels attribué à G6, aucun temps
comparé à la référence historique de charge et de code différents.

Bruts `C:/Users/msics/donjon/artifacts/g6-328/` : `tests-cibles.json`,
`tests-reprise-contrat.json`, provenance et empreintes dans `references.json`
et `analyse-luna.json`, `fin-luna-passe.json` puis **`fin-cloture.json ok=true`**.
Code/tests inchangés depuis validation ; aucune seconde passe ni relance de tests.

**Limites et intégration.** Le moteur garantit les réponses typées et les reprises
exactes, pas le routage de toute question libre ni toute position implicitement
exprimée dans une prose française. Aucun audit de cette prose n'est retiré.
G6 typé est livré ; son adoption par Luna reste non démontrée sur les scripts prescrits.
Recouvrement avec 326/G17 et 327/G19 : `narration.py`, attestations et rappels à
conserver ensemble à la fusion. La base G5 reste non fusionnée. Ni suite complète
ni banc PNJ ; aucun changement de modèle ou de décision des PNJ.
