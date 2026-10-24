# Lot 41 — une admissibilité de route pour la recherche et la marche

24 octobre 2026. Branche `codex-route-admissible`, **non fusionnée**, base
`750837a` (fiche `0d81ad4`). Aucun changement du MJ, des scénarios, des ressources,
des caractères, de `REPIT` ou des seuils ; aucun appel au modèle.

**Invariant et fonctions.** `route_admissible.refus` juge l'eau pendant chaque
passage, les gestes des portes et l'issue du séjour. `trajet_estime.parcours`
l'applique aux préfixes, `Vue.route` au but ; `_marcher` consulte cette même route
et borne son chemin spatial à ses salles et portes fermées. `eau.en_peril`
consulte aussi cette règle : une traversée en cours ne devient plus un séjour
à la minute ronde si le PNJ peut encore sortir avant la noyade et gagner son but.
`Vue.descente`, `piege` et `_retour` refusent de créer un enfermement : retour
**ou évacuation**, par le même parcours projeté à l'horizon du séjour, portes
certaines et durées comprises. Sortir d'un péril déjà présent reste permis. Une porte inconnue se tente seulement avec un repli immédiat encore
possible, estimé prudemment à deux fois le trajet entier ; ni une attente ni
un crochetage futur ne garantissent une sortie. Clés et ouvertures acquises
dans le plan comptent. La droite d'eau reste sous le sol avant de l'atteindre ;
l'eau observée reste son minimum. Ses coefficients et les durées entrent dans
`_entrees`. `VERIFIER` emploie la même règle. La borne du lot 38 reste admissible :
des arêtes sont retirées, aucun coût positif qu'elle minore n'est réduit.
Les causes écartées se lisent dans le récit ; le refus du départ se sauvegarde
avec la chronique.

**Preuves.** Brune (capture crue 500 à 160) et Ilse (scène d'auteur à 100)
rejoignent le poêle au sec avant vingt minutes : même monde complet et rendu
après recharge, d'un bloc ou par minutes, depuis la capture originale. Six tests
couvrent aussi la traversée en cours, le passage trop long, la porte incertaine,
le repli coupé, l'évacuation acquise et l'invalidation de mémoire. Le test
historique du détour reste vérifié pour deux PNJ avec une eau coupant réellement
le passage : interdire sa traversée brève sous la seule projection à une heure
était précisément le défaut corrigé. Le test des ressources suit la nouvelle
nuit : Brune rallume le poêle avec une planche consommée, l'autre reste comptée ;
les trois charges de Gorm sont intactes. Le diagnostic du lot 39 vérifie désormais
l'arrivée, sans figer le bug.

**Mesures.** Rapide, 4 h × 1985/7/42/2024, crue et Relais, contre `750837a` :
aucun plantage, violation ou usurpation. Relais : chroniques et mesures identiques.
Crue : sans recours **75 → 60**, eau **110 → 98,75** min·PNJ ; maximum horaire
moyen des passages **17 → 12,75**, pire **32 → 14**. La boucle faim/eau en 1985
cesse de faire rebrousser le PNJ pendant une traversée sûre. Bascules 0,25 → 0,5 :
Brune ouvre la réserve à 103, Gorm la referme à 228 (une reprise, pas une boucle) ;
une alternance isolée d'enquête en 7 ; aucun avertissement redit.
Paire CPU finale sans cache, crue 1985, 4 h, un processus, référence puis branche
sous la même charge de validation : **10,31 → 12,06 s (+17 %)**, nuits divergentes.
Aucune comparaison des temps du cache avec ceux des reprises.

Audit final, branche seule, 12 h : crue 500, eau **815**, sans recours **60**,
attente **1 475**, trois « eau longue » ; crue 42 : **285 / 185 / 255**, aucun
« eau longue ». Aucun plantage, usurpation ou écart. Les archives prescrites
`artifacts/verif-integ-ffcc295/` sont absentes du poste ; le cache disponible
ne contient que les 4 h. Le rapport 39 donne pour 500 **865 / 495 / 1 100** :
comparaison chiffrée partielle, aucune comparaison complète aux deux nuits
historiques revendiquée, aucune référence de 12 h relancée.

**Validation finale.** `VERIFIER` et `spatial.VERIFICATION=1`, 2 h, crue 42/500 :
aucun écart ni borne. Suite finale (`tools/tests.py --processus 3`) : **1 713 tests,
quatre ignorés**, verte en 563,8 s, priorité réduite. Les six tests du lot repassent
après le dernier contrôle du temps d'attente au départ du retour ; les chroniques
et mesures des huit nuits rapides restent identiques à la passe finale précédente.

**Limites.** Durées estimées par salle, sans occupation mobile ni actions futures
des autres ; une découverte ou le temps écoulé imposent une nouvelle délibération.
Les anciennes parties sans cases gardent leur durée conventionnelle. Ni une
baisse uniforme de l'exposition à l'eau ni la fin générale des boucles entre
besoins ne sont garanties. Bruts : `artifacts/codex-41/` du worktree.
