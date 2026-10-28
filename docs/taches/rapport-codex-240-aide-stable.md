# Lot 240 — l'aide reste admissible après son adoption

28 octobre 2026, laptop. **Branche `codex-aide-stable`, non fusionnée**,
base intégration **`1c71666`**. Aucun Luna.

**Invariant.** Une demande d'aide, puis l'attente de sa réalisation, ne perdent
pas leur admissibilité parce que leur adoption reclasse le besoin `presse`.
`Vue.detresses` conserve désormais l'ouverture pour le motif d'une intention
vide tant qu'une aide acceptée reste connue et valide. Cette cause ne dépend
ni du classement du besoin ni de la phase du contrat : elle couvre aussi
l'intervalle où le geste `confier` vient d'être retiré. Le filtrage existant
des promesses (refus, confiance, échéance) précède cette lecture. Une phase
`attendre` ou un plan vide seuls ne prouvent pas un manque de moyens : une
garde tenue reste une garde. La recherche revalide les moyens et ne réinstalle
aucun ancien plan. Ses entrées de cache contiennent déjà détresses et aides.
Seul code du jeu modifié : `Vue.__init__`. Le contrat et la phase `attendre`
de `deliberation`, `_classer`, le MJ et le format des sauvegardes sont conservés.

**Cas réel.** Archives 237 absentes du laptop : rejeu séquentiel de
`4306c14` détaché, hameau 1985, départ tiré, joueur en chambre de la cloche,
jusqu'à 540 puis observation de 541–545. Captures versionnées à **541:0**
et **544:156** (instant **326556**). À ce dernier instant, Gorm attend le
brasero après l'accord d'Aubin pour rapporter les bûches du guet ; son choix
fait disparaître son propre recours sur la base.

Les tests vérifient des choix répétés avec classement `attente` puis `presse`,
la conservation du but et de sa phase, l'absence de feu inventé, monde et
rendu après sauvegarde/rechargement, cinq minutes depuis la capture 541
d'un bloc ou par quarts de minute, sans abandon de l'attente. Autre besoin
et scénario : Bram à la mine attend que Josse allume la chandelle ; réalisation
réelle, même laps découpé et annulation reçue sont contrôlés. Un plan vide,
même en phase `attendre`, sans promesse connue n'ouvre pas l'aide.

**Vérifications.** Contre-épreuve : les deux régressions historiques échouent
sur le constructeur exact de la base extrait par AST (22,827 s). La **suite complète unique**
a terminé **2 534 tests / 293 fichiers, 3 409,760 s, trois échecs, zéro erreur,
16 ignorés ; suite non verte**. L'ouverture par la seule phase `attendre`,
trop large, changeait les deux captures `test_etapes_chainees` : mine
8 471 → 12 825 visites, plans et monde modifiés ; auberge 14 489 → 16 274,
visites/diagnostics seuls. Remplacée par la promesse connue : **tous les
champs retrouvent exactement la base**, sans modifier ces oracles. Échec
de torche reproduit avec le constructeur exact de la base (16,358 s), mêmes
réussite à 3188 et perte à 3615, réserve du lot 238 ; même échec sur le raccord
final (15,217 s). **24 ciblés finaux verts** (quatre fichiers, 75,792 s), dont
les deux oracles historiques intacts. Banc final : **20 paires de quatre
heures**, vingt références réemployées, aucune rejouée, zéro plantage.
Suspects 219 **0/0/2/0/0 inchangés** (Relais/mine/auberge/crue/hameau),
cycles **507**, préemptions **58**, à expliquer **87** inchangés. **20/20**
états finaux, chroniques, récits, souvenirs et empreintes identiques ; seul
écart de compteur : recherches neuves **15 017 → 15 024 (+0,05 %)**.
Aucune comparaison de temps issus du cache.

**Limites.** Ce lot ne garantit pas l'absence de toute boucle entre besoins.
La fenêtre historique de la neuvième heure est rejouée sur capture ; le banc
de comparaison reste limité aux quatre heures demandées.
Une ancienne sauvegarde dépourvue de toute promesse connue ne permet pas de
reconstruire une cause d'aide déjà perdue.
Pas de seconde suite complète après le dernier raccord ; créneau de
30–45 minutes dépassé par les validations. Travailleurs à priorité réduite ; bruts dans
`C:/Users/msics/donjon/artifacts/aide-240/`.
