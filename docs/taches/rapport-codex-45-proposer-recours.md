# Lot 45 — Proposer faute de mieux (A2b)

Base **bafb9b9**, brief **9faf7b4** ; branche `codex-proposer-recours`, non fusionnée.
Code signé **2cb8220**. Aucun appel à Luna ni modification des quatre fichiers réservés au lot 44.

**Invariant et fonctions.** `deliberation.choisir` appelle `pnj_propositions.recours` après le
choix ordinaire : une offre avant la faute retenue, ou après une demande d'objet/part refusée
(`retenir_refus`). Aucune proposition développée par la recherche. Après l'offre, nouvelle
délibération ; `echanges.proposer` garde l'autorité sur le verdict, les remises et engagements.
Contreparties possédées et portées (objets/parts), pièces disponibles au plus au prix public.
Classement par coût propre/chance estimée, puis chance : lien du proposant, refus reçus,
prix publics et besoins observés, sans attitude privée de l'auditeur. Déclencheur et tentatives
sauvegardés par lésé/besoin ; seul un moyen cru nouveau, davantage de paiement ou un lien
amélioré relance. Le simple délai, une perte ou la réobservation ne suffisent pas.

Reprises du lot 36 : contreparties, `chance_proposition`, termes en mots, validation depuis
les connaissances du proposant et `Monde.adopter` (publication validée conservant les
références moteur). Contrat commun renforcé : une part remise s'attend auprès du receveur,
distinctement du service au lot, et toute réception conserve l'identité du lot. Sans cela,
le PNJ repartait chercher un autre moyen avant livraison. Récit/rendu par la parole perçue
commune ; mesures `propositions` et `acceptees` au banc.

**Vérification.** Six tests ciblés après recharge : Brune/Gorm en crue (pièces refusées puis
vol ; accord puis livraison sans vol), autre auditeur, Odon/Mathe (demande réellement refusée,
offre acceptée puis livraison), garde active sans seconde offre, même laps découpé/rechargé,
absence de réessai par délai et indépendance de l'attitude privée. Les 13 tests des marchés
du joueur passent. Les anciens tests isolent désormais leur effraction, voix ou ressource
plutôt que d'imposer une issue devenue négociable.

**Banc rapide**, quatre scénarios × 4 h × 1985/7/42/2024 contre `bafb9b9` : aucun plantage,
violation ou usurpation. Propositions/acceptées : Relais **1,25/1,25**, mine **4,25/1,75**,
auberge **2/0,75**, crue **3,25/0** ; vols tentés **1,5 → 0 / 0,5 → 0,25 / 0 → 0 / 2,25 → 2**.
Pas de boucle répétée nouvelle relevée ; crue 42 ajoute une seule alternance de buts de Gorm,
signal d'observation qui ne prouve pas une boucle.

**Temps sans cache**, versions lancées ensemble, 4 h, 42/1985, un processus par version : CPU
mine **9,391 → 9,203 s (−2,0 %)**, auberge **7,805 → 8,352 (+7,0 %)** ; ensemble **+2,1 %**.
**Le plafond +5 % par scénario n'est pas atteint à l'auberge.** Profil mine : recours 0,094 s,
exécution de dix offres 1,422 s sur 65,516 s ; actions/recherches supplémentaires dominantes.
La première mesure avant correction de l'attente donnait +11,2 % dans la mine.

**Suite complète finale**, trois processus à priorité réduite : **1 731 tests, 4 ignorés**,
614,3 s. Deux vérifications de scénario corrigées (Corvus placé sur Joss après huit heures ;
prêt rendu après le marché) : leurs deux fichiers repris en entier, **30 tests verts**.
**Bilan consolidé vert**, traces brutes conservées. Une première suite avait été lancée trop
tôt avant le correctif des parts remises ; le lot dépasse 45 minutes, vérification comprise.

**Limites / suite de 3e.** Pas de tâche promise en contrepartie, réparation de confiance,
intermédiaire ni négociation de passage. Le forcement visant un objet/une part se négocie pour
ce bien ; l'ouverture seule d'un bien fixe n'a pas de terme A2a. Une personne crue dans la
même salle est estimée joignable ; marche et parole réelles revalident contact/audition.
Valeur crue limitée au prix public et au besoin observé ; pas de surenchère en pièces.
Un outil acquis ou un accès nouvellement cru ouvert peut autoriser une nouvelle offre.
Traces non versionnées : `artifacts/recours-*`.
