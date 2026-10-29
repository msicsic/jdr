# Lot 340 — A5.8, ascendant et issue perçue du mandat

Branche `codex-ascendant-evolue`, **non fusionnée**, base fournie `9f261f9`,
30 octobre 2026. **Lot terminé après synchronisation**, fusion `a5368a3`,
branche poussée vers `origin`. Validation initiale du moteur `14ba7f2` verte.

**Synchronisation terminée.** `origin/integration 64130fa`
(336, G5 et G6) fusionnée sans rebase par `a5368a3`, à deux parents
(`1dbd57e`, `64130fa`). Conflit de `planification.py` résolu
par l'union des lectures : mandats perçus, engagements de protection et
agendas d'origine contrat dans `_entrees_communes`. Fusions automatiques
d'`agendas.py` et d'`echanges.py` relues ; les deux invariants conservés.
Documentation des deux côtés retenue. **442 tests / 44 fichiers : 441 verts,
un échec antérieur, aucune erreur ni saut, 420,721 s**. Les treize scènes du
340 et les huit tests du 336 passent. L'unique échec de
`test_appel_reconnu_et_course_reels_sur_agenda_seul` attend `echoppe` alors
que Gorm est à `chambre_cloche`. **Même échec sur la référence exacte
`64130fa`, fichier 5/6, 6,455 s** ; traces identiques hors chemins absolus.
Test inchangé ; aucun échec nouveau. Empreintes des sources/tests identiques
à celles de la passe. Deux travailleurs réduits au plus, aucun nouveau banc,
Luna ou suite complète, aucun calcul actif. Bruts dans
`C:/Users/msics/donjon/artifacts/ascendant-340/fusion-64130fa/` :
`tests.json`, `reference-tests.json`, `analyse-cloture.json`,
**`fin-cloture.json ok=true` avec réserve explicite** ; bilan brut
`fin.json ok=false` et erreur d'import initiale du lanceur conservés.

**Invariant et réalisation.** `relations.EPREUVES` reçoit trois épreuves :
réussite **+10**, échec/renoncement **−10**, abus **−20**, sur l'ascendant.
Bornes, hystérésis, ancrages et estompement restent communs. La preuve durable
identifie la charge et l'issue ; elle survit aux quarante souvenirs et à la
recharge. Un constat complète seulement la part manquante d'un ouï-dire,
sans deuxième gain entier ; le passage du temps ne réarme aucune preuve.

`agendas._actualiser_epreuves` utilise les fins du titulaire et les connaissances
du témoin. Un compte rendu cru pèse **la moitié de son poids de source** ;
un doute ou une voix non attribuée n'établit aucune issue. Le témoin conserve
son contrat entendu dans le registre facultatif `mandats_percus`, validé à la
recharge et réservé à la façade par le contrôle AST. Il ne lit pas l'avancement
privé du titulaire. Sans contrat connu ni compte rendu, voir une arrivée ne
révèle pas un mandat. Après constat d'une réussite, un déplacement ultérieur
ne transforme pas cette réussite en échec.

L'abus reprend les prédicats disponibles : péril d'eau ou violence active crue
au lieu imposé ; transmission contraire à une croyance du titulaire, au
`prix_faute` commun d'honnêteté. L'effet de cette faute est pondéré par
`min(1, prix / FAUTE)` ; une faute interdite ou le péril prend le plein poids.
Le jugement conserve aussi l'abus d'un **ordre refusé**. Tentative, confirmation
et acceptation partagent sa preuve, sans plusieurs pénalités. Le témoin juge
l'ordre effectivement entendu selon ses propres connaissances et valeurs ;
un simple compte rendu d'issue n'annonce pas un abus.

**Chaîne et portée.** `echanges.executer` transporte le contrat déjà prononcé
comme contenu PNJ `ordre_mandat`, par `social.recevoir` et l'ouïe commune :
aucune parole automatique ajoutée. `paroles.TYPES_JOUEUR` reste inchangé.
`agendas.evaluation` diffère registre et épreuves jusqu'à la publication du
choix ; interruption et devis ne publient rien. La nouvelle lecture figure
dans `planification._entrees_communes`. Aucun scénario, modèle, MJ, réputation
publique, sanction ni règle de violence modifié.

**Preuves initiales. 218/218 tests, 23 fichiers verts, 186,271 s**, zéro échec,
erreur ou saut. Treize nouvelles scènes : Gorm → Aubin, puis Bram → Josse à la
mine, réussite/échec/abus ; marche et parole réellement exécutées, ordre refusé,
témoin ignorant, doute, voix inconnue, ouï-dire puis constat, mémoire courte
saturée, estompement, publication imbriquée et interruption. Monde complet,
rendu, scène et paroles entendues sont comparés après recharge. Les fins au
hameau et à la mine sont identiques en laps entier/découpé. Les essais initiaux
et leurs prémisses corrigées restent archivés, sans effacement des échecs.

**Banc rapide : 20/20 paires conformes**, 4 h, Relais/mine/auberge/crue/hameau
× 1985/7/42/2024, référence exacte `9f261f9`. Suspects 219 **0 → 0 dans chaque
nuit**, zéro plantage/usurpation. Chroniques, mesures de jeu, avis et constats
d'audit identiques nuit par nuit. **Aucun mandat naturel, donc aucun mandat
abouti** : la preuve du nouveau comportement passe par les scènes.
Les vingt références exactes manquantes ont été calculées/rangées une fois
dans le cache commun ; aucune référence disponible relancée. Aucun bilan de
performance déduit des temps. `tools/valider_ascendant_340.py` : **fin.json
ok=true**, codes tests/banc **0**, **1 137,994 s**, deux travailleurs réduits
au plus ; ni Luna ni suite complète. Empreintes du code/tests inchangées
avant/après et encore identiques au moteur livré à la clôture.

**Limites.** Les croyances peuvent être fausses : ce lot fait évoluer une
autorité subjective, pas une vérité publique. L'abus est établi par les
prédicats ci-dessus ; aucune inférence générale sur une morale narrative,
un risque de trajet non calculé ou une violence future n'est garantie.
Recouvrements à intégrer : **336** (`agendas.py`, `echanges.py`,
`planification.py`) ; **337** (`agendas.py`, `social.py`, `planification.py`).
Bruts : `C:/Users/msics/donjon/artifacts/ascendant-340/` : `tests.json`,
`comparaison.json`, `bilan.json`, `debut.json`, `fin.json`, journaux et
`analyse-cloture.json` (lecture des résultats existants, sans rejeu).
