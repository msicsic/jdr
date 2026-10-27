# Revue 217 — Des décisions stables, mais pas encore une continuité d'intention

27 octobre 2026 — `codex-revue-vierge-decisions`, base exacte `817795918acc51d9ea0ab793e9fae1c0f7a7bf40` vérifiée. **Lecture seule du jeu** ; cinq nuits de 4 h, graine 1985, départ tiré : Relais, mine, auberge, crue, hameau. Un calcul à la fois, priorité réduite par `banc_pnj.ceder`, aucun Luna. Bruts : `C:/Users/msics/donjon/artifacts/revue-217/`, fichiers `<scenario>-1985.txt/json`.

**Limite de méthode autorisée après signalement :** `etat-dev.md` a été ouvert avant l'observation, suivant l'instruction générale du dépôt. Cette revue n'est donc pas vierge au sens strict. Les premières impressions ont ensuite été enregistrées dans `premieres-impressions.txt`, sur les nuits et le code, avant les plans et rapports prescrits. Ci-dessous, **O** signifie observation nouvelle, **C** lecture du code actuel, **H** historique lu ensuite ; les recommandations sont des inférences, pas des résultats mesurés.

## Ce que montrent les nuits

**O — Les personnages savent déjà tenir parole et trouver un autre interlocuteur.** Relais, min 12 : « Gorm appelle Brune et lui donne une part des vivres du refuge » ; min 13 : « Brune dit à Gorm avoir tenu sa parole », après son travail sur la torche. Crue, min 2–3 : Gorm refuse Brune par méfiance ; elle sollicite Aubin, qui accepte et lui donne une part à 3. Ce détour social est plus convaincant qu'une multiplication de gestes. Auberge, min 193 : Hugues « s'interpose et dit : “N'approche pas davantage.” », après l'offre de Lucien à Anselme, min 192. Un conflit peut ainsi exister sans violence.

**O — Toute immobilité n'est pas une panne.** Le récit attribue à Odile 171 minutes de charge déjà satisfaite ; Gorm en crue attend 148 minutes un moyen, avec des routes écartées pour l'eau. Ilse reste dans la lumière de 1 à 240 en crue. Ce dernier épisode paraît pauvre, mais sa longueur ne prouve ni entêtement ni recours oublié. **H —** Cela rejoint les contraintes justes du rapport 215 ; aucune raison de rétablir toutes les interactions anciennes.

**O — Toute fermeture suivie d'une réouverture n'est pas un caprice.** Mine, min 118 : Bram ouvre et referme son coffre, mais Lucien vient de nourrir Gaspard. L'aide peut légitimement cesser. À 191–193, Bram ouvre, ferme, rouvre puis finit par servir Josse : séquence suspecte, causalité non établie ici. **C —** `secours` exige une cible actuellement perçue pour proposer l'aide ; `choisir` ne conserve pas un engagement indépendant de cette génération. **H —** Le diagnostic 209 attribue des cas analogues à cette frontière. Il ne prouve pas la cause de mes nouveaux épisodes ; son avertissement contre « 57 retours = 57 défauts » est justifié.

**O + C — L'entêtement a parfois une allure d'horloge.** Mine : Odon vise 40 pièces à 0, 91 et 182, abandonne vers 30, 121 et 212. `_patienter`, `renoncer` et `choisir` imposent 30 minutes de patience puis 60 de répit, enregistré par motif. Cette cadence explique une partie de l'impression mécanique. Les événements intermédiaires empêchent d'affirmer qu'il reprend sans aucune information nouvelle.

**O + C — Un service réussi peut devenir absurde sans aucun retour de but.** Hameau, min 7 : « Brune […] allume la torche », puis « a fait le travail que Maël lui avait payé » ; min 8 : elle « éteint la torche », puis annonce sa parole tenue. `echanges.tenu` valide un résultat constaté ; `menager_flamme` économise ensuite une flamme devenue inutile à son propre plan. Ce n'est pas une preuve de mensonge : le contrat actuel peut être instantané. C'est une faiblesse de la définition du service utile, que stabiliser `choisir` ne résoudra pas.

**O — Richesse et agitation se mêlent.** Le hameau produit 315 gestes contre 95 en crue, avec promesses abandonnées et remboursées autour du repas de Brune, puis avis contradictoires et prises de parti à 206–229. Les 149 retournements au bruit du hameau contribuent aussi à l'agitation. Les cinq compteurs d'usurpation sont nuls : cela ne certifie pas l'absence de lecture indue. Davantage de gestes, de signatures ou moins de retours ne constitue pas, seul, une mesure de qualité.

## Compatible avec les décisions actuelles

