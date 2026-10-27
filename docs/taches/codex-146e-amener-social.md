# Tâche Codex 146 e (A4a, fin) : amener, les sous-buts sociaux

Lot de 30 à 45 minutes (`AGENTS.md`) ; **livraison partielle permise** (dis précisément ce qui reste). Pas de Luna. **Poste :
le PC fixe** (`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot tourne sur ce
poste (vérification d'intégration, bancs longs), deux sur le laptop : au plus 2 processus de calcul, priorité réduite. Ce lot
touche `agendas.py`, `deliberation.py`, `planification.py`, `echanges.py`/`social.py` si besoin, les données de la crue et leurs tests ; **pas** `mj.py`, `sources.py`, les fournisseurs,
`narration.py`, `consignes.py`, `paroles.py`. **Bruts dans `C:\Users\msics\donjon\artifacts\amener-146e\` (dépôt principal),
jamais dans le worktree** : l'archivage du worktree les supprime. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une
ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-agendas.md` (§ 4 `amener`, § 6.2 à 6.4, bilans 144, 146, 146 b, 146 c, 146 d), les rapports des
lots 146 c et 146 d (le défaut de porte qui arrêtait l'évacuation collective est corrigé par 146 d), puis `agendas.py`.

## Ce qu'il faut faire
1. Réécris les sous-buts sociaux d'`amener` (portée de voix, plus proche d'abord ; avis de menace du lieu quitté si la personne
   ne croit pas déjà le lieu préférable ; demande de déplacement commune `confier`, refus retenu selon sa cause, réveil sur
   croyance nouvelle ; accompagner sans jamais déplacer l'autre), transitions publiées à la sortie du choix (lot 146 b), et
   l'agenda de Gorm dans la crue (amener Ilse et Brune à la galerie).
2. Rejoue la crue 2024 et une autre graine. Si un autre défaut moteur apparaît, isole son invariant avec un test qui échoue
   sans le correctif, corrige-le dans le contrat commun, et dis ce qui reste d'`amener` si le temps manque.

## Vérification
- Tests après rechargement : Gorm amène Ilse puis Brune à la galerie par la parole et la demande, s'arrête atteint ; refus par
  méfiance : sommeil avec raison, réveil sur croyance nouvelle ; faim désespérée prioritaire ; même laps d'un bloc ou découpé.
- Crue 4 h × quatre graines (dont 2024) sans arrêt, Ilse/Brune à la galerie (base 3/8), passages par heure, aucune usurpation ni
  boucle nouvelle ; empreintes 2 h Relais/mine/auberge × quatre graines identiques ; `VERIFIER` + spatial 0,2 crue 42 et 2024, 2 h.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-amener-social-e` poussée (pas `main`).
`docs/plan-agendas.md`, `docs/etat-dev.md` (« Branche `codex-amener-social-e`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-146e-amener-social.md`.
