# Lot 233 — compagnon entendu, rencontre et validation des oracles

28 octobre 2026. Branche `codex-pas-compagnons-c`, **non fusionnée**.
Livraison initiale `f34e6c2` ; reprise après merge de `origin/integration`
**`01ce467` dans `7d68a8f`**, sans rebase, seul conflit documentaire.
**Décision utilisateur : perte de richesse du hameau acceptée** ; les rencontres
nées de rotations fortuites ne sont pas une source légitime de richesse.

**Invariant.** Un bruit ordinaire attribué à une présence crue réveille le choix
commun (`ouie.entendre → esprits.reconsiderer`) sans rotation ni position
inventée. La compatibilité de marche seule ne rajeunit pas sa preuve ;
l'audibilité et l'identification gardent leurs contrôles communs. Le `tenu`
du 195 reste conservé. **Aucun code moteur/MJ ajouté ou modifié par cette
reprise** ; les modifications du 229 et du 232 viennent du merge demandé.

**Arbitrage des six échecs du candidat.**

| Cas | Diagnostic et correction de l'oracle/prémisse |
|---|---|
| Empreinte mine | Oracle caduc : rotation de Gaspard à 288872 supprimée. Six champs mesurés migrés. |
| Empreinte auberge | Même cause, rotation d'Anselme à 289356 supprimée. Même migration. |
| Secours de Rémy, capture 209 | Le départ à 0 n'engendre plus le secours historique. Reprise au checkpoint réel **725** de `01ce467` : aide à Odon avec le pain de Lucien. Contrat initial exigé, monde/rendu rechargés et laps découpés conservés ; naissance toujours exercée à l'auberge. |
| Lampe de Lucien | Le plan de demande existe à 846, mais Josse se déplace avant l'échange. La lampe est désormais réellement vue, Josse occupé au poste durant la fenêtre. **VERIFIER, demande effective et refus respecté inchangés**. |
| Témoin pendant le vol | Son à 0, réveil, puis à 100 le choix abandonne le trajet injecté « devoir » sans charge. Trajet fixé comme réflexe déclaré `alerte`, régi par sa priorité commune ; toutes les assertions de vol, témoignage et mémoire sont conservées. |
| Placement d'Ilse | Défaut connu du 195, réservé au **234** ; ni `signes.place` ni `pnj.agir` modifiés. |

Captures rejouées sur l'intégration et le candidat : **lignes affichées,
`regarder` et `scene_percue` strictement identiques** aux oracles historiques ;
seules visites, nombres, plans, diagnostics et monde interne changent. `pas-233-etapes.json` ne remplace que ces six champs.
Sur les quatre fichiers arbitrés, **152 des 153 anciennes assertions sont
identiques par AST** ; une expression d'empreintes est migrée, quatre assertions
de provenance/schéma sont ajoutées. Aucune assertion de résultat retirée.

**Aubin, crue 2024, 23576 : retour justifié comme autre moyen, pas service
accompli.** Retirer seulement le réveil 233 (`ouie.py` 195 en mémoire) fait
disparaître cette trajectoire sur les mêmes 41 premières minutes : l'apparition
est donc un effet indirect du 233. À **23551**, demande refusée `necessaire`,
moyen retenu en `manque`. À **23576**, `eveil=None` : fin de la surveillance,
pas nouveau réveil acoustique. Le choix conserve le refus et remplace la
demande par **ouvrir la réserve puis servir**, sans témoin. Il se rapproche,
mais le témoin empêche le vol : réserve toujours fermée, aucune nouvelle
demande, aucun don fictif dans la fenêtre testée. Capture versionnée, mêmes
monde/rendu après recharge et 100 dixièmes d'un bloc ou 50+50. Le compteur 219
regroupe le but et ne prouve pas ce changement de moyen : **alerte brute
conservée, répétition fautive écartée à la lecture ciblée**, sans modifier le
compteur ni certifier l'absence générale de boucles.

**Mesures initiales réutilisées**, `f34e6c2` contre `adb52c4`, 20 paires × 4 h ;
pas de nouveau banc global ni de Luna. Suspects bruts **2 → 2**, zéro
plantage/usurpation. Retournements **1 555 → 722**, en baisse dans les cinq scénarios.
Hameau S/F/D **35/8/2,625 → 27,75/7,25/2,375**, S **[26–44] → [17–37]**,
échanges acceptés **13 → 9** : baisse acceptée, aucun gain uniforme revendiqué.

**Validation de reprise.** **31 ciblés + 19 tests de pas verts** ; cas réel
Brune/Ilse hameau 1985, autre scénario Relais, inconnu anonyme, méprise et
recharges/découpages conservés. **Suite complète unique : 2 549 tests / 294 fichiers, 2 430,801 s,
quatre échecs, zéro erreur et zéro ignoré.** Aucun des cinq écarts repris ne
revient ; les neuf tests de `test_dynamique_besoins` (229) passent.
Restent **trois préexistants** reproduits lors de la première livraison sur
`adb52c4` : torche du hameau 1985 (ici perte permise après départ cru), deux
MiMo `6 != 5` ; et **le placement d'Ilse du 195 réservé au 234** (distance
finale 4 au lieu de ≤ 1). La suite reste non verte, sans nouvel échec identifié.
Le test de stabilité de Lucien du 229 est intégré ; placement réservé au 234.
Bruts dans
`C:/Users/msics/donjon/artifacts/pas-233/reprise/` : diagnostics comparés,
empreintes, captures, contrôle AST, résultats ciblés et suite. Deux travailleurs
réduits au maximum ; aucun Luna. Scripts de génération et traces restent dans
les bruts ; les deux checkpoints et les empreintes attendues sont versionnés.

Créneau dépassé par la suite complète unique et son attente ; aucun second lancement.
