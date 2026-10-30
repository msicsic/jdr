# Lot 343 — G7, déplacements résolus

30 octobre 2026. Branche `codex-g7-deplacements`, base exacte `dc6da62`.
**Lot terminé, non fusionné ; branche poussée, aucun calcul actif.**

Le moteur enregistre les mouvements réellement accomplis du joueur : acteur,
opération, quantité, unité, direction et bornes temporelles. `Moteur._appliquer`
relève les mutations physiques ; la fin d'étape borne leur durée. Le traînage
différé est relevé à son échéance dans `tenir.finir_trajet`, depuis sa durée
commune, sans changer le contrat des gestes sauvegardés.
`deplacements.clore/phrases` construit le cumul depuis cette structure, jamais
les lignes de texte, puis sert aussi les attestations exactes du lot 95.
Les directions successives restent ordonnées ; sans métrique, un passage ne
s'invente pas de distance. Sons et événements gardent leurs lignes distinctes.
Journal et rendu précèdent la sauvegarde et l'affichage commun G4.

Le clic transmet l'identifiant du trajet et les directions encore choisies.
Chaque pas reste indépendant et revalidé ; seuls les mouvements enregistrés
d'une continuation immédiate sont cumulés. Interruptions, nouveau clic et
reliquat sont conservés ; la fuite conserve aussi son reliquat. Les
reformulations libres restent auditées. `jeu.py` et `transactions.py` intacts.

**235 tests distincts / 17 fichiers verts**, sans saut, 452,374 s cumulées des
fichiers retenus : G4, U-D, U-T, véritable sonde JavaScript du clic, ponts
web/TUI, moteur, opérations, temps et narration. Monde complet, texte, scène
et carte vérifiés après recharge ; sauvegarde avant affichage, reprise exacte
sans audit. Refus avant premier pas, faisabilité, faux total, nouveau clic,
trois pas arrêtés au deuxième, traînage Relais/auberge et obstacle couverts.
Le script réel `force-4c-fuir` accomplit **trois pas sur cette base** (nord,
nord-ouest, ouest), contre deux au diagnostic 171 ; autre départ à deux pas
vérifié. Les sons à l'ouest ne comptent jamais comme mouvements du joueur.

**8/8 empreintes 2 h identiques**, Relais/auberge × graines 1985/7/42/2024 :
état complet, chroniques, récits, souvenirs et mesures ; zéro plantage.
Huit références exactes absentes calculées/rangées une fois, toutes relues du
cache à la reprise. Le premier rouge venait de la trace vide des attentes :
deux scènes comparées aux moteurs base/743e5e9/final prouvent cette cause
unique après recharge. La trace est désormais absente sans mouvement ; PNJ
inchangés. Les essais rouges, dont les erreurs initiales de fixtures, restent
archivés ; les fichiers corrigés sont verts.

**Luna : une passe**, fuite/traînage, 32,182 s. Deux résultats exécutés,
**zéro appel après confirmation**, récit, audit du total, erreur technique,
erreur de recharge, repli ou mention sans fondement. Brune rejoint la case
de départ du joueur ; leurs mouvements ne sont pas additionnés. Un refus de
fidélité subsiste avant traînage. Référence historique `cdaf371` entièrement
en cache, jamais relancée : 11 → 6 appels, trois audits narratifs → zéro ;
aucun gain causal attribué à G7. Six réponses rejouées hors réseau avec le
code final : textes d'exécution et états rechargés identiques au live.
Aucune seconde passe Luna, suite complète ou banc d'intégration.

Bruts : `C:/Users/msics/donjon/artifacts/g7-343/`, `tests-final.json`,
`empreintes-corrigees.json`, `analyse-cloture.json`, `luna/`,
**`fin-cloture.json`** ; fin initiale rouge `fin-validation.json` conservée.
Deux travailleurs réduits au plus pour les bancs. Recouvrements :
`narration.py` avec 341, documentation avec tous les lots ; aucun autre fichier
moteur commun identifié d'après les briefs 325/338/342. La preuve exacte ne
s'étend ni aux paraphrases ni aux cumuls des PNJ.
