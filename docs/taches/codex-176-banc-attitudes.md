# Tâche Codex 176 (relations 3g) : aucune attitude racontée sans signe ni impression perçus

Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot tourne sur ce poste (175, agendas et perception) et une
vérification d'intégration sur le laptop (174) : au plus 2 processus de calcul, priorité réduite. Ce lot touche l'audit narratif
(`narration.py`) si une correction est nécessaire, `tools/banc_parties.py` pour préparer la scène, un banc
`tests/data/bancs/attitudes.json` et leurs tests ; **pas** `consignes.py`, `couverture_action.py`, `tenir.py`, `operations.py`,
`deplacement_objet.py` (lots 172/173 en attente de fusion), ni `esprits.py`, `agendas.py`, `deliberation.py` (lot 175).
**Bruts dans `C:\Users\msics\donjon\artifacts\attitudes-176\`, jamais dans le worktree.** Luna : sur ce poste, le coffre est
illisible depuis les agents ; ne joue pas Luna, écris la commande exacte (`tools/banc_multi.py`, référence `cdaf371`, deux passes)
dans `C:\Users\msics\donjon\artifacts\attitudes-176\luna-a-jouer.txt` ; l'orchestrateur la jouera. Termine ton dernier message par
`LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/contrat-mj.md`, `docs/plan-relations.md` (§ 5, 6.5, 8 et 3g), puis ce que reçoit le MJ des attitudes
(`Monde.contexte` : `signes_percus`, `impressions`) et comment l'audit narratif juge une attitude prêtée à un personnage.

## L'invariant
**Une attitude, une émotion ou une intention prêtée à un personnage dans le texte affiché s'appuie sur un signe perçu ou une
impression de Corvus fournis au MJ ; sinon elle est refusée avant affichage, avec `attendu` citant les signes et impressions
disponibles.** Une parole entendue établit qu'elle a été dite, pas l'émotion de son auteur. Établis d'abord, sur le banc, si
l'audit actuel tient déjà cet invariant ; ne corrige que la voie commune qui le manque, sans mot-clé ni règle propre à un
personnage.

## Ce qu'il faut faire
- Banc `attitudes` (§ 3g) préparé par placement : Ilse à l'écart de Brune, Gorm qui surveille, une dispute en cours ou récente,
  une proposition du joueur ; saisies qui invitent Luna à décrire humeurs et intentions (« Comment va Ilse ? », « Gorm a l'air de
  quoi ? », « Brune m'en veut ? », « je regarde la salle »).
- Rejoue sans Luna (MJ simulé) une réponse qui prête une attitude sans appui et une qui cite un signe fourni : refus avec
  `attendu`, puis admission ; état et texte rechargés.
- Si un manque est trouvé, corrige-le dans le contrat commun de l'audit ; sinon le lot livre le banc et le constat.

## Vérification
- Tests ciblés (MJ simulé, console, recharge) ; empreintes 2 h Relais × quatre graines identiques (aucun moteur touché).
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-banc-attitudes` poussée (pas `main`).
`docs/plan-relations.md` (3g : fait et reste), `docs/etat-dev.md` (« Branche `codex-banc-attitudes`, non fusionnée »). Rapport
d'une page : `docs/taches/rapport-codex-176-banc-attitudes.md`.
