# Lot 146 b — candidats sans mutation ; fin d'amener partielle

Branche `codex-agendas-amener-b`, non fusionnée ; base `b5a23bb`, code `36e1b33`
puis `268e190` (complément prioritaire du lot 148 reçu pendant le lot).
Le brief absent a été récupéré par `fetch` puis avance rapide. Aucun Luna, aucun
fichier MJ réservé, aucune sauvegarde utilisateur ni branche `main` modifiés.

## Invariant et changement

Évaluer un candidat ne modifie ni le monde ni l'esprit. `agendas.evaluation`
prépare les états et chroniques hors de `data` ; `vues_du_choix` les publie après
le contrôle de lecture seule d'un choix complet, comme les efforts bornés du lot 87.
`choisir` inclut désormais l'activation dans cette frontière ; `_candidats` ne
l'active plus. `planifier` isolé ne publie rien. Un choix interrompu jette aussi
les propositions imbriquées. Confirmation explicite reçue : un agenda essayé
sans plan s'endort à la sortie du choix, même si un autre candidat fournit le plan.

Un projet visant l'arrivée d'autrui se termine sur ce que son porteur croit,
jamais sur la position réelle d'une personne distante. `agendas.actualiser`
reconnaît `amener` : toutes les personnes crues dans le lieu donnent `atteint`,
avec la raison `arrivee crue`. Sinon, une destination crue ou attendue noyée donne
`abandonne`, avec sa cause. États et causes sont sauvegardés ; un état terminal ne
renaît pas. Les autres projets `amener` dorment explicitement, sans candidat,
demande ni déplacement artificiel. Aucune déclaration ajoutée à la crue.

La correction d'intégration est prioritaire ; la livraison d'`amener` reste
limitée à ce cycle de fin. Les avis actuels concernent la menace d'eau : aucune
préférence générale entre lieux n'est prétendue réalisée par ce traitement.

## Vérification

Bruts dans `artifacts/agendas-146b/`. Deux calculs au plus, priorité réduite.
Les sauvegardes temporaires des tests ont nécessité l'exécution hors bac à sable.

- **31 tests ciblés verts**, six fichiers, dont huit nouveaux tests. Le nouveau
  test du premier choix crue 42 échoue sur la base intacte avec l'assertion signalée.
  Devis, interruption, imbrication et publication différée contrôlés. Gorm,
  Ilse/galerie et Brune/échoppe : arrivée réelle sans connaissance distante,
  puis croyance vue ou dite ; les deux personnes doivent être crues arrivées.
  Destination réelle sèche mais crue noyée : abandon pour les deux personnes.
  Non-renaissance, absence d'engagement ou de transport, état complet et rendu
  après sauvegarde/rechargement ; même laps de trois minutes entier ou découpé.
  Les croyances sont installées par les tests : ce ne sont pas des épreuves
  d'évacuation ni de production autonome des paroles.
- Crue 42 fixe/tirée, **2 h avec `VERIFIER` et `spatial.VERIFICATION` 0,2** :
  aucun arrêt ; état complet, chronique, mesures, récit et souvenirs identiques
  à la base non vérifiée. Deux références manquantes cachées, aucun rejeu de nuit.
- **12/12 empreintes 2 h identiques**, Relais/mine/auberge, quatre graines.
  **4/4 crues 4 h identiques** en état complet ; zéro plantage, usurpation ou
  violation, aucune boucle nouvelle ; mêmes constats `voir_alterne`/`eau_longue`.
  Attente urgente 20 min, eau 128,75 min, maximum de passages horaires 13,25,
  Ilse/Brune à la galerie en fin de nuit 3/8 : inchangés. Seize références
  manquantes cachées une fois. Aucun gain d'évacuation ni de vitesse revendiqué.
- Coût crue 1985 fixe 4 h : **1 430 recherches, 1 092 neuves, 83 066 nœuds**
  de chaque côté ; CPU indicatif 21,28/20,89 s sur poste partagé.
- Suite complète finale : **2 168 tests, 244 fichiers, 1 192,24 s**, deux échecs
  MiMo historiques `6 != 5`, zéro erreur ni ignoré. Les deux sont reproduits
  seuls sur la base intacte `b5a23bb` (deux tests, zéro erreur). Première suite
  interrompue à l'arrivée du complément prioritaire ; une seule suite complète
  achevée, sur le code final. Aucun code modifié depuis les ciblés et les bancs.

## Reste et limites

**Amener n'est pas réalisé dans son ensemble.** Restent la préférence générale
et son avis, le plus proche à égalité par identifiant, la portée vocale, la demande
autonome `confier`, le refus durable et son réveil, l'accompagnement, l'abandon
pour route crue coupée, les données de la crue et la preuve d'évacuation successive
avec priorité du désespoir. Une route immédiate absente ne prouve pas qu'aucun plan
ne peut trouver une clé ou ouvrir un passage. Aucun résultat de ce lot ne prouve
l'arrivée avant l'eau. Les limites A4a des lots 144 et 146 restent applicables.
Pas de clé de signature Git configurée : commits non signés, branche seule poussée.
