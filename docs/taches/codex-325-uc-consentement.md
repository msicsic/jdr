# Tâche Codex 325 : U-C, le consentement aux actes lourds du texte libre

Lot U-C de la [feuille de route de la refonte du MJ](../plan-refonte-mj.md), après U-P (lot 319, branche
`codex-up-recapitulatif`, livrée et en attente de fusion). **Base : la branche `codex-up-recapitulatif`**, pas
`integration` : U-C s'appuie sur le récapitulatif « Compris : … » et sa fiche. Lis `AGENTS.md` (contrat du MJ,
« Fidélité de la saisie »), `docs/conception-valeur-llm.md` (décision « Fidélité : option c avec b en filet », ligne U-C et
le paragraphe « U-C doit couvrir les actes lourds… ») et le rapport 319.

## L'invariant
**Tout acte lourd ou irréversible issu d'une saisie libre (paiement, offre engagée, avis, enfermement, violence, et tout
autre effet de même nature) montre le plan entier par sa ligne « Compris » avant exécution, et ne s'exécute qu'après
`tenter` ; `annuler` le laisse sans aucun effet. À la confirmation, le moteur revalide le plan : un changement pertinent du
monde depuis l'aperçu impose un nouvel aperçu au lieu d'exécuter l'ancien.** La gravité se décide **sur les effets typés**
du plan (une classification commune aux transactions et aux plans composés ; une étape lourde suffit à faire montrer toute
la composition), jamais sur une liste de formulations, de verbes ou de noms d'objets. Les actes légers gardent l'exécution
puis la ligne de résultat (U-P). Un clic ou un menu n'ajoute aucun contrôle de fidélité.

Ce qui ne change pas : contre-revue et fidélité de parole restent sur les actes à effets issus du libre (transition) ;
aucun audit retiré ; aucune nouvelle consigne au modèle ; aucun appel au modèle après la confirmation sauf une nouvelle
admission réellement nécessaire.

## Vérification
- Un paiement, puis un enfermement ou une violence, et un acte de même gravité par un autre chemin (plan composé où une
  seule étape est lourde) : aperçu, annulation sans effet (monde identique), confirmation qui exécute ; plan périmé entre
  aperçu et confirmation (cible partie, prix changé) qui redemande l'aperçu. Console, TUI et web, avec MJ simulé sans
  réseau ; état, mots entendus, texte sauvegardé et rendu identiques après recharge.
- Un acte léger reste exécuté sans fiche ; un clic sur un geste lourd n'ajoute pas de fiche de fidélité.
- Mesure : saisie → aperçu, puis confirmation → effet, temps humain séparé ; appels au modèle après confirmation = 0
  sur ces parcours.
- Tests ciblés des fichiers touchés, dont les 28 tests TUI existants inchangés. Pas de Luna, de banc ni de suite complète.

## Contraintes
**Poste : le laptop.** Deux processus au plus, priorité réduite. Recouvrements connus : lot 321 (fabrication au terminal,
`jeu.py`, `tui.py`) et lot 323 (G5, `jeu.py`, `rendu.py`) ; signale-les dans le rapport.

## Livraison
- Branche `codex-uc-consentement`, base `origin/codex-up-recapitulatif`, poussée vers origin
  (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur : la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-325-uc-consentement.md`, entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\uc-325\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
