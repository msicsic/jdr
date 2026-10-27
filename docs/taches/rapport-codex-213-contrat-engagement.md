# Lot 213 (196 c) — contrat d'engagement, validation en cours

Branche `codex-contrat-engagement`, non fusionnée, départ `cca5f50` vérifié,
reprise demandée sur `d2243c2` (211), intégration fusionnée par `2a2d766`.
Reprise au-delà du créneau explicitement autorisée. Aucun Luna ; deux
travailleurs réduits au plus. Bruts exclusivement dans
`C:/Users/msics/donjon/artifacts/engagement-213/`. Aucune clé Git configurée.
Le commit de diagnostic `51728f2` est poussé ; il précède l'implémentation.

**Revue 217 appliquée.** Aucun coût de trajet déjà parcouru n'entre dans
l'inertie. La marge commune vaut `INERTIE + VOL/4` ; les coûts futurs des
moyens restent évalués par le planificateur, sans conversion arbitraire de
minutes en points d'urgence. Le contrat minimal reste lié à l'identité de
l'intention dans un registre auxiliaire d'`agendas.py` (validateur d'intention
d'`esprits.py` inchangé), sans créer d'agenda pour les secours. Sa demande
porte condition de fin, parent éventuel et raison crue. Les phases naître,
continuer, attendre, finir et les causes de sortie attestées avec leurs faits
sont persistées ; une absence de certificat reste explicitement indéterminée.
**35 ciblés distincts verts**, dont huit tests du contrat. Le passage commencé
avant cette instruction a été interrompu ; les vérifications finales portent
sur cette version figée. **Limite 218 :** la suspension temporaire d'une charge
n'est pas portée par ce registre. Gorm/Aubin, hameau 1985 min 6 : sa garde peut
reprendre après reconstruction de la livraison ; reprise laissée au lot 218.

**Ce qui change.** `choisir` revalide l'intention avant l'arbitrage et applique
une règle commune de préemption : palier strictement supérieur, ou gain d'au
moins `INERTIE` au même palier. Une garde ou une attente à plan vide peut être
revalidée. L'inertie n'écarte plus les candidats à leur naissance ; les bonus
locaux d'agenda et de besoin sont absorbés par cet arbitrage. Un geste manqué
libère l'engagement et les préférences de cible avant une nouvelle décision ;
une nouvelle planification vers le même but reste permise.

Les candidats portent une demande typée pour les conditions et les agendas.
Sa provenance, son urgence et sa raison sont conservées par `agendas.py`,
comme état facultatif vérifié et rechargeable, lié à l'intention courante.
`_reprendre_demande` consulte les mêmes prédicats de condition et de projet
que les mécanismes existants. Un secours peut ainsi continuer hors de vue
sur sa détresse crue ; une détresse démentie, la mort connue ou une disposition
sociale devenue incompatible le libère. Le poids social est recalculé.
Aucune règle de personnage, objet ou scénario, aucun fichier interdit modifié ;
`_lieu_cru` et `salle_crue` comparés à la base : identiques.

**Preuves.** Base : vingt nuits 4 h, cinq scénarios × quatre graines,
compteur 199 : **0/1/5/9/9 = 24**, sans plantage. Références exactes en cache,
relues sans nouveau calcul. Les captures 209 de Rémy (mine 42) et Mireille
(auberge 1985) sont conservées en fixtures : adoption réelle d'un secours,
monde complet, rendu et laps entiers/découpés après rechargement vérifiés.
Autres scènes : faim hors de vue malgré plan coupé, démenti, préemption d'une
ronde, autre PNJ et autre secours contre le froid, garde vide et marge.
**28 ciblés verts** avant le dernier test de démenti. Suite complète unique
`tools/tests.py --processus 2` en cours ; aucune seconde suite prévue.
L'oracle A0 conserve la naissance historique sans intention ; la poursuite
est désormais vérifiée par reproduction et recharge, pas par identité avec
l'ancien arbitrage.

**Premier banc, non final.** Vingt nuits de branche : suspects
**0/1/0/0/1 = 2**, aucun scénario en hausse, aucun plantage ni usurpation.
Mais Brune hameau 2024 reste dans l'eau (140 min sur cette graine) : un plan
commence à répétition par une prise d'outil manquée. Cette observation a
motivé le démenti commun sur geste manqué ajouté ensuite. Le banc final doit
encore vérifier cet effet. Les métriques finales et S/F/D restent à relever.
Les activations/sommeils d'a1 de Brune passent de huit à trois dans ce premier
banc ; leur cause n'est pas supprimée. Gorm présente encore des épisodes
sans but ; aucune correction générale de leur cause n'est établie.

**Limites ouvertes.** Un `None` du planificateur ne distingue toujours pas
borne, coût d'endurance et impossibilité. La poursuite ne réinstalle donc
jamais aveuglément un ancien plan ; en revanche, toute disparition de plan
n'a pas encore de certificat moteur de démenti. Les sources sans demande
persistante doivent encore réémettre leur cible pour être revalidées.
La liste fermée n'est donc pas garantie sur toutes les voies, et les verrous
historiques d'abri/lumière ne sont pas tous absorbés. Les localisations cachées
et la restauration des charges restent hors périmètre. **Aucune solution
générale, absence d'entêtement ou aptitude à la fusion revendiquée à ce stade.**
