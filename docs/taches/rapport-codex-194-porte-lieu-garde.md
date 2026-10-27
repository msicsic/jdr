# Lot 194 — installations et responsabilité crue

Branche `codex-porte-lieu-garde`, **non fusionnée**, base `integration
de18162`. Aucun Luna ni scénario modifié. Raccords minimaux dans `pnj.py`
et `moteur.py` autorisés par l'orchestrateur pour partager le contrat avec
les témoins et le joueur. Bruts exclusivement dans
`C:/Users/msics/donjon/artifacts/porte-194/` ; deux travailleurs réduits au plus.

**Invariant.** Briser une installation sans propriétaire déclaré lèse aussi
son responsable connu. `biens.responsable_cru` conserve la priorité de la
propriété existante ; à défaut, il lit le porteur cru d'une clé (avec les
contenants intermédiaires), une garde interprétée ou la charge propre du
personnage par `deliberation.charges_gardees` (pulsion/agendas). Il ne lit
aucun agenda privé d'un autre personnage. Une responsabilité supposée
fausse reste une croyance ; un déplacement réel non appris ne la remplace
pas. Aucun transfert de propriété n'est inventé dans la sauvegarde.

`a_autrui`, `leses` et `lese_par` alimentent le devis et l'exécution.
`Vue.leses_bris` conserve la personne lésée : les gestes de bris ajoutent les
prix communs de l'honnêteté et de la douceur, avec la même usure en détresse
et les mêmes interdits à 100. La personne lésée entre dans `_entrees_communes`,
y compris lorsque seule son identité change. Les témoins visuels et auditifs
attribuent le tort selon leurs propres croyances avant mémorisation et
épreuve relationnelle. Les coups du joueur sur un objet protégé passent
désormais par le registre commun, coup manqué compris.

**Vérifications.** **105 ciblés finaux verts**, huit fichiers : sept nouveaux
parcours, 34 tests du prototype et 64 des contrats repris. Aubin demande la
clé plutôt que de forcer ; la neutralisation de la seule nouvelle lecture
rend le bris dans cette même scène. Demande pour un autre contenant, coup
réel du joueur et tort mémorisé au gardien, détresse et coups réels, valeurs
entières, ignorance du porteur réel, garde lue et charge propre, expiration
de la lecture invalidant le cache, monde/rendu/journal rechargés et laps
entier/découpé. La nuit hameau 1, tirée,
4 h sur la base actuelle avec la nouvelle responsabilité neutralisée, ne
reproduit plus les coups historiques d'Aubin ; scène équivalente autorisée.
Les tests construisent cette scène équivalente avec les autres foyers
épuisés, sans changer les données historiques du scénario.

Suite complète unique : **2 323 tests, 268 fichiers, 1 868,206 s**, quatre
échecs et quatre erreurs bruts, aucun ignoré. Le raccord joueur ajouté
pendant la suite révélait une lecture de profil autonome chez un acteur
sans profil : contrat corrigé, prototype repris vert. Les nouveaux tests
ont été corrigés sur le nom du besoin (`chaleur`), la durée du bris et le
témoin hors du regard du joueur. Les 105 ciblés consolident ces reprises ;
restent les deux MiMo historiques `6 != 5`, sans seconde suite complète.

**Bancs.** **21 nuits 4 h**, quatre scénarios × quatre graines, hameau
× cinq (dont 1) : zéro plantage/usurpation ; **21/21** mondes/rendus rechargés
identiques. Deux bris au hameau (Ilse/porte, 7 ; Brune/réserve, 42), cinq
crochetages (trois crue, deux hameau), aucune demande de clé dans ces nuits :
le nouveau choix est démontré par les scènes ciblées. Quatre répétitions
signalées (agendas de Brune, hameau 1985/7 ; lecture de Gorm, Relais 2024) :
trois contrôles de branche neutralisant la seule nouvelle lecture donnent
des **états complets, chroniques et alertes identiques** ; aucune nouvelle
boucle attribuée au lot. Autres observations : quatre `fige_presse`, un
`noir_long`, trois `voir_alterne`. **VERIFIER + spatial 0,2**, hameau 1985,
2 h : aucun écart/plantage, monde/rendu rechargés identiques.
Seize références relues uniquement, `4c57020` (Relais/auberge) et `812ebe5`
(mine/crue), antérieures à la base : écarts non imputés au seul lot ; quatre
chroniques d'auberge identiques. Aucun cache hameau disponible. Aucune
référence existante rejouée ni comparaison de CPU de cache.

**Limites.** La responsabilité ne donne pas de nouveau moyen social :
le plan compare les demandes de clé et autres moyens déjà disponibles ;
aucune demande d'ouverture nouvelle n'est ajoutée. La garde d'autrui doit
être connue par une lecture existante, pas déduite de son agenda secret.
Le contrat existant conserve une victime par bien : à propriété égale,
les clés puis les gardes sont prioritaires, départagées par identifiant
stable si plusieurs responsables sont crus. Aucune garantie générale
supplémentaire sur les boucles, les autres besoins ou la narration.

Aucune clé de signature Git configurée : commit non signé. Livraison sur
la branche seule, `main` intacte.
