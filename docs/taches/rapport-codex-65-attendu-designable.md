# Lot 65 — Un attendu ne cite que des cibles désignables

Branche `codex-attendu-designable`, non fusionnée ; base `de3e986`, brief `39e756c`.
`origin/integration` était déjà inclus au départ. Ni `main`, ni `planification.py`,
ni `social.py`, ni scénario, ni consigne de Luna modifiés. Modèle `gpt-6-luna` conservé.

**Invariant et correction.** Les listes techniques d'entités proposées dans les refus
passent par `refus.cibles` : candidats du geste, filtre `Monde.designable`, référence
publique de `noms.reference`, dédoublonnage, tri et plafond commun, dans cet ordre.
Couvre cible, outil, destinataire et ancrage des actions, opérations, improvisations,
artisanat, combat, paroles, dons et ajouts. Le champ `attendu` est projeté comme un
contrat technique : les références opaques restent utilisables, sans devenir des
portraits dans une chaîne de prose ; une voix non reliée garde sa référence de voix. L'absence de candidats est explicite. La saisie
locale inconnue donne aussi cet attendu par `Monde.trouver`.

`designable` admet désormais explicitement les souvenirs visuels marqués, corps déjà
reconnus, voix récemment entendues et noms appris, en plus de l'accès et du regard
possible existants. Aucun accès matériel n'est accordé par ce souvenir : les préconditions
physiques du moteur restent séparées, vérifiées à la préparation du geste. La saisie
nominale garde aussi son contrôle sensoriel distinct (`noms.verifier_nom`). Les registres
existants se sauvegardent déjà ; aucune migration ni donnée de scénario ajoutée.

**Cas réel relu.** La trace originale `integration-r2/relais`, saisie « je prends le
pied-de-biche », transmet `barbe_gorm`, `brune`, `mains_gorm`, `marchand` dans une chaîne.
Nuance du constat initial : `echoppe` est bien l'identifiant interne de la Conduite basse,
les surfaces `echoppe_*` y sont visibles et Gorm y est effectivement perçu ; leur absence
absolue n'est pas le bon critère. Les identifiants privés des corps et éléments sont
remplacés par leurs références publiques ; les autres entités ne passent que si elles
sont perçues ou mémorisées. La liste ne prouve jamais une présence.

**Vérification.** Cinq nouveaux tests : console/MJ simulé et vraie sauvegarde du cas réel ;
personne inconnue nommée dans le noir et refus local ; références publiques et souvenir
sans accès ; parcours des actions et opérations sur deux mondes rechargés ; refus de
combat qui énumérait toutes les personnes vivantes. Contrôles de l'état, des possessions,
du message affiché et du rendu après recharge. Les 50 premiers tests ciblés passent ;
les cinq nouveaux passent (8,33 s). Suite complète unique à trois processus et priorité
réduite : **1 823 tests, 16 ignorés, 1 092,75 s**. Neuf assertions initialement en échec :
deux régressions corrigées (contrôle sensoriel à la saisie et référence de voix), sept
attentes adaptées à la distinction connaissance/accès dans `test_question_absent` et
`test_personnages`, sans retirer leurs contrôles d'état privé. **103 tests de reprise verts**
(cinq fichiers via `tools/tests.py`, puis les deux fichiers adaptés), plus 24 tests de
défense et sauvegarde. Bilan consolidé : aucun échec restant ; aucune seconde suite.

Empreintes 2 h, Relais, 1985/7/42/2024 contre `de3e986` : chronique, mesures et état final
complet identiques, quatre nuits. Référence absente, calculée une fois et rangée dans le
cache commun. Aucun banc long ni campagne Luna à deux passes.

Luna, une passe complète de `relais`, `crypte`, `echanges` : 62 → 54 appels, 22 → 20 tours MJ, **2,82 → 2,70 appels/tour**, 12,03 → 11,32 s/tour.
Relais 3,00 → 2,50 ; crypte 2,67 → 2,78 ; échanges 2,75 → 3,00 appels/tour.
Aucune erreur technique ni erreur de recharge ; un repli en crypte sur la prime (contre zéro
au cache) : faux refus sémantique de la condition de remise, puis confusion entre offre et
dette due, hors de cet invariant. Le cas réel est effectivement refusé et relancé : l'attendu
reçu par Luna garde `element_33`, `element_9`, sans `brune`, `marchand`, `barbe_gorm` ni
`mains_gorm`. Les surfaces `echoppe_*` visibles et les objets mémorisés restent admissibles.
Référence `main` `42bb9c0` relue directement du cache : scripts identiques, harnais ancien
(`91a2d21f3d`), donc comparaison indicative des temps et appels. Le lanceur actuel ne peut
pas rejouer `main` (import `agendas` absent), sans appel Luna lors de cette tentative.
Bruts : `artifacts/bancs-multi/`, `tests-complets-65.json`, `empreintes-65.json`.

**Limites.** La liste est bornée à douze références, elle n'est pas une preuve de faisabilité.
Les refus peuvent citer la valeur reçue : cette répétition ne doit pas être confondue avec
une suggestion d'entité connue. Ce lot borne les listes de correction ; il ne prétend pas
résoudre les contradictions sémantiques du MJ ni tous les faux refus d'audit. Pas de nouvelle
exception par personnage, lieu, objet ou formulation.
