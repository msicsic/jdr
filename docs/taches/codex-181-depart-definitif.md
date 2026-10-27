# Tâche Codex 181 (A4b, décision du 2026-10-27) : partir des lieux, et la fin de « protéger » sur départ cru

Décision de l'utilisateur, 2026-10-27 : ajouter la notion de **départ définitif**, absente du monde (lots 167 c et 175 : une
position inconnue ne termine rien, et rien ne distingue un départ d'une absence). Lot de 30 à 45 minutes (`AGENTS.md`) ;
livraison partielle permise si elle dit ce qui reste. Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot tourne sur ce poste (180 : `narration.py`, `mj.py`) : au plus
2 processus de calcul, priorité réduite. Ce lot touche le monde et la marche (issues et état de présence), `esprits.py`,
`agendas.py`, la perception si nécessaire, le scénario dérivé `scenario_crue_hameau.json` et leurs tests ; **pas** `narration.py`,
`mj.py`, `consignes.py` (lot 180), ni les scénarios historiques (Relais, crue, mine, auberge, rixe, atelier, crypte). **Bruts dans
`C:\Users\msics\donjon\artifacts\depart-181\`, jamais dans le worktree.** Termine ton dernier message par `LOT TERMINÉ` (résumé
d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-agendas.md` (§ 4 `protéger`, bilans 167 c à 179), les rapports 167 c, 175 et 179, puis la marche
commune (`spatial`, `pnj._marcher`, `moteur` pour le pas du joueur), la présence (`Monde.verifier`, `present_physique`) et
`agendas` (fin de `protéger` sur mort crue, lot 167 c).

## Définition retenue
- Un scénario peut déclarer une **issue vers l'extérieur** sur une sortie de salle (donnée, par exemple la digue du refuge dans
  `crue_hameau`). Franchir cette issue par la marche commune fait **quitter les lieux** : le personnage passe à l'état
  « parti », reste dans les données (biens compris, avec lui), n'est plus présent, perçu, entendu ni atteignable ; il peut
  revenir par la même issue si un geste ou une donnée l'y ramène.
- Qui le voit franchir l'issue, ou l'apprend par les nouvelles communes (même règle de confiance et de date que les autres
  constats), **le croit parti**. Une croyance « parti » est démentie s'il est revu.
- Un agenda `protéger` envers un protégé cru parti se termine, avec cette cause, publiée à la sortie du choix, sans renaissance ;
  une position simplement inconnue ne termine toujours rien.
- Le joueur suit la même règle : quitter les lieux est un pas par l'issue (la partie se clôt comme une fin de joueur, sauvegardée).

## Hors lot (à dire dans le rapport)
Aucun choix autonome nouveau de partir pour les PNJ (lot ultérieur, à décider) : dans ce lot, un PNJ ne part que par une
marche déjà décidée (épreuve en données de tests, placement d'auteur ou agenda existant dont la destination est l'issue).

## Vérification
- Tests après rechargement, deux cas de même nature : un PNJ part sous les yeux du protecteur (fin de `protéger`), un autre part
  hors de vue puis la nouvelle arrive (fin à la réception) ; position inconnue sans fin ; retour par l'issue qui dément la
  croyance ; joueur qui part (fin de partie sauvegardée) ; même laps d'un bloc ou découpé ; monde et rendu rechargés identiques.
- Empreintes 2 h, quatre scénarios historiques × quatre graines, identiques (données historiques intactes) ; banc rapide 4 h
  de `crue_hameau` × quatre graines (aucune usurpation, plantage ni boucle nouvelle).
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-depart-definitif` poussée (pas `main`).
`docs/plan-agendas.md` (A4b : fait et reste), `docs/etat-dev.md` (« Branche `codex-depart-definitif`, non fusionnée »).
Rapport d'une page : `docs/taches/rapport-codex-181-depart-definitif.md`.
