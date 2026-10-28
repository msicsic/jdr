# Lot 255 — chronologie des observations partagées

**Branche `codex-sait-observations-c`, non fusionnée ; validation de fusion en attente.**
`origin/integration` **4318a5b** fusionnée sans rebase dans **5eac995**. Conflits
réunis : les deux entrées d'état et les deux tests distincts d'étapes sont conservés ;
`recevoir_statuts` du 254 conservé. Aucun changement de MJ, scénario, planificateur,
délibération ou `pnj.py` hors apports de cette fusion.

**Cause établie sur les bruts 250.** Les 46 avertissements redits sont concentrés
au hameau 1985 : à partir de 219, Brune annonce 79 cm dans la salle des vannes,
Aubin répond 79 cm « en hausse ». Capture **9371144**, rejouée jusqu'avant la
parole de Brune à 219 : Brune possède une estimation stable observée à **216**,
Aubin une hausse estimée à **211**. La co-perception existe déjà ; le suivi de
portée écrasait sans date les précisions successives, confondant aussi vitesse
inconnue et vitesse nulle. L'hypothèse d'une simple absence de co-perception
n'explique donc pas ces redites.

**Invariant corrigé :** une preuve partagée ne redevient pas nouvelle à cause
d'une estimation antérieure ; une précision absente n'efface pas une précision
établie. `social._retenir_information` date chaque composante de la portée
existante ; `_nouveau` compare cette chronologie. Parole et observation commune
utilisent ce même contrat ; aucune lecture nouvelle de l'esprit de l'auditeur.
`esprits.verifier` valide les dates sauvegardées ; direction inconnue représentée
par `None`, distincte de zéro. Un niveau seul ne rajeunit pas une direction privée.
L'oracle du point commun passe de `[1, 0]` à `[1, None]` : les assertions « vitesse
privée encore nouvelle » puis « décrue commune non nouvelle » restent intactes.

**Preuves :** capture hameau 219, trois minutes entières ou découpées en 12 laps,
monde, rendu, scène et mots enregistrés rechargés identiques ; au plus une mise
à jour stable licite, pas de riposte par l'ancienne estimation. Autre scène au
Relais : information partielle, date propre de chaque précision, vraie décrue
postérieure encore annoncée ; date invalide refusée. Les tests existants de
non-co-perception et de confidence utile restent dans la validation ciblée.
**83 tests distincts ciblés verts / neuf fichiers** : passe 82/82 en
67,439 s ; fichier complémentaire final 4/4 en 4,916 s, dont l’auditeur de dos. La passe initiale a aussi exercé
le fichier d’étapes fusionné (vert) ; pas de suite complète.

**Limites et suspects :** les cinq nouveaux signalements 219 du 250 ne démontrent
pas la même cause : Lucien/Mathe concernent achats et services de pain ; Aubin
hameau 1985 à 1–2 minutes recherche Gorm (première confidence d'eau à 70), Aubin
2024 à 113 perd puis retrouve sa localisation crue. La séquence 1985 a été capturée
par gestes et rejouée sur le moteur historique, sans reclasser le suspect.
Aucune correction de ces services/localisations ni garantie générale de boucle
n'est revendiquée. Les anciens suivis sans date ne reçoivent pas de date inventée.
Une information de même date et de contenu contradictoire n'est pas arbitrée ici.

**Mesures :** banc détaché 4 h, cinq scénarios × quatre graines, référence exacte
**4318a5b**, cache commun ; un travailleur réduit. Critères par nuit et mesures
référence → 250 → 255 à compléter après `fin.json`. Repère historique 250 contre
1194876 : confidences **34/72/38/53/58 → 26/54/19/48/122**, suspects **4 → 8**,
redites **0 → 46** (autre base, pas une attribution causale au seul delta 255).
Pas de suite complète ni Luna. Bruts :
`C:/Users/msics/donjon/artifacts/partagee-255/`.
