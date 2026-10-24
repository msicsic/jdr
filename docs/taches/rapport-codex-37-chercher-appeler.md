# Lot 37 — chercher en appelant sans recommencer sa tournée

Branche `codex-chercher-appeler`, non fusionnée, base `da13f9d` ; correctif signé SSH
`222f3cf`. Sans Luna, priorité réduite, quatre processus de calcul au plus ; suite à trois.

**Invariant et cause.** Chaque personne cherchée possède ses lieux déjà parcourus en vain.
Ils restent écartés jusqu'à un nouvel indice local. Le rejeu de la crue 3 à 120 reproduit
les dix appels de Brune : voir Gorm, puis constater son absence, réactivait toutes les
salles cherchées avant cette croyance. L'expiration après 60 minutes permettait aussi
de recommencer sans information ; les trajets rapides exposaient le défaut.

**Contrat commun.** `deliberation.appels_vains` lit désormais le registre persistant sans
filtre de minute. `indice_recherche` rouvre uniquement le lieu indiqué : pour la personne
identifiée par `esprits.croire` (vue, voix, bruit attribué, nouvelle), ou pour les personnes
cherchées si `ouie._bruit_inconnu` retient un bruit nouveau sans auteur identifié. Un bruit
déjà attendu ou couvert ne réarme rien ; aucun auteur n'est inventé. Une absence ne rouvre
rien, même dans la minute de l'appel. Les souvenirs ne migrent qu'en l'absence du registre :
recharger ne réinjecte plus des échecs levés. Même règle pour le joueur cherché.
`planification.py`, les scénarios, besoins et réponses négociées restent inchangés ; la clé
existante comprend déjà les lieux écartés. L'audit abandonne la justification par le délai.

**Preuves.** Six tests nouveaux, avec scènes enregistrées de la crue 3 à 120 et de la mine 7
à 469 : chaque rappel exige une réouverture, appels bornés par les lieux et les indices
nouveaux, passages bornés sur dix minutes, même état et même rendu après recharge et laps
découpé. Autres cas : joueur cherché, absence et attente de 121 minutes, indice dans la même
minute, recharge, bruit répété, réponse et retrouvailles (Aubin/Gorm, Hugues/Anselme).
**Bilan consolidé : 1 694 tests, 16 ignorés, zéro échec restant.** Suite lancée une fois
(`tools/tests.py --processus 3`, 1 743,6 s) : deux erreurs de sockets Web et deux fichiers TUI
bloqués dans le bac à sable ; leurs seules reprises hors bac à sable passent (41 tests).
Le blocage TUI a prolongé la vérification ; aucune seconde suite globale.

**Mesures.** Banc rapide contre `da13f9d`, quatre scénarios × 1985/7/42/2024, 4 h :
les mesures des seize nuits sont identiques, zéro violation, usurpation ou plantage.
Appels moyens Relais/mine/auberge/crue : 0,25 / 0 / 0 / 1,25 dans les deux versions ;
maximum de passages horaires par nuit, moyenné : 7,5 / 8 / 13,75 / 17, inchangé.
Référence calculée une fois et cachée ; aucune comparaison de performance entre des temps
mesurés séparément. Audit 12 h contre les nuits historiques
`ffcc295`, réanalysées sans rejouer : crue 3, appels 11 → 9, passages/h 21,5 → 19,5 ; mine 7,
23 → 19 et 20,33 → 18,25. Brune appelle trois fois à 121–122 au lieu de dix à 121–128,
puis retrouve Gorm et lui demande sa part à 123. Odon parcourt les sept lieux une fois ;
deux rappels à 475 suivent les bruits nouveaux du baraquement et de la galerie.
Zéro plantage ou usurpation ; maxima horaires crue 24 → 24, mine 23 → 22 ; aucune nouvelle
alerte de boucle. Les six avertissements redits de la mine existaient déjà.

**Limites.** Une cible mobile ou de nouveaux indices peuvent légitimement provoquer de
nouveaux appels ; aucune borne globale indépendante des informations reçues n'est promise.
L'alerte « appels nombreux » d'Odon subsiste (20 → 15 appels). Les rencontres et échanges
divergent : dans la crue, le sans-recours augmente de 60 à 240 minutes cumulées et deux
observations d'eau longue apparaissent, malgré une exposition totale à l'eau de 585 → 540.
Pas d'amélioration uniforme des besoins promise. Ni Luna, ni campagne complète d'intégration supplémentaires.
Bruts : `artifacts/codex-37/` dans le worktree ; référence d'audit historique réutilisée
depuis `artifacts/verif-integ-ffcc295/audit-12h/` du dépôt principal.
