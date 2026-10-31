# Lot 423 — Une pièce de lot par la saisie libre

31 octobre 2026 — `codex-piece-de-lot-libre`, base `integration` / `07e270be`, code `ab0f9105`.
**Contrat commun et reprise vérifiés avec MJ simulé ; prélèvement Luna non démontré.**

**Origine.** Le même script `lots` sur la copie de `91a58c8f`, parent de la fusion
A4–A5 `b1d74a71`, propose bien `prelever` dès la première interprétation de
« je prends discrètement une planche du tas ». Il ne prélève rien : la description
physique n'est pas admise. Ce résultat ne prouve pas que le typage initial était
toujours juste. Dans la trace réelle du 422, la revue déclarait `deplacer` conforme
dans ses champs typés et refusait le plan pour un autre motif (vol prétendument
ajouté), sans champ corrigeable. A5 figeait donc cette opération, puis bloquait
`prelever`. Ce blocage de correction vient d'A5 ; l'erreur de quantité initiale
et le défaut de qualification ne sont pas attribués à A5 sur cette seule passe.

**Changement.** `contrats_lots` définit une seule fois le déplacement de l'objet
entier et le prélèvement d'exactement une pièce (`objet` / `part`). Le compilateur,
les consignes existantes et la revue réemploient ces définitions. `operations`
fige dans chaque sous-plan sa quantité proposée depuis l'état simulé de cette
étape : nombre transféré, nom de pièce et reste du lot. `comprehension` expose
ces données à la revue et dans « Compris », sauvegardé par la voie existante ;
le reste annoncé est explicitement celui prévu après réussite. Un refus typé
de quantité peut contester l'opération qui porte cette quantité, sans libérer
cible, destination, méthode ou autre étape. Le refus moteur de `prelever` sur
la dernière pièce libère désormais cette seule opération, avec reçu et accepté.
A5 conserve ses gardes ; aucun mot du refus ni de la saisie n'est analysé.

**Tests : 72 méthodes vertes**, sept fichiers concernés, un travailleur à priorité
réduite. `tests-livraison.json` : 67 tests, 158,23 s ; `tests-cloture.json` :
compréhension console/web/TUI verte (5 méthodes), avec reprise et dossier revérifiés.
La vraie boucle console/PontWeb, avec MJ simulé, contrôle après deux chargements
une planche du Relais et une bûche de réserve : une pièce portée, lot diminué,
charges et masse conservées, conversation, récapitulatif, inventaire et vues
identiques après reprise. Une correction qui change aussi la méthode reste
refusée. Autres oracles : lot entier explicitement demandé, deux prélèvements
successifs et dernière pièce déplacée après refus de quantité borné à son étape.
Les dossiers sont indépendants de la prose, sans mutation du monde ni du plan.

**Banc rapide terminé : 8/8 nuits sans plantage**, branche seule, Relais/auberge,
4 h × quatre graines, un travailleur à priorité réduite : 608,27 s écoulées,
600,69 s CPU. L'audit signale 52 dérives d'avis ouvertes, quatre cessations
physiques de service, trois figements, un noir prolongé, un avis à expliquer,
une alternance et douze appels répétés de Lucien (auberge 2024). Ces signaux
ne prouvent pas une régression ; sans référence appariée, son absence n'est
pas établie non plus. `rapide-fin.json` confirme les huit nuits achevées.

**Luna, une passe sur copies.** Base ancienne : **11 appels / 3 tours MJ**, 55,10 s
écoulées, aucun plantage ni erreur de recharge. Branche, `lots` et `ressources` :
**17 appels / 6 tours MJ**, 2,83 appels et 10,77 s/tour, 88,37 s écoulées,
aucun repli, erreur technique ou de recharge. `ressources` : 6 appels, aucune
relance ni refus. `lots` : la qualification est écartée par le contrôle de portée ;
au tour de prise, Luna propose un enrichissement de personnage, refusé comme
non visible. Aucune proposition en attente, aucune pièce prise, lot inchangé.
Ces chiffres ne mesurent donc pas le coût d'un prélèvement fidèle ni un gain.

**Limites.** Le choix initial et le classement de la revue restent sémantiques.
La nouvelle définition et le dossier quantifié ne constituent pas une garantie
universelle de compréhension du français. La passe Luna ne valide pas l'invariant
complet en partie ; le correctif ne doit pas être présenté comme cette garantie.
Les derniers ajustements de contrat, rendu et refus de dernière pièce ont été
contrôlés ensuite sans modèle ; aucune seconde passe Luna n'a été lancée.
Aucun audit retiré, scénario ou registre d'esprit modifié. Pas de suite complète.

**Bruts.** `C:/Users/msics/donjon/artifacts/piece-de-lot-423/` : fils et copies de
mondes, lanceurs, commandes, tests, banc rapide et `bilan.json` final. Aucun calcul
restant. La première tentative de rejeu
dans le bac à sable a été interrompue sans résultat après dix minutes ; la passe
achevée et les tests utilisent les temporaires Windows accessibles hors du bac.
