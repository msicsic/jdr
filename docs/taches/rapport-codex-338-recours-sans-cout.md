# Lot 338 — Deviser et conserver le recours jusqu'au constat

Branche `codex-recours-sans-cout`, **non fusionnée**, base `integration e37d9ee`.
Code prêt à vérifier ; passe ciblée élargie et bancs détachés, clôture en attente.
Bruts : `C:/Users/msics/donjon/artifacts/recours-338/`, fichier final `fin.json`.

**Invariant et correction.** `agendas.planifier` exige un coût fini pour toute
proposition admissible. Les branches de recherche conservent leur coût complet
(reprise du bien, acquisition monétaire, garde comprise). Les suites directes,
dont inspection et attente, passent par `planification.mesure_recours` : approches,
gestes et pression aux tarifs communs ; une attente sans geste coûte zéro,
un moyen impossible n'a pas de mesure. `duree_devis` partage cette composition
physique sans convertir la pression en durée. `choisir_mandataire` refuse un
recours propre sans devis fini ; seul l'absent reçoit l'infini.

Le contrat d'intention conserve dans l'esprit l'empreinte des entrées ayant
justifié son recours. `deliberation.choisir` garde son suffixe admissible jusqu'à
son terme, ou son attente déjà adoptée, tant que ces entrées ne changent pas.
Le déplacement propre et les dates de regard ne rouvrent pas les moyens ; les
états crus, possessions, accords, refus, relations et échéances le peuvent.
Un geste démenti, une inadmissibilité, la fin du projet ou une urgence concurrente
gardent leurs contrôles existants. Aucun changement d'`INERTIE`, délai ajouté,
lieu interdit, identité de PNJ ou sorte d'agenda codée dans cette continuité.
Les lectures nouvelles de composition utilisent la Vue et ses tarifs existants ;
aucune entrée nouvelle de recherche mémorisée hors de `_entrees`.

**Preuves préalables.** Cinq nouvelles régressions vertes, 24,354 s : capture
réelle du 317 crue 3 à 160 min ; inspection et attente confrontées à une
délégation possible ; suffixe de l'agenda `informer` conservé après déplacement,
rouvert sur une localisation nouvelle ; attente `garder` à l'auberge ; refus
des coûts absents, infinis ou NaN. Monde complet, rendu et scène contrôlés
après recharge. Le cas réel est joué sur 15 min, d'un bloc ou minute par minute,
avec recharge à chaque frontière : états finaux identiques. Gorm inspecte la
galerie à 170 min, y connaît Ilse et ne repasse plus entre 171 et 175 min.
Cela ne certifie pas l'achèvement de tout l'agenda, qui vise aussi Brune.
Autre scénario : garde à l'auberge, même laps de 3 min entier ou découpé.
Premier précontrôle existant : 16 tests verts, 21,873 s. Ces précontrôles
précèdent la validation consolidée du code final ; ne pas les additionner.

**Calculs et limites.** Le lanceur enchaîne les fichiers ciblés (deux travailleurs
réduits), le banc 4 h × Relais/mine/auberge/crue/hameau × quatre graines, puis
crue 3 sur 12 h et son maximum horaire des passages de Gorm. Référence figée à
la base d'intégration, recherchée dans le cache commun ; seules les références
manquantes sont calculées une fois, avant la branche. Aucune comparaison de temps
avec les références en cache. Les suspects 219 sont comparés nuit par nuit,
avec plantages et usurpations dans `criteres-4h.json`. Résultats consolidés et
maximum sur 12 h **encore à établir**. Aucun Luna, suite complète ou correctif
du contact Aubin/Sève. Les devis portent sur le prochain sous-but ; ils ne
garantissent ni l'accord futur ni la réussite du projet. L'empreinte est une
invalidation conservatrice des moyens connus, pas une preuve causale minimale.