**C + H — Garder l'architecture générale, simplifier son contrat.** Le planificateur choisit les moyens ; la délibération choisit le but ; les agendas portent les projets durables. Cette séparation reste utile. Le juge commun proposé en 196 est la bonne direction, sous deux évaluations distinctes : croyances pour décider, réalité pour exécuter. Partager une règle ne doit jamais partager la vérité cachée.

Je recommande un **engagement minimal porté par l'intention**, arbitré par `choisir` : identité du but et éventuel parent, condition de fin, préconditions crues, suspension temporaire nécessaire, cause de sortie. Naître, continuer, attendre et finir deviennent des opérations distinctes ; un plan vide ne signifie aucune de ces choses à lui seul. Ne pas transformer chaque secours en agenda ni ajouter une seconde pile de décisions. `esprits` conserve l'état nécessaire à la reprise ; les juges de famille interprètent les conditions ; le générateur propose des alternatives. L'abri possède déjà une partie de ce contrat.

Priorités proposées, effet attendu et coût qualitatifs :

| Priorité | Invariant général à établir | Effet attendu / coût |
|---|---|---|
| 1. Continuité et raisons de sortie | Un but engagé ne disparaît pas parce que sa condition de naissance cesse ; chaque interruption cite fin, démenti ou préemption, avec les faits pertinents. Les obligations suspendues restent attachées au plan. | Fort sur les secours et auto-interruptions ; coût élevé, à découper. |
| 2. Contact comme sous-but commun | Un besoin d'interaction sans localisation peut rechercher/appeler ; position inconnue ne signifie ni impossible ni localisé. Coût, danger et refus restent communs. | Fort sur les possibilités d'action ; coût moyen. |
| 3. Coordination observable de l'aide | Une aide annoncée et entendue peut éviter un doublon ; sa réussite ou son abandon se transmet par les voies ordinaires, jamais par l'intention privée du tiers. | Moins de démarches concurrentes ; coût moyen à élevé. |
| 4. Audit des transitions et des résultats | Une alerte distingue répétition, préemption légitime, progression et satisfaction par autrui ; elle examine aussi les dérives sans retour et le service effectivement obtenu. | Fort pour juger les prochains lots ; coût moyen. |

**C + H —** La priorité 2 retrouve indépendamment le raccord manquant de 215 : `rejoindre` sait chercher, mais `s_enquerir` et l'agenda d'information écartent une localisation absente. Aucun gain chiffré n'en découle. **H —** Le rapport 210 contredit l'idée que réduire la réflexion suffirait : moins de nœuds, mais des plans perdus et davantage d'attente. Habitudes et saillance ajouteraient des conditions d'invalidation avant que celles de l'intention soient maîtrisées ; ce ne sont pas aujourd'hui une architecture plus simple.

## Remettrait une décision en cause

**H + C — Proposition 196, § 4.1 :** je déconseille de majorer automatiquement l'inertie du trajet *déjà parcouru*. Ce coût passé peut produire de l'obstination et n'est pas directement comparable aux points d'urgence. Préférer le coût futur de bascule, avec la ténacité VOL décidée au § 10 du plan des agendas. C'est une réserve sur la proposition 196, pas un rejet de cette décision utilisateur.

**C — Règle actuelle des 30/60 minutes :** remplacer le répit global par motif par un réessai lié à l'obstacle cru remettrait cette mécanique en cause. Invariant visé : le même obstacle n'est pas oublié par délai, et un recours nouveau n'est pas interdit par l'échec d'un autre. Effet plausible sur Odon, coût moyen ; ne pas supprimer les attentes temporelles légitimes.

**O + C — Services instantanés :** distinguer explicitement « obtenir cet état » et « le maintenir jusqu'à telle fin » changerait le contrat de tâche actuel. Invariant : réussite, prix et obligations postérieures portent la même durée. Effet fort sur la crédibilité, coût élevé. Aucun interdit spécial d'éteindre une torche n'est recommandé.

**H — Utilité unique :** supprimer les paliers au profit d'un score entièrement compensable remettrait en cause les priorités absolues de la décision 2 du plan des agendas. Je ne le recommande pas. Ni les nuits ni le code ne justifient de déplacer l'autorité vers Luna ou d'abandonner les croyances privées.

## Ce qui n'est pas vérifié

Cinq nuits d'une seule graine, joueur passif, sans comparaison de versions ni détecteur 199 relancé. Pas de capture causale intermédiaire, de rechargement monde/rendu, de laps découpé, de suite de tests ou de Luna : cette revue ne valide aucun correctif et ne garantit aucune absence générale de boucle. Les chiffres des rapports historiques restent ceux de leurs bases. Les résumés comportent des intervalles inversés (`12–11`) : les citations datées ci-dessus suivent la chronique, pas ces bornes. Bruts et premières impressions sont conservés ; seuls ce rapport et une ligne du point de reprise sont livrés.
