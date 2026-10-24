# Lot 29 — Propositions du joueur (A2a)

Base : `450cebb` (brief, intégration `19b0261`). Branche `codex-propositions`, non fusionnée.
Code signé SSH : `65032f5`, `7595dc7`, `a880ca8` ; signatures vérifiées.

**Invariant et réalisation.** Une offre lie sa demande à sa contrepartie ; le moteur tranche
avant affichage, puis applique remises et promesses sur copie. `propositions.py` décrit et
contrôle l'union typée ; `paroles` la transmet comme une idée indivisible, à un seul auditeur.
`echanges.evaluer_proposition` calcule P/G/L : valeur propre des biens/pièces, devis fondé sur
les croyances pour une tâche, confiance sur une promesse, altruisme/affection/dette-loyauté/rancune,
puis persuasion et protection par l'INT contre un mauvais marché. Chaque refus dit une cause.
`proposer` inscrit les cessions, parts prélevées et engagements ; une réserve gardée ne se cède
pas. Une part ne cède pas le lot dont un devoir impose le lieu. Le prélèvement utilise le
compteur de la ressource (portions alimentaires ou charges).

`agendas` reste le seul accès aux engagements, y compris ceux du joueur, créés à la première
offre acceptée. Un effet réel du moteur doit réaliser la condition ; l'observation par le
bénéficiaire permet ensuite `engagement_tenu`. Attendre devant un état déjà vrai ne tient pas
une promesse. Après 240 minutes, l'abandon est éprouvé quand les deux peuvent se parler, sans
connaissance à distance. Fiche, contexte et journal restent lisibles après recharge. Une même
promesse ne reçoit pas deux contreparties.

**Nombres retenus.** DD 12 ; pas de 5 minutes de valeur propre par point de persuasion ;
protection d'INT à partir de 8 ; prix conventionnel d'un objet non chiffré : 1 pièce. Les poids
du lien suivent § 7.1, sans recompter ceux du jet historique. Une tâche offerte ne vaut que le
devis évité pour une pulsion/un engagement de l'auditeur, × confiance/100 ; une quantité cachée
de réserve offerte n'est pas lue (une part évaluée sans prix total). Ces nombres sont un
point de départ, aucune calibration d'équilibre n'est revendiquée.

**Vérification.** Tests ciblés : marchés acceptés/refusés en console avec MJ simulé, deux
auditeurs, même jet et INT différente, réserves nécessaires/gardées, formes invalides avec
`attendu`, confiance, double paiement, tâches réalisées par le moteur, sauvegarde/recharge et
textes persistés. Bilan ciblé final consolidé : 39 tests verts, un saut (`jsonschema` facultatif).
Empreintes de 2 h, Relais/mine/auberge × 1985/7/42/2024 : **12/12 identiques**, chronique,
mesures et état final complet contre `19b0261`. Les douze références venaient du cache ;
leurs temps ne sont pas comparés. Suite complète unique, trois processus à priorité réduite :
**1 672 tests, 16 ignorés, bilan consolidé vert**, 2 534,6 s (42 min 15 s).
La suite a été lancée trop tôt : deux fichiers ont chargé un import transitoire manquant ;
leurs seules reprises sur le moteur final sont vertes (32 tests, 20,5 s). Les 12 erreurs de
la première exécution sont toutes dans ces fichiers ; aucun échec restant. Le lot dépasse
45 minutes : sans historique des durées dans ce worktree, la mine a été planifiée tard.

Luna, **une seule passe**, cinq saisies, copies temporaires, priorité réduite : **17 appels,
3,4/tour, 19,4 s/tour**, aucun repli, erreur, mention sans fondement ni recharge invalide.
Cloche contre part et offre à Brune méfiante : `proposition` dès le premier appel, issues
conformes. Mauvais marché : part typée à tort au lieu du lot, contre-revue puis réponse sans
transfert (5 appels). Tâche promise : conversation ordinaire ; formulation libre : `propos`.
**Le typage spontané des tâches et l'absence générale d'issue inventée ne sont donc pas prouvés**.
Les engagements typés sont vérifiés sans modèle ; aucune seconde passe n'a été lancée.

**Limites et périmètre.** Les anciennes demandes restent distinctes : vente au prix sans jet,
prêt d'objet durable, service alimentaire au lieu de cession. Leur conversion modifierait les
nuits PNJ ; elle attend le lot où ils proposent. Tâches limitées au vocabulaire existant
allumé/verrouillé/objet en salle ; remises matérielles au contact. Le joueur promet un résultat,
pas un maintien continu. Aucun geste PNJ nouveau, intermédiaire, avis ni fichier réservé au
lot 28 modifié. Traces : `artifacts/propositions-empreintes.json`, `propositions-tests.*`,
`propositions-validation-consolidee.json`, reprises ciblées et `luna-propositions/*` (non versionnés).
