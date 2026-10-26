# Rapport Codex 134 — traîner un corps

Branche `codex-trainer`, **non fusionnée**, base `bb31eb5`. Aucun appel à Luna,
aucune modification des fichiers réservés aux lots 132/133. Python du dépôt principal,
deux processus de calcul au plus, priorité réduite. Aucune clé Git de signature configurée.

**Invariant** : `tenir.valider_trajet` vérifie pour le joueur et les PNJ le contact,
la conscience de l'auteur, ses mains libres, une cible inconsciente/ligotée/rendue ou
une dépouille, et deux pas physiques admissibles. La cible rejoint la case quittée par
l'auteur ; l'arrivée de celui-ci doit être libre. Les portes et obstacles passent par
`spatial.pas_vers`, l'eau par `eau.refuser_entree`. Chaque refus expose son `attendu` au MJ.
`tenir.commencer` enregistre les positions initiales et la direction dans l'issue du
registre commun ; `finir_trajet`, appelé par `pnj.finir_gestes`, revalide avant toute
mutation. Un changement de place, un réveil sans autre entrave, un coup ou l'inconscience
empêche le déplacement. L'allure de 4,5 s (6,4 s en diagonale, `temps.duree_pas`)
et la rotation précèdent l'effet.

Le moteur et la commande locale `traîner <corps> vers <direction>` utilisent ce contrat.
Le regard suit le pas ; le corps au contact derrière reste ciblable. Le rendu et le journal
ne donnent le déplacement pour acquis qu'après l'issue. Les lieux visités et les perceptions
sont actualisés. Le contact commun accepte désormais les dépouilles. Une personne vivante
passe par les témoins, souvenirs et relations communs ; une dépouille ne crée aucune
contrainte. Le vocabulaire de `social.GESTES` permet de raconter ce souvenir. Un geste de
contrainte sans coup ne rompt plus à lui seul la reddition. Aucun choix autonome ajouté.

Le test de découpage a exposé un défaut commun : l'éveil passé d'un témoin encore occupé
était repoussé à chaque reprise de l'horloge. `pnj._avancer` ne le décale désormais que
si le personnage peut effectivement reprendre au début du laps. L'état complet et le rendu
du même geste concordent après rechargements intermédiaires, y compris avec témoins actifs.

**Vérifications** : reprise finale **37 tests ciblés verts**, trois fichiers, un processus
réduit, **7,11 s** ; eau, obstacle, auteur retenu et durée diagonale inclus.
Suite complète unique : **2 082 tests, 228 fichiers, deux échecs MiMo `6 != 5`, zéro
erreur**, **1 101,90 s**, deux processus réduits. Les mêmes deux échecs sont reproduits
sur l'archive intacte de `bb31eb5` (13 tests, 10,05 s). La suite n'est donc pas entièrement
verte ; aucun échec nouveau établi, aucune seconde suite complète.
Scènes : Brune inconsciente au vrai Relais, quatre cases jusqu'à une autre salle avec
témoin ; dépouille ; Joss ligoté à l'auberge et seuil du cellier ; joueur et PNJ ; refus
conscient libre, arrivée occupée, porte fermée, mains prises ; réveil, coup, inconscience,
changement de place ; reddition et rotation ; positions, mémoire et rendu rechargés.
Le rendu d'une victime derrière le joueur est vérifié après retournement, sans fuite de vue.

Banc rapide **4 h × Relais/rixe × 1985/7/42/2024 : 8/8 identiques** à la base : état final,
empreintes 5/60/120/240 min et issue, chroniques, mesures et boucles. Zéro plantage,
usurpation ou violation ; six observations `fige_presse` historiques de chaque côté.
Référence absente du cache : huit nuits jouées une fois puis rangées. Pas de comparaison
de performance sur ce poste partagé. Banc avant les derniers compléments propres à
`trainer` (lieux visités, rendu PNJ, auteur retenu, durée diagonale), exercés par la suite
ou la reprise ciblée finale.
Bruts : `artifacts/trainer-134/` (`banc.json`, `identites.json`, `cibles-finaux.json`,
`suite.json`, `base-mimo.json`).

**Limites** : mains libres signifie aucun objet mobile directement porté, sans nouveau
système d'équipement ; le contenu d'un contenant reste porté via celui-ci. Traîner n'est
pas porter. Aucun choix autonome ni secours par déplacement, aucune garantie narrative
Luna supplémentaire. Enfermer, forcer les portes et captivité prolongée restent hors lot.

Livraison : commit non signé (aucune clé configurée), branche poussée ; ni fusion ni
modification de `main` ou d'`integration`.
