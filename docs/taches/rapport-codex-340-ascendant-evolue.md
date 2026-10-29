# Lot 340 — A5.8, ascendant et issue perçue du mandat

Branche `codex-ascendant-evolue`, **non fusionnée**, base fournie `9f261f9`,
29 octobre 2026. Code livré ; **validation finale détachée en cours**.

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

**Preuves acquises.** **19/19 tests verts**, dont treize nouvelles scènes et
les six tests du socle, en **23,603 s** : Gorm → Aubin, puis Bram → Josse à la
mine, réussite/échec/abus ; marche et parole réellement exécutées, ordre refusé,
témoin ignorant, doute, voix inconnue, ouï-dire puis constat, mémoire courte
saturée, estompement, publication imbriquée et interruption. Monde complet,
rendu, scène et paroles entendues sont comparés après recharge. Les fins au
hameau et à la mine sont identiques en laps entier/découpé. Passes voisines
acquises : 24/24 puis 31/31, avec recouvrement. Les essais initiaux et leurs
prémisses corrigées restent archivés, sans effacement des échecs.

**Validation finale à lire.** `tools/valider_ascendant_340.py` lance les
**23 fichiers ciblés**, puis **20 paires de nuits de 4 h**, cinq scénarios ×
quatre graines, référence exacte `9f261f9`. Cache commun réutilisé ; seules
les références manquantes sont calculées/rangées. Critère par nuit : suspects
219 sans hausse, zéro plantage et zéro usurpation. Le bilan compte les mandats
naturels et leurs réussites ; **leur exercice naturel n'est pas encore établi**.
Empreintes du code/tests avant/après ; deux travailleurs réduits au plus.
Ni Luna ni suite complète. Fin écrite en dernier :
`C:/Users/msics/donjon/artifacts/ascendant-340/fin.json`.

**Limites.** Les croyances peuvent être fausses : ce lot fait évoluer une
autorité subjective, pas une vérité publique. L'abus est établi par les
prédicats ci-dessus ; aucune inférence générale sur une morale narrative,
un risque de trajet non calculé ou une violence future n'est garantie.
Recouvrements à intégrer : **336** (`agendas.py`, `echanges.py`,
`planification.py`) ; **337** (`agendas.py`, `social.py`, `planification.py`).
Bruts, tests, journaux, bilan et empreintes :
`C:/Users/msics/donjon/artifacts/ascendant-340/`.
