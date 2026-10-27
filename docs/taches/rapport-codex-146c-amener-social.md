# Lot 146 c — livraison partielle : route coupée

Branche `codex-amener-social`, **non fusionnée**, base `ef65e55`, code `fc3037c`.
Brief récupéré par avance rapide. **Sous-buts sociaux non livrés**, données de
la crue inchangées. Aucun Luna, fichier réservé, sauvegarde utilisateur ou `main` modifiés.

**Invariant.** L'absence de plan immédiat ne prouve pas l'impossibilité d'une route.
`agendas._route_coupee`, appelée par `actualiser`, conclut seulement si aucune
route ne relie une position crue de destinataire à la destination en retirant
les salles crues noyées, même avec toutes les portes supposées ouvertes. Une
serrure, une recherche bornée ou une position inconnue ne suffisent pas.
`abandonne`, cause `route crue coupee`, suit la publication différée du lot 146 b
et persiste après recharge, sans renaissance terminale.

**Mesures finales** (`artifacts/`, code figé) :

- **25 ciblés verts** : Ilse/galerie, Brune/palier et échoppe adjacente accessible ;
  évaluation sans publication, état complet et rendu rechargés identiques, cause
  conservée après réouverture crue. Croyances installées, niveaux réels non noyés.
- Suite complète unique : **2 188 tests, 249 fichiers, 1 293,96 s**, deux processus
  réduits ; deux échecs MiMo historiques `6 != 5`, zéro erreur/ignoré.
- **12/12 empreintes 2 h identiques** à `ef65e55`, Relais/mine/auberge × quatre
  graines. Premier témoin `main` `812ebe5` également identique ; nuits archivées
  du lot et de la base comparées directement hors ligne, sans rejeu.
- Crue 4 h × quatre graines : **4/4 états complets identiques** à `ef65e55`, mêmes
  chroniques, mesures et constats historiques ; zéro plantage/usurpation ou boucle
  nouvelle. Galerie **3/8**, eau **128,75 min**, attente urgente sans recours
  **60 min**, maximum horaire de passages **13,25** en moyenne : inchangés.
- `VERIFIER` + spatial 0,2, crue 42 fixe × 2 h sans arrêt. Coût crue 1985 fixe × 4 h :
  mêmes **1 430 recherches, 1 092 neuves, 83 066 nœuds**. Temps non comparés.
  Références manquantes calculées une fois, celles présentes relues.

**Tentative retirée.** Avis de menace, `confier`, marche propre et observation
passaient sur des parcours individuels et collectifs vers l'échoppe rechargés,
avec laps continu/découpé. Mais l'évacuation collective vers la galerie a révélé
un abandon d'engagement pendant les manœuvres de portes. Crue 2024 : arrêt à
**120 min**, `Passage incohérent`, dans la copie d'un devis ; l'invariant d'une
porte détruite/détachée ouverte et déverrouillée est violé, cause exacte non isolée.
Six constats de répétition, deux rafales, un va-et-vient et une alternance de buts.
Code social et déclaration de la crue retirés entièrement. Bruts : `amener-crue.json`,
`crue.log`, `tentative-sociale.diff`, tests et déclaration associés dans `artifacts/`.
Un ciblé de 13 s a chevauché le premier banc à deux travailleurs (pic de trois
calculs) ; l'enchaînement final a ensuite été strictement séquentiel, au plus deux.

**Reste.** Plus proche/portée vocale, avis/réception, demande autonome avec refus
durable/réveil, accompagnement, données de la crue et épreuve galerie/désespoir/laps
découpé. Aucun avis commun de préférence générale entre lieux : menace du lieu
quitté prévue comme recours. La coupure conservée ne couvre pas tous les obstacles
ni le danger dépendant de la durée ou d'une montée future. Aucune évacuation
spontanée revendiquée. Aucune clé Git de signature configurée : commits non signés.
