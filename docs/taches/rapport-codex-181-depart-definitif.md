# Lot 181 — présence et fin de protection sur départ cru

Branche `codex-depart-definitif`, **non fusionnée**, base `integration 8c0cecd`.
Livraison partielle autorisée par le brief. Aucun Luna, fichier réservé au
lot 180 ou scénario historique modifié. Deux travailleurs de calcul réduits
au plus. Bruts exclusivement `C:/Users/msics/donjon/artifacts/depart-181/`.

**Invariant livré.** Une sortie déclarée `exterieur: true` termine la présence,
sans supprimer le personnage ni ses affaires. `presence.franchir` est appelée
par les deux marches communes, avec et sans cases ; elle enregistre l'état
et les preuves des témoins avant le récit. `Monde.present_physique`, positions,
occupation, lumière, vue et ouïe excluent aussi les biens emportés dans des
contenants. L'ordonnanceur retire immédiatement un PNJ qui part dans son laps.
Les caches perceptifs tiennent compte de cet état, joueur compris.
Le seul scénario modifié est `crue_hameau`, avec sa digue à l'est du refuge.

`etat.parti` est une preuve datée, distincte d'une position inconnue. Les
nouvelles communes la transmettent aux PNJ, sous leur règle de confiance et
de date. `agendas.actualiser` et la lecture des responsabilités terminent
`protéger` avec `protege cru parti`, publication différée, sans renaissance.
La vue au retour dément la croyance. Le placement d'auteur `presence.revenir`
réemploie le seuil enregistré, refuse un seuil occupé et reprend l'horloge
corporelle et les gestes à la date du retour. Le joueur quitte par le même
pas ; sa fin `depart`, son journal et le rendu de fin sont sauvegardés.

**Épreuves.** Ilse puis Brune partent devant leur protecteur ; une autre scène
transmet le départ depuis un témoin au protecteur resté loin. Ignorance sans
fin, cause et publication différée, biens, occupation, ouïe, retour sans
renaissance, temps entier/découpé, joueur avec/sans cases et digue déclarée.
État complet et rendu comparés après sauvegarde/rechargement.
**55 ciblés validés au terme des reprises**, dont les huit tests de départ
finaux verts (1,279 s). Suite complète unique : **2 287 tests, 263 fichiers,
1 334,188 s**, deux échecs MiMo historiques `6 != 5`, zéro erreur. Les deux
compléments ajoutés après le passage du fichier dans la suite et les reprises
finales de retour/nouvelle sont vérifiés en ciblés, sans deuxième suite.
L'épreuve de confidence passe par `social.bavarder`, réception et parole
communes ; son premier placement de rencontre était hors perception, corrigé.

**Empreintes.** 16/16 nuits historiques de 2 h, Relais/mine/auberge/crue ×
quatre graines : chronique, mesures, récit, souvenirs, empreintes physiques
et état complet identiques ; 16/16 mondes et rendus identiques après recharge.
Références finales du lot 179 exclusivement relues, aucune nuit de référence
rejouée. Le diff de `70bf000` à la base ne touche que les dossiers de
contre-revue hors partie passive et la documentation. Aucune comparaison des
temps issus du cache ni gain de vitesse revendiqué.

**Hameau, 4 h × quatre graines.** 4/4 nuits sans plantage ni usurpation,
aucune boucle signalée ; trois bascules isolées, passages horaires maximaux
20/27/20/28. Une observation `fige_presse` du devoir de Gorm (1985), pas une
nouvelle boucle établie. Quatre états/rendus identiques après recharge.
Aucun départ dans ces nuits passives : les scènes ciblées prouvent les
franchissements. Un travailleur de banc pendant le dernier fichier de suite,
puis les ciblés à un travailleur ; jamais plus de deux calculs simultanés.

**Limites.** L'invariant intégral reste ouvert pour l'adoption subjective des
nouvelles par le joueur : les paroles entendues sont conservées, sans modèle
de confiance ni jet d'adoption inventé. Le retour est un placement d'auteur,
pas un nouveau geste du MJ ; aucun choix autonome nouveau de départ n'est
ajouté. Le temps et les événements hors des lieux ne sont pas simulés.
Les sorties extérieures conservent un support géométrique réciproque dans
les données, sans monde extérieur simulé. A4b conserve ses autres restes :
suivi à portée de voix, interposition d'un lieu, ouï-dire des droits de garde.

Aucune clé Git de signature configurée : commit non signé. Ni fusion ni
modification de `main`.
