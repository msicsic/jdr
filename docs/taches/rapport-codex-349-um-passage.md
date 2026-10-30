# Lot 349 — U-M passage

Branche `codex-um-passage`, base intégration `a0f0eba`, **terminée, non fusionnée**.

## Invariant et changement

`gestes_publics.passages_publics` propose dessous/dessus sur un obstacle
perçu dont la forme est établie, le parcours d'une échelle installée et
le franchissement avec un appui mobile déjà arbitré. Gabarit, charge,
encombrement, état du matériel et jets restent jugés par le moteur.
La page reçoit les références et choix publics, sans dimensions,
préconditions ou difficulté à choisir. L'échelle se choisit sur son
support ou son marqueur au palier ; les homonymes gardent leur référence.

`commandes.passage_descripteur` revalide l'offre et construit le même plan
que la commande locale. `franchir <obstacle> avec <appui>` reprend le même
arbitrage mémorisé, avec prise au sol si nécessaire. Aucun analyseur ou MJ
n'intervient sur le clic. `moteur.preparer` réutilise la gravité U-C,
« Compris », les confirmations existantes et la revalidation exacte.
Le consentement conserve désormais **le descripteur et son origine d'entrée** :
l'origine d'un arbitrage mémorisé ne doit pas modifier ses sous-plans à la relecture.

Raccords nécessaires : extraction pure de `franchissement.cle_arbitrage`,
sans changement de signature ou de règle ; normalisation JSON récursive
des effets composés avant journalisation, pour garder les coordonnées
identiques à la recharge. Ni `obstacles.py`, MJ, `jeu.py` ou `tui.py` ne
changent. Aucun fichier de code commun avec les lots 345/348 ; `etat-dev.md`
est commun à la livraison.

## Vérification et mesures

**71 tests distincts validés, sélection dans sept fichiers : zéro échec,
erreur ou saut dans le bilan retenu.** 58 résultats conservés de la passe
`tests-cloture.json` ; reprise des dix tests de passages (206,146 s), de
la méthode TUI complète (113,633 s) et de deux contrôles corporels de
consentement (35,353 s). Aucune assertion d'état ou de recharge affaiblie.

Plans, effets, textes et monde/scène/fiche/carte comparés après recharge
dans la vraie boucle, avec MJ interdit et sauvegarde avant affichage.
Les sept bancs réels `sous-obstacle-*` sont repris sur copies : Relais,
auberge, enjambement, trop bas, trop haut, encombré et forme inconnue.
Échelle dans les deux sens, perche portée ou prise au sol, annulation,
référence/qualification périmée, paramètres injectés et homonymes couverts.
Un saut en contrebas contrôle aussi la trace persistante commune.

Les passes rouges restent archivées : attente de texte périmée reproduite
avec le moteur de la base, accès au palier et tuples imbriqués corrigés,
puis origine de revalidation corrigée. Le clic TUI d'offre sans effet dans
la passe de clôture ne s'est pas reproduit dans la méthode complète rejouée,
avec ses assertions intactes et sans modification du code TUI.

**10 parcours : 10 saisies évitées, 3 clics jusqu'à l'effet**, confirmation
comprise, cible à portée ; approche éventuelle en sus. Zéro appel au modèle.
Deux travailleurs au plus, priorité réduite ; ni suite complète, Luna ou banc PNJ.
Bruts : `C:/Users/msics/donjon/artifacts/um-passage-349/` ; preuves retenues :
`tests-cloture.json`, `reprise-passages.json`, `reprise-tui.json`,
`reprise-corps.json`, `mesures-cloture.json`, synthèse `fin-livraison.json`.

## Limites et livraison

Décision explicite de l'utilisateur : **le saut à la perche n'est offert
que pour une difficulté déjà mémorisée dans le même contexte physique**.
Un premier arbitrage reste au chemin libre du MJ ; le joueur ne choisit
pas sa difficulté. Une forme inconnue reste à qualifier séparément (G13).
Une offre ne promet jamais la réussite. U-T passage reste à faire.
Branche poussée vers `origin`, aucun calcul actif ; fusion laissée au superviseur.
