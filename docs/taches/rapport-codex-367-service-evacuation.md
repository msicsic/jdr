# Lot 367 — service payé et évacuation

Branche `codex-service-evacuation`, base `integration dea991a5` ; laptop,
deux travailleurs réduits au plus. Aucun appel à Luna ni suite complète.
**Terminé, non fusionné ; code mesuré `21bc1897`, branche poussée.**

**Invariant et cause.** Une réussite payée sur un bien mobile connu comme
appartenant au bénéficiaire n'est pas abandonnée par son seul départ. Dans
le cas hameau 1985, l'allumage est constaté à `242`, avec Ilse connue dans
l'antichambre. À `1145`, Brune la croit dans l'échoppe, tandis qu'elle porte
la torche dans l'antichambre. `services_proteges` clôt alors la trace ;
`menager_flamme` peut éteindre à la minute 2. Le déplacement appris d'Ilse
est réel pour cette croyance : ce n'est pas une clôture issue d'un monde
simulé. L'ancrage spatial du 238 ne suffit plus, car il ne distingue pas un
bien du bénéficiaire d'un moyen appartenant au prestataire.

**Correction.** `biens.services_proteges` tient compte du propriétaire connu
dans la preuve perceptive de possession déjà sauvegardée avec le lieu de
l'objet. Pour un bien mobile du bénéficiaire, son départ ne suffit plus à
clore la protection. Le filtre commun des transitions et `menager_flamme`
emploient déjà ce résultat ; aucun raccord propre à l'évacuation, au hameau,
à une flamme ou à un agenda. Ni `agendas.py` ni `deliberation.py` modifiés :
pas de recouvrement de code avec les lots 364–366/368 annoncés. L'état
constaté défait, la destruction, la mort et l'épuisement restent des fins
ordinaires ; aucune obligation d'entretien ni reconstitution de trace close.

**Preuves.** Les deux méthodes réservées du 362 passent, sans changer
leurs assertions. Le fichier historique et son voisin : 29 tests verts,
46,698 s. Le nouveau parcours d'auberge paie réellement Joss pour la lanterne
d'Odile, puis déplace prestataire et bénéficiaire. Il contrôle flamme, trace,
autre service payé de serrure, monde complet, rendu et scène après recharge,
en bloc et en deux laps ; une cession apprise ne clôt que la trace concernée.
Les anciennes épreuves de départ sur le bien du prestataire et d'épuisement
restent conservées.

**Validation finale.** **115 tests / dix fichiers verts**, 306,812 s,
zéro échec, erreur ou saut. Les dix méthodes historiques du fichier modifié
sont identiques en AST ; `test_pas_compagnons.py` est inchangé.
**12/12 paires d'empreintes 2 h identiques**, quatre graines sur hameau,
auberge et Relais contre `dea991a5` : chronique, mesures et état complet,
aucun plantage. Les douze références manquantes ont été calculées une fois
puis rangées dans le cache commun, aucune référence relancée. Les compteurs
d'avis restent identiques (zéro non justifié ; deux à expliquer au hameau
1985 et 7). Ces nuits naturelles identiques ne remplacent pas les captures
ciblées qui exercent le correctif. `fin-validation.json` : codes tests et
empreintes **0/0**, sources inchangées, 960,396 s ; aucun calcul actif.

**Limites.** L'utilité reste une estimation conservatrice : la propriété
connue prolonge la protection même sans besoin actuel ; elle ne lit ni besoin
privé ni propriété réelle cachée. Les biens fixes et les biens mobiles d'un
autre propriétaire gardent le critère spatial des lots 224/238. Une ancienne
trace déjà close n'est pas reconstruite. Aucune garantie générale sur les
boucles des agendas n'est revendiquée.

Bruts : `C:/Users/msics/donjon/artifacts/service-evacuation-367/`
(`diagnostic-367-detail.json`, `tests.json`, `empreintes.json`, sources et
`fin-validation.json` écrit en dernier). Les premiers lancements sous bac à
sable ont échoué sur les temporaires Windows ; les vérifications exploitables
utilisent les droits d'exécution autorisés, sans modification du harnais.
