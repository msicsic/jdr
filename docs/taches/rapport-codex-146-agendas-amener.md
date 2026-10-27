# Lot 146 — accord de déplacement, prérequis d'amener

Branche `codex-agendas-amener`, non fusionnée ; code `b70e530`, base `cee0201` (brief récupéré par
avance rapide depuis `origin/integration`). **Livraison partielle autorisée par le
brief : la sorte `amener` reste à réaliser.** Aucun Luna, aucun fichier réservé au
lot 147, aucune sauvegarde utilisateur ni branche `main` modifiée.

## Invariant et réalisation

Une tâche qui demande à son auteur d'être dans un lieu doit être évaluée et exécutée
comme sa propre marche, sans le traiter comme un objet transportable. Le vocabulaire
commun validait déjà `{objet: auteur, lieu: destination}`, mais `_pulsion` produisait
le but et les gestes d'une prise/dépose. `planification._pulsion` vise désormais
`e.salle` pour cette condition, sans prendre ni poser le personnage. Le devis et
l'exécution de l'engagement partagent cette recherche. `deliberation.satisfaite`
lit sa position propre ; `echanges.tenu` reconnaît l'arrivée, même dans la minute
de l'accord et sans croyance sur soi. Pour un autre observateur, les croyances de
position restent nécessaires : pas de savoir de l'arrivée à distance.

`confier` reste la demande commune : accueil et persuasion inchangés, coût et route
jugés par le destinataire, engagement enregistré avant la réponse, marche choisie
ensuite par son planificateur en concurrence avec les besoins. Aucun ordre, seuil,
personnage ou lieu particulier ajouté au moteur.

## Vérification

Bruts : `artifacts/agendas-146/`. Deux calculs au plus, priorité réduite ; suite à
un processus pour cohabiter avec les autres lots. Les temporaires des tests ont
nécessité l'exécution autorisée hors bac à sable.

- 28 tests ciblés verts (déplacement, activation/socle des agendas, promesse tenable,
  tâches payées), puis 5 tests du nouveau fichier verts après ajout de deux gardes.
- Gorm demande une marche à Ilse vers la galerie et une autre à Brune vers l'échoppe :
  accord sans changement de salle, engagement puis marche et parole tenue. Même
  `data` et rendu après 3 minutes d'un bloc ou six demi-minutes avec recharges.
  Réponse « accepte » effectivement entendue, identique après rechargement
  (scènes avec voix connues, contrôle ajouté pendant la suite et repris par
  cinq ciblés verts ; aucun changement moteur après son lancement).
  Méfiance : aucun engagement ; destination crue noyée : refus avant engagement,
  pour les deux personnes. Arrivée propre dans la minute et absence de connaissance
  distante vérifiées après sauvegarde/rechargement réels.
- Empreintes 2 h Relais/mine/auberge × quatre graines : **12/12 identiques**,
  chronique, mesures et état complet. Douze références absentes calculées une fois
  et cachées ; aucune référence rejouée.
- Crue 4 h × quatre graines : **4/4 identiques**, état final complet, relevés,
  chronique, récit, souvenirs, mesures, boucles et constats. Zéro plantage,
  usurpation/violation ; mêmes constats historiques `voir_alterne` et `eau_longue`.
  Attente urgente moyenne **20 → 20 min**, eau **128,75 → 128,75 min**, maximum
  de passages horaires **13,25 → 13,25** ; Ilse/Brune à la galerie à 4 h
  **3/8 → 3/8**. Arrivée avant l'eau non démontrée. Quatre références manquantes
  cachées sans rejeu.
- Coût, crue 1985 fixe 4 h : **1 430 recherches**, **1 092 neuves** et
  **83 066 nœuds** de chaque côté ; CPU indicatif 20,64/20,86 s sur poste partagé,
  aucun gain de vitesse revendiqué. Les deux nuits ont été lancées une seule fois.
- Suite complète unique : **2 154 tests, 241 fichiers, 2 170,72 s**, deux
  échecs MiMo historiques `6 != 5`, zéro erreur. Les mêmes deux échecs sont
  reproduits sur la base intacte `cee0201` (13 tests, 10,99 s), sans seconde suite.

## Reste et limites

Ce lot ne réalise ni l'agenda d'évacuation ni sa preuve autonome. Restent tous les
sous-buts d'`amener` : choix du plus proche, préférence et avis commun, demande
autonome et refus retenu sans délai seul, accompagnement, atteinte et abandon sur
les croyances du porteur, puis données de la crue et épreuves correspondantes
(notamment faim désespérée et réveil après refus). Les tests de marche ne sont pas
présentés comme ces épreuves. Les limites A4a du lot 144 restent applicables.
Pas de clé de signature Git configurée : commits non signés, branche poussée seule.
