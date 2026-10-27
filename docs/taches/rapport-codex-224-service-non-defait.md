# Lot 224 — Ne pas défaire le résultat d'une parole de service

Branche `codex-service-non-defait`, **non fusionnée**, base `a22f92e` vérifiée.
Code `456ff6a`, sans signature : aucune clé configurée. Aucun Luna, aucun
fichier des lots voisins modifié hors du filtre commun et de ses entrées.
Bruts : `C:/Users/msics/donjon/artifacts/service-224/`.

**Invariant et approximation décidée pendant le lot.** Le prestataire ne défait
pas un résultat promis tant qu'il croit le bénéficiaire auprès de ce résultat
ou porteur de l'objet. Le lieu et l'état viennent de ses croyances existantes,
jamais des besoins, des pulsions ou de l'intention privés du bénéficiaire.
Un départ cru ou un état constaté défait termine la protection, sans délai ;
l'absence de nouvelle information ne dément pas la parole reçue. Un bénéficiaire
présent qui n'en a plus besoin reste protégé. Aucun entretien n'est exigé après
réussite. Le vocabulaire est celui des tâches existantes : flamme allumée,
installation fermée à clé, objet en un lieu ; aucun nouveau type de tâche.

**Contrat commun.** `echanges.tenu` retient le résultat lorsqu'il constate une
parole effectivement en cours, avant sa clôture. `biens.retenir_service` conserve
qui, pour qui et quelle condition dans `services_rendus`, validé par `biens.verifier`
et sauvegardé hors de la mémoire bornée. `biens.services_proteges` réunit ces traces
et les engagements ouverts : un résultat obtenu avant son constat de clôture
est également protégé. `planification._normaliser_suites` filtre les transitions
qui passent de l'état obtenu à l'état défait, après les approches et les effets
des portes franchies ; suites différées comprises. Les gestes nécessaires pour
obtenir le résultat restent offerts. La nouvelle entrée dans `_entrees_communes`
empêche la reprise d'un ancien plan ou certificat ignorant ce filtre.
`deliberation.menager_flamme` lit la même protection. Aucun changement dans
`choisir`, `s_enquerir`, `reagir`, `agendas.py`, `esprits.py`, `social.py` ou le MJ.

**Cas réel et tests.** Avant correction, avec le placement initial du joueur,
hameau 1985 reproduit exactement l'allumage de Brune à **4584 (7 min)** et
l'extinction à **4824 (8 min)** ; monde, `regarder` et `scene_percue` rechargés
identiques. La reprise corrigée de la capture réelle à 4584 conserve la flamme
jusqu'à 10 min ; même monde et mêmes rendus après recharge, même laps en bloc
ou découpé. Départ réel non appris sans effet ; départ cru libérant l'extinction.
Autres scènes : serrure d'auberge promise à Odile ou payée par le joueur,
ouverture par un trajet, clé posée pour autrui, éviction du souvenir, état défait
par autrui et combustible épuisé sans nouvelle dette ni parole rouverte.

**Mesures finales : en cours.** Banc 4 h, cinq scénarios × quatre graines,
compteur 219, coût mine 4 h et suite complète unique à deux travailleurs réduits.
La branche locale `main` est ancienne ; référence correcte `origin/main`,
`395834b`, dont le code est identique à la base du lot. Ses nuits calculées
une fois sont réutilisées, sans comparer leurs temps CPU aux nouveaux temps.

**Limites.** La règle suit les observations, donc une présence ou un départ crus
à tort peuvent protéger ou libérer à tort. Aucun message typé existant ne libère
spécifiquement ces états. Les anciennes paroles déjà clôturées sans trace ne
sont pas reconstruites depuis des souvenirs éventuellement évincés. Le compteur
219 inclut aussi les pertes par combustible épuisé ou par d'autres personnages ;
une telle perte n'est pas à elle seule un manquement du prestataire.
