# Lot 175 — fins constatées, livraison partielle

Branche `codex-fins-agendas`, **non fusionnée**, base `integration 7eb1ac9`,
code `0544be1` puis `101f770`.
Périmètre élargi autorisé par l'orchestrateur : perception/esprits et points
de geste communs ; départ définitif du protégé retiré du lot. Livraison
partielle autorisée. Aucun Luna, scénario historique ou fichier réservé aux
lots 172/173 modifié. Bruts exclusivement
`C:/Users/msics/donjon/artifacts/fins-175/`.

**Invariant livré.** Une destruction ou consommation constatée survit à la
mémoire bornée et au retrait des restes. `perception.fin_objet` distingue
intégrité nulle, réserve de portions/charges épuisée et simple extinction
d'un réservoir rechargeable. `esprits.constater_fin_objet` enregistre la
croyance `fin`, sa source et sa date ; `constats_geste`, commun au joueur
et aux PNJ, couvre aussi l'outil cassé sur un geste manqué. Les observations
et le schéma sauvegardé du joueur utilisent le même contrat. Une réparation
observée dément la croyance. La perception n'efface plus un savoir parce
que l'objet a disparu du registre réel ; cette disparition ne prouve rien.
Les lectures d'état/disponibilité sont conservées. La preuve n'ajoute pas
de réveil aux voies existantes ; la clé du plan ne la lit que par ses effets
sur gardes/prix_gardes, déjà inclus. Le placement d'auteur `sans_evacues`
retire lui-même les croyances initiales des entités qu'il retire de la scène.

`agendas.actualiser` abandonne `garder` sur cette seule preuve crue, avec
cause publiée à la sortie du choix. La responsabilité est retirée aussi
des lectures communes avant publication ; un choix interrompu ne publie
rien. Aucun devis direct ne réactive un projet terminal, même réparé.
Position inconnue et fin distante non constatée ne terminent rien.

**Épreuves et mesures.** **157 tests ciblés finaux verts** : deux biens détruits, deux
réserves épuisées, consommations réelles du joueur et d'un PNJ, deux outils
brisés sur échec, ignorance à distance, date persistante, retrait des restes,
réparation, choix interrompu, même laps entier/découpé, état et rendu après
rechargement ; preuve sans effet sur une clé de plan sans garde, invalidation
par la responsabilité avec garde, même si le bien réel est intact.
Suite complète unique : **2 264 tests, 261 fichiers, 1 352,153 s**, sept
échecs et une erreur bruts. Les régressions de cadence, dépendance du plan,
projection d'oracle et placement d'auteur sont reprises vertes ; restent les
deux MiMo historiques `6 != 5`, sans seconde suite complète. Un test de
clé supplémentaire est inclus dans les 157 ciblés, après cette suite.

**16/16 nuits 2 h** (quatre scénarios × quatre graines) : chroniques,
mesures, récits, souvenirs et empreintes physiques identiques ; aucun plantage,
16/16 mondes et rendus identiques après recharge. **8/16 états complets
strictement identiques** ; cinq autres ne diffèrent que par les preuves
`fin`, trois crues aussi par l'empreinte interne des croyances de l'agenda
d'évacuation. États, causes et dates de fin inchangés. Trois contrôles de
branche avec seule écriture de preuve désactivée expliquent ces écarts ;
ils ne rejouent pas le code de référence. Aucun gain de vitesse revendiqué.

**Référence réutilisée.** Les 16 nuits du lot 167 c, commit `5f69840`, sont
relues dans `garder-167c/empreintes.json`. Le diff de ce commit à la base
`7eb1ac9` ne contient que de la documentation. Aucun rejeu de référence ;
seules les nuits de branche sont calculées avec les fonctions du comparateur.
Chaque monde de branche et son rendu sont sauvegardés et rechargés.

**Limites.** Rendu/remis et perte vue sans permission ne sont pas livrés :
l'invariant complet demandé pour `garder` reste ouvert. La preuve matérielle
porte sur les objets à intégrité nulle ou portions/charges épuisées du moteur
actuel ; elle n'invente pas d'événement pour une suppression sans observation.
Départ définitif d'un protégé hors lot, notion absente du monde et à décider.
Restent suivi à portée de voix et interposition d'un lieu. Aucune garantie
générale nouvelle sur les autres besoins, les navettes ou l'hystérésis.
Aucune clé Git de signature configurée : commits non signés. Au plus deux
travailleurs réduits ; aucune fusion ni modification de `main`.
