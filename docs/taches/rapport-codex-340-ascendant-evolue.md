# Lot 340 — A5.8, ascendant et issue perçue du mandat

Branche `codex-ascendant-evolue`, **terminée, non fusionnée**, 30 octobre 2026.
Base initiale `9f261f9`, moteur initial `14ba7f2`. Intégrations `64130fa`
(336/G5/G6) et **`c9b972b` (G17/326 et 337)** fusionnées sans rebase par
`a5368a3` puis **`c84ba5a`**, ce dernier à deux parents (`e29d1bd`, `c9b972b`).
Branche poussée vers `origin`, aucun calcul actif.

**Invariant et réalisation.** `relations.EPREUVES` reçoit réussite **+10**,
échec/renoncement **−10**, abus **−20** sur l'ascendant, avec les bornes,
l'hystérésis et l'estompement communs. La preuve durable identifie charge et
issue : mémoire courte, délai et recharge ne réarment aucun effet. Un compte
rendu cru pèse la moitié de son poids de source ; un constat complète seulement
la part manquante. Doute et voix non attribuée n'établissent aucune issue.

`agendas._actualiser_epreuves` lit les fins du titulaire et les connaissances
du témoin. `mandats_percus`, facultatif, validé à la recharge et réservé à la
façade par le contrôle AST, conserve le contrat effectivement entendu. Aucun
avancement privé n'est lu par le témoin. `echanges.executer` transmet l'ordre
par `social.recevoir` et l'ouïe commune (`ordre_mandat`, PNJ seulement), sans
nouvelle parole automatique. `agendas.evaluation` diffère registre et épreuves
jusqu'à la publication du choix ; interruption et devis ne publient rien.

L'abus reprend le péril d'eau ou la violence active crus au lieu imposé, ou
une information contraire aux croyances au `prix_faute` d'honnêteté : poids
`min(1, prix / FAUTE)`, plein poids si interdit ou périlleux. L'ordre refusé
compte aussi ; tentative et acceptation partagent la preuve. Un simple compte
rendu d'issue ne prétend pas rapporter un abus.

**Fusions.** Premier conflit de `planification.py` : union des mandats perçus,
engagements de protection et agendas contractuels dans `_entrees_communes`.
Seconde fusion : aucun conflit de code ; filtrage des preuves négatives de fin
du 337 conservé. Dans `test_agendas_socle.py`, contrôle AST du 340 et prémisse
d'inventaire du 337 coexistent. Conflits documentaires : deux côtés conservés.

**Validation après G17/337 : 495 tests / 48 fichiers, 492 verts, trois échecs
antérieurs, aucune erreur ni saut, 536,659 s.** Les treize scènes 340, quatorze
tests de garde par ouï-dire et onze de comptes parlés moteur passent. Gorm →
Aubin et Bram → Josse : réussite, échec, abus, marche/parole réelles, témoins,
doute, ouï-dire puis constat, mémoire saturée, publication et interruption ;
monde/rendu/scène/paroles rechargés, temps entier/découpé.

Les deux échecs `test_ouie_temoins` concernent les nouvelles de Bram ; celui de
`test_voix` attend une persuasion crue après l'appel d'Hugues, obtenue douteuse.
**Référence exacte c9b972b : mêmes trois échecs, 28 tests / deux fichiers,
18,878 s**, traces identiques hors chemins. Assertions inchangées ; aucun
échec nouveau, sources/tests vérifiés inchangés. Bilan brut rouge conservé.
Première synchronisation : 441/442 verts, un appel sur agenda déjà en échec
sur `64130fa` ; réserve conservée, non réexercée par la dernière sélection.

**Mesures initiales, avant synchronisations.** 218/218 tests verts ; 20/20
paires de nuits de 4 h, cinq scénarios × quatre graines, suspects 219 **0 → 0
par nuit**, zéro plantage/usurpation, chroniques/mesures/avis/constats identiques.
Aucun mandat naturel : preuve du comportement par les scènes. Vingt références
exactes absentes rangées une fois ; aucune disponible relancée. Aucun bilan
de performance déduit. Aucun nouveau banc après fusion, ni Luna ou suite complète ;
deux travailleurs réduits au plus.

**Limites.** Autorité subjective, croyances possiblement fausses ; aucune
réputation publique ou sanction. Pas d'inférence générale sur une morale
narrative, un risque de trajet non calculé ou une violence future.
Bruts `C:/Users/msics/donjon/artifacts/ascendant-340/`, puis
`fusion-64130fa/` et **`fusion-c9b972b/`** : tests, témoin exact,
`analyse-cloture.json`, **`fin-cloture.json ok=true avec trois réserves`** ;
`fin.json ok=false` brut préservé. Aucun acquis rejoué à la clôture.
