# Lot 360 — contrat des nouvelles après le 337

Branche `codex-regressions-337`, base `integration 0b62a4fa`.
**Correctifs et portages réalisés ; validation finale en cours, non fusionné.**
Bruts : `C:/Users/msics/donjon/artifacts/regressions-337-360/`.

**Invariant commun.** Un enrichissement de preuve ne perd pas l'information
plus simple qu'il contient ; un fait initial inchangé ne devient pas nouveau
par une nouvelle observation ou par l'installation d'une représentation.
Le 337 disait « identité distincte d'une accusation de portage » : cette
distinction reste nécessaire, mais son implémentation rendait les preuves
de droits et de lieu disjointes dans les deux sens. `faits_dits` retient
désormais lieu nu **et** droits. Le lieu seul n'atteste toujours pas les droits ;
la réception des droits atteste aussi le lieu. Les deux captures d'étapes
retrouvent **tous leurs hashes attendus**, plans, visites, monde projeté,
lignes et deux rendus compris, sans recalage d'oracle.

**Décision utilisateur du 30 octobre.** L'inventaire de départ ne se raconte
pas. `faits_initiaux` est une provenance sauvegardée, distincte des croyances
et des faits dits. `reviser_dits` retire l'ancrage au changement appris ; le
retour ultérieur à une ancienne valeur reste nouveau. Les biens déjà portés
incluent leur état matériel : les portions et charges déjà consommées dans
les captures d'appel 270 et d'aide 541 ne produisent plus de fausses nouvelles
de consommation. `preuve_possession`, `etat_materiel` et `faits_materiels`
partagent le calcul avec le constat normal. Les découvertes sur un bien tiers
restent possibles, notamment un verrou appris par essai. Aucun savoir privé
n'est versé aux croyances, aucun droit réel relu à la réception, aucun appel Luna.

**Prémisses portées, assertions conservées.** Une vraie prise ou consommation
reste racontable selon le rapport 337 ; elle peut changer les jets et les
plans d'une épreuve antérieure. Six anciens oracles isolent donc leur canal
de constats de 55 avec `canal_constats_anterieur_337` : les faits y sont
déclarés récents, sans confidence de possession/fin concurrente. Ce double
n'est utilisé ni par les tests du 337 ni par les nouveaux tests de provenance.
La capture de flamme conserve tous ses objets et besoins : seul le savoir
d'Aubin est déclaré à jour sur le levier déjà porté par Ilse à t=102, au lieu
de son ancienne position au sol à t=98. Le recours de lumière 645 déclare
explicitement son urgence de sécurité, sans froid ni abri de compagnie
concurrents : la capture brute commençait à sécurité 23,493 et chaleur 95,967,
avec un plan de chaleur. Elle reste rejouée pendant 30 min, entier/découpé.
**453 assertions AST contrôlées** : seules les deux formulations de mouvement
G7 autorisées dans la méthode de passage du 360 diffèrent. Le monde complet
et les deux rendus sont comparés après recharge ; seul le nouveau registre
de provenance sort de la projection historique d'étapes. Aucun hash attendu
n'a changé. `DemanderLePassageTests` reste intact pour le 361.

**Mesures.** Premier contrôle groupé : 319 tests, neuf échecs et une erreur ;
ces incidents ont maintenant leurs témoins ciblés corrigés. Les tests du 337
restent verts, avec nouveaux témoins Relais/auberge de l'inclusion des preuves,
et vivres/bois du hameau pour les consommations anciennes puis nouvelles.
Premier banc : 20/20 nuits achevées sans plantage, sources stables ; constats
confiés **102 sur main / 179 sur le premier candidat**. Cette comparaison
cumule les autres lots depuis main, ce n'est pas une mesure causale du 360.
La reprise finale joue 31 fichiers ciblés et la classe du passage spontané,
puis vingt empreintes de 2 h, cinq scénarios et quatre graines, deux travailleurs
réduits au plus. `origin/main` résout `main 0bad227`, cache partagé conservé.
Les comptes finaux seront dans `validation-finale/constats-confies.json` ;
fin écrite en dernier : **`validation-finale/fin.json`**. Ni suite complète ni Luna.

**Limites.** Le passé initial d'une ancienne sauvegarde sans provenance n'est
pas reconstructible : l'installation ancre ses inventaires présents et ses
anciennes localisations sans droits. La distinction exacte entre inventaire
initial et transfert ancien encore non raconté n'est alors pas garantie.
Les scènes isolées des anciens oracles ne prouvent pas que toutes les anciennes
nuits gardent leur calendrier avec de vraies nouvelles supplémentaires.
Aucune garantie universelle contre les boucles ; pas de fusion dans ce lot.
