# Tâche Codex 388 : rembourser volontairement une dette en pièces

Mécanique décidée par l'utilisateur le 2026-10-31, relevée par le lot 380 (U-M social comptes) : le moteur sait
**réclamer** un dû (`paroles` contenu `reclamer`, `biens.regler`), **rendre** une contrepartie impayée
(`biens.rembourser`, `solder`), restituer un prêt et exécuter un échange convenu, mais il n'a **aucun acte typé pour
qu'un débiteur rembourse de lui-même une dette en pièces**. Lis `AGENTS.md`, `docs/etat-dev.md` (court),
`docs/mecaniques.md` (« Prêter, confier, payer ») et le rapport 380 (`docs/taches/rapport-codex-380-*.md`).

## Invariant (un seul)
**Un débiteur, joueur ou PNJ, peut rembourser de lui-même tout ou partie d'une dette en pièces qu'il croit devoir, par
un acte commun et typé : le moteur vérifie la dette, la présence et l'audience du créancier, la bourse du débiteur,
transfère les pièces, solde la ligne de dette, et enregistre la parole et ses conséquences avant l'affichage ; la
remise est perçue par le créancier, qui en tire l'épreuve relationnelle existante d'une dette honorée.** Un
remboursement partiel laisse le reste dû ; un montant supérieur au dû est refusé avec `attendu` (le dû exact) ; une
dette inconnue, un créancier absent ou une bourse insuffisante ont chacun leur propre refus. Aucune exception de
scénario.

- **Joueur** : contenu de parole typé (par exemple `rembourser {montant}`, montant vide = tout le dû envers ce
  destinataire), dans le contrat commun des contenus (`paroles.TYPES_JOUEUR`, `CHAMPS_CONTENU`, `SENS_CONTENU`), avec
  « Compris : … » avant exécution (acte à effets : consentement U-C) ; le compte affiché vient de `biens.comptes_joueur`.
- **PNJ** : le même acte devient un geste du planificateur, choisi selon les valeurs existantes : c'est le pendant
  volontaire de `biens.garde_du` (garder l'argent dû est déjà une faute au prix de l'honnêteté). Il ne doit pas
  provoquer de remboursements en boucle ni de redites : un remboursement fait, la dette est soldée.
- Pas de nouveau registre d'esprit (S1 en cours) : la dette reste dans `data["dettes"]`.

## Vérification
Cas réel et autre cas après recharge, même laps entier/découpé : Corvus rembourse Brune en entier, puis partiellement
un autre créancier ; un PNJ débiteur honnête rembourse sans être réclamé ; refus d'un montant trop fort, d'une dette
inconnue, d'un créancier absent. État complet (bourses, dettes), paroles entendues, rendu et fiche après recharge.
Tests touchés (`echanges_suite`, `taches_payees`, `comptes`/G17, `propositions`, U-C). Banc rapide 4 h, quatre
graines, Relais et auberge (changement de comportement des PNJ). Luna : une passe ciblée sur une saisie libre de
remboursement (le banc `comptes` ou un script dédié), sur copie. Pas de suite complète.

## Contraintes
**Poste : le laptop.** Lots voisins : 380 (U-M social comptes, `web/page.html`, `dialogues.py`) ; S1
(`donjon/memoire.py`, `esprits.py`) : touche le moins possible leurs fonctions. Le raccourci de menu viendra dans un lot
U-M/U-T ultérieur. Deux processus au plus, priorité réduite, calculs longs détachés. La poussée de ta branche vers
origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) est autorisée.

## Livraison
- Branche `codex-rembourser-dette`, base `integration`, poussée vers origin.
- Rapport d'une page `docs/taches/rapport-codex-388-rembourser-dette.md` ; entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\rembourser-388\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
