# Tâche Codex 351 (refonte G18) : un avis reste un jugement cru et une parole enregistrée

Lot de la refonte du MJ, après G15 (émissions de parole), G16 (information parlée, lot 345), G17 (comptes parlés), U-P
et U-C, tous fusionnés. Lis `AGENTS.md` (« Contrat du MJ »), `docs/etat-dev.md` (court), `docs/plan-refonte-mj.md`
(ligne G18), `docs/conception-refonte-mj.md` (G15 à G18) et les rapports 345 (G16) et G17, dont tu reprends la forme.
Pour les lots anciens sur les avis (121 disputes, 124/128 avis du joueur, 164 avis saisis), cherche dans
`docs/historique-lots.md` par mot-clé, sans le lire en entier.

## L'invariant
**Une réplique d'avis dont le moteur fixe le contenu (sujet, valeur, conviction, adoption, dispute) est formulée par le
moteur, sans reformulation ni audit de réplique par Luna ; elle établit qu'elle a été dite et entendue, jamais que la
menace annoncée est vraie.** Un avis contraire reste une parole conservée avec sa source ; l'adoption et la dispute
restent des issues du moteur, distinctes de la vérité du monde. Même voie pour l'avis du joueur (contenu typé `avis`,
consentement U-C conservé) et pour l'avis d'un PNJ entendu par Corvus.

## Fichiers attendus
`donjon/paroles.py` (réplique des avis), formateurs communs déjà employés par G16/G17, `donjon/emissions.py` si la
source typée l'exige. Ne touche ni `page.html` (lot 349), ni `agendas.py`/`echanges.py`/`biens.py` (lot 350), ni les
règles de réception des avis (`social.py`, poids des sources, dispute) : seul leur rendu change.

## Vérification
- Avis du joueur positif et négatif, avis d'un PNJ entendu, avis contraire puis dispute ; deux lieux ; monde, paroles
  entendues, croyances et rendu identiques après recharge ; zéro appel de reformulation ou d'audit sur ces répliques.
- Bancs Luna ciblés, **une passe** : `avis-joueur`, `echanges` (et un script de dispute si existant), sur copies.
- Tests ciblés et voisins (`test_emissions_parole`, `test_contenus_parole`, tests d'avis et de disputes, consentement).
  Les tests d'actes lourds passent « tenter » via `suite=("tenter",)` du harnais `jouer` (lot 325).
- Pas de suite complète, ni banc long.

## Contraintes
**Poste : le laptop.** Deux processus au plus, priorité réduite. Lots en cours : 342 (attribution du groupe 1), 349
(U-M passage), 350 (E2) ; signale tout fichier commun.

## Livraison
- Branche `codex-g18-avis`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur ; la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-351-g18-avis.md`, entrée « non fusionnée » de 8 lignes au plus dans
  `docs/etat-dev.md`, section « Lots non fusionnés ».
- Bruts dans `C:\Users\msics\donjon\artifacts\g18-351\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
