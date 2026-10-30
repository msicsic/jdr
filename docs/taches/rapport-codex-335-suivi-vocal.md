# Lot 335 — protéger à portée de voix

Branche `codex-suivi-vocal`, non fusionnée ; base initiale `9237e14`.
Reprise du 2026-10-30 : fusion sans rebase de `origin/integration c9b066b`.
Bruts : `C:/Users/msics/donjon/artifacts/vocal-335/reprise-c9b066b/` ;
validation initiale dans `vocal-335/verification/` du même dépôt.

**Invariant.** L'agenda protéger réutilise le séjour `rester` du lot 266,
avec une portée vocale typée. `planification.proximite` est commune au
contact et à la voix. `proximite_vocale.arrivees` utilise `ouie.propager`
et `parvenu` : voix ordinaire, distance, ouvertures et portes crues.
Seule l'oreille propre intervient ; aucune lecture des positions, de
l'oreille, du repos ou des trajets privés du protégé. Le devis et la marche
commune visent les mêmes arrivées, avec obstacles et tarifs communs.
La place admissible est conservée, sans rotation vers une cible inconnue.
Sans localisation, recherche commune payante ; sans case, inspection.
Les lectures acoustiques propres entrent dans `_entrees`.

L'agenda reste actif sans poste d'interposition ; les paliers supérieurs,
le secours et les fins sur mort/départ crus gardent leur contrat. Le rendu
« reste à l'écoute » affirme la veille sans révéler une présence cachée ;
son souvenir est sauvegardé avant affichage. Aucun agenda ajouté aux
scénarios historiques, aucun cas particulier de scénario ou personnage.

**Résolution des conflits.** Dans `planification._pulsion`, la demande de
cause de détresse précède toujours le séjour, et la durée du devis d'E3
reste transmise. `pnj._approcher` et `trajet_estime.approche` gardent à la
fois le terminal vocal et le contact matériel du 313 : perception fraîche,
localisation crue, observation et contrôle physique du geste. Les ajouts
332/333 et E1–E4/357 sont conservés. `etat-dev` reprend l'intégration,
avec une seule entrée 335 de cinq lignes dans « Lots non fusionnés ».

**Validation de reprise.** **414 tests / 50 fichiers, 409 verts, cinq échecs,
zéro erreur ou saut** : 356 tests en 242,771 s, puis 58 en 120,716 s.
Deux travailleurs au plus, priorité réduite. Les cinq échecs (trois ouïe,
deux boucles PNJ) sont reproduits avec **traces identiques hors chemins**
sur l'intégration intacte `c9b066b`, cinq rejeux en 3 s (`attribution.json`).
Aucun nouvel échec ciblé ; les cinq préexistants ne sont pas déclarés corrigés.
Les sept tests de suivi vocal passent : Relais et mine, repositionnement,
appel réel reconnu, recherche, désespoir prioritaire, portée limite stable,
portes crues, coût, invalidation par l'oreille et inspection sans case.
Monde complet, rendu et scène rechargés, laps entier/découpé identiques.
Contact 313, attention conjointe 332, gardes 333, cause de détresse,
agendas, délais E1–E4 et tâches payées 357 passent. Aucun test affaibli.
Les essais console retenus passent sans adaptation supplémentaire U-C.

**Banc de reprise en cours.** Branche seule, vingt nuits de 4 h, Relais,
mine, auberge, crue et hameau × 1985/7/42/2024 ; un travailleur réduit,
calcul détaché (`run_banc.py`), `bilan.json` puis `fin.json` écrit en dernier. Aucune des
vingt références compatibles de `c9b066b` n'est en cache : aucune référence
rejouée. Ni suite complète ni Luna. Avant réaccord : 131 tests verts et
20/20 nuits identiques à la référence compatible `f08ef58`, suspects 0→0 ;
ces résultats initiaux ne sont pas ceux de la nouvelle intégration.

**Limites.** L'écoute crue du protecteur ne garantit pas l'audition réciproque,
les retrouvailles générales ni la correction de toute croyance périmée.
Les déplacements et localisations du protégé sont des données d'épreuve ;
sa marche autonome entière n'est pas démontrée. Les nuits historiques sans
agenda nouveau ne prouvent pas le suivi actif ; celui-ci est éprouvé en tests.
Sans référence compatible, aucun delta ni identité avec l'intégration ne
sera certifié par le banc de reprise. Recouvrements 330 : planification/PNJ ;
333 : agendas/PNJ/protection.
