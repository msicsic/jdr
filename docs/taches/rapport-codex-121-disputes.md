# Lot 121 — Disputes entre PNJ

Base `0a53910`, branche `codex-disputes`, non fusionnée. Sans Luna, changement de scénario,
de `planification.py` ou de `main`. Calculs à priorité réduite, deux processus au maximum.

**Invariant.** Un avis contraire entendu se conteste par la parole commune, dans un épisode fini.
`social.faire_entendre` photographie les preuves des auditeurs et ouvre la contradiction avant
que les témoins adoptent le premier argument. Une réponse si le locuteur tient encore au sien,
puis un éclat seulement si fierté > 60 ou colère ≥ 20. Les témoins qui saisissent les deux
positions pèsent les sources par confiance × affection × conviction ; à égalité, jet opposé
d20 + modificateurs CHA/ELO ; nouvelle égalité : doute ou conservation. Une seule position
entendue reste un avis ordinaire. Les égalités numériques sont comparées à douze décimales.

`ouie` porte l'éclat à 6 crans (voix 4, bruyant 7), avec mots, voix et réaction communes ;
`ecoute` rend aussi les éclats indistincts. `faits_dits` suit les positions réellement entendues
pendant l'épisode, y compris les prises de parti, hors mémoire courte. `relations` applique
`dispute_perdue` (+10 rancune × fierté) et `parti_pris` (+3 affection du soutenu envers le témoin).
Les suites exigent un parti pris audible et une identité reconnue ; aucun coût de mensonge
pour une simple divergence de prévisions. Les marqueurs de chronique sont validés et mesurés
par `pnj`/`banc_pnj`.

**Preuves ciblées.** Scènes d'auteur sur la crue 500 : Aubin/Ilse au refuge, puis Ilse/Aubin
au palier des vannes. Prévisions opposées, Gorm adopte la source mieux étayée ; rancune et
affection enregistrées, joueur présent lisant la dispute. Éclat entendu de l'échoppe, Brune
courageuse invitée à aller voir par `bruit_a_voir`, paroles entendues par le joueur restituées après recharge.
Absence de nouvel épisode au tour suivant même après oubli ; même monde complet, chronique
et rendu après deux minutes d'un bloc ou par quinze secondes sauvegardées. Égalité des poids,
égalité des jets, constat propre prioritaire, surdité et absence de fierté également contrôlés.

**Banc rapide.** 4 h × crue/Relais × graines 1985/7/42/2024, huit références `0a53910`
reprises du cache après leur premier calcul. Huit états finaux et huit chroniques identiques.
Crue : 18 → 18 avis, zéro adoption ; Relais : zéro avis. Aucune dispute, aucun éclat ou parti
pris naturel dans ces nuits ; leur preuve demeure ciblée. Aucun plantage, usurpation ou
violation ; mêmes alertes `voir_alterne` (crue 42), `eau_longue` (crue 2024), `fige_presse`
(trois Relais). Les temps du cache ne sont pas comparables. Le resserrement final du relais
de conviction ne concerne que les prises de parti, absentes de ces nuits.

**Tests.** Reprise finale : **53 tests verts, sept fichiers, 68,01 s**, un processus réduit.
Elle inclut les resserrements faits après le lancement de la suite : destinataire initial
soumis au même arbitrage, conviction propre du partisan relayée, légende de l'éclat.
Suite complète unique : **2 045 tests, 16 ignorés, aucun échec/erreur**, 221 fichiers,
deux processus réduits, **1 919,09 s**. Bilan consolidé vert ; aucune seconde suite complète.
Bruts : `artifacts/disputes-121/`.

**Limites.** Menace d'eau uniquement, parole typée du joueur différée. Scènes d'auteur,
sans garantie de fréquence naturelle ni d'amélioration de la justesse des avis sur huit graines.
L'éclat s'entend selon la géométrie, les portes et les capacités de chacun ; il ne franchit pas
toute distance. Le désaveu repose sur les partis exprimés devant les deux orateurs, pas sur
la vérité cachée de la crue ; une erreur future n'est donc pas qualifiée de mensonge ici.
