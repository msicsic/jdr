# Tâche Codex 146 d (A4a, fin) : amener, les sous-buts sociaux (reprise)

Lot de 30 à 45 minutes (`AGENTS.md`) ; **livraison partielle permise** (dis précisément ce qui reste). Pas de Luna. **Poste :
le PC fixe** (`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot tourne sur ce
poste (vérification d'intégration, bancs longs), deux sur le laptop : au plus 2 processus de calcul, priorité réduite. Ce lot
touche `agendas.py`, `deliberation.py`, `planification.py`, `echanges.py`/`social.py` si besoin, le moteur des portes si le
défaut ci-dessous l'exige, les données de la crue et leurs tests ; **pas** `mj.py`, `sources.py`, les fournisseurs,
`narration.py`, `consignes.py`, `paroles.py`. **Bruts dans `C:\Users\msics\donjon\artifacts\amener-146d\` (dépôt principal),
jamais dans le worktree** : l'archivage du worktree les supprime. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une
ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-agendas.md` (§ 4 `amener`, § 6.2 à 6.4, bilans 144, 146, 146 b, 146 c), le brief et le rapport du
lot 146 c (`docs/taches/codex-146c-amener-social.md`, `rapport-codex-146c-amener-social.md`), puis `agendas.py`.

## Le défaut révélé par le lot 146 c (ses bruts sont perdus)
La tentative sociale du lot 146 c (avis de menace, `confier`, marche propre et observation) passait les parcours individuels,
mais l'évacuation collective vers la galerie en crue 2024 s'arrêtait à **120 min** sur `Passage incohérent`, dans la copie d'un
devis : l'invariant « une porte détruite ou détachée est ouverte et déverrouillée » était violé ; un engagement était abandonné
pendant les manœuvres de portes. Cause non isolée.

## Ce qu'il faut faire
1. Réécris les sous-buts sociaux d'`amener` (portée de voix, plus proche d'abord ; avis de menace du lieu quitté si la personne
   ne croit pas déjà le lieu préférable ; demande de déplacement commune `confier`, refus retenu selon sa cause, réveil sur
   croyance nouvelle ; accompagner sans jamais déplacer l'autre), transitions publiées à la sortie du choix (lot 146 b), et
   l'agenda de Gorm dans la crue (amener Ilse et Brune à la galerie).
2. Rejoue la crue 2024 (et une autre graine). **Si `Passage incohérent` réapparaît, isole d'abord l'invariant moteur en cause**
   (où une porte détruite/détachée perd son état ouvert/déverrouillé : geste, devis sur copie, abandon d'engagement), corrige-le
   dans le contrat commun avec un test qui échoue sans le correctif, puis seulement reprends `amener`. Si le temps manque, livre
   le correctif moteur seul et dis ce qui reste d'`amener`.

## Vérification
- Tests après rechargement : Gorm amène Ilse puis Brune à la galerie par la parole et la demande, s'arrête atteint ; refus par
  méfiance : sommeil avec raison, réveil sur croyance nouvelle ; faim désespérée prioritaire ; même laps d'un bloc ou découpé.
- Crue 4 h × quatre graines (dont 2024) sans arrêt, Ilse/Brune à la galerie (base 3/8), passages par heure, aucune usurpation ni
  boucle nouvelle ; empreintes 2 h Relais/mine/auberge × quatre graines identiques ; `VERIFIER` + spatial 0,2 crue 42 et 2024, 2 h.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-amener-social-d` poussée (pas `main`).
`docs/plan-agendas.md`, `docs/etat-dev.md` (« Branche `codex-amener-social-d`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-146d-amener-social.md`.
