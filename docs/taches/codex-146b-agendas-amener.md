# Tâche Codex 146 b (A4a, fin) : l'agenda amener

Lot de 30 à 45 minutes (`AGENTS.md`) ; **livraison partielle permise** (dis précisément ce qui reste). Pas de Luna. **Poste :
le PC fixe** (`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot tourne sur ce
poste (vérification d'intégration qui joue des bancs longs) : au plus 2 processus de calcul, priorité réduite. Ce lot touche
`agendas.py`, `deliberation.py`, `planification.py`, `echanges.py`/`social.py` si besoin, les données de la crue et leurs
tests ; **pas** `mj.py`, `paroles.py`, `narration.py`, `consignes.py`. Termine ton dernier message par `LOT TERMINÉ` (résumé
d'une ligne) ou par `QUESTION : …`.

Le lot 146 a livré le prérequis : un engagement de déplacement accepté (`confier`, `{objet: auteur, lieu: destination}`) se
tient par la marche de son auteur, choisie par **son** planificateur (rapport `docs/taches/rapport-codex-146-agendas-amener.md`).
Lis aussi `AGENTS.md`, `docs/plan-agendas.md` (§ 4 sorte `amener`, § 6.2 à 6.4, bilans des lots 144 et 146 sous A4), le
brief et le rapport du lot 144, puis `agendas.py` (activation, `informer`, `planifier`, `poids`).

## Ce qu'il faut faire
- **La sorte `amener`** (qui, lieu ; manière `sans_violence` par défaut) sur le socle du lot 144 ; chaque sous-but passé comme
  condition à `chercher`, jamais un plan gardé dans l'agenda, aucune règle propre à la crue :
  1. être à portée de voix de la personne (comme `informer`) ;
  2. qu'elle croie le lieu préférable : un avis par la parole commune (lots 80, 121), seulement si elle ne le croit pas déjà ;
  3. qu'elle accepte d'y aller : la demande de déplacement commune du lot 146 (`confier`), jugée par elle ; un refus est
     retenu selon sa cause (`retenir_refus`), sans réessai au seul délai ;
  4. l'accompagner ou la laisser aller : l'amenant ne la déplace jamais ; il peut la suivre ou la précéder.
- **Atteint** quand l'amenant croit la personne au lieu (vue ou parole) ; **abandonné** si le lieu devient cru impossible
  (route coupée, lieu noyé attendu), cause retenue ; plusieurs personnes : la plus proche d'abord, à égalité par identifiant.
- **Épreuve en données** : dans la crue, Gorm reçoit l'agenda d'amener Ilse et Brune à la galerie (données seulement), en
  plus d'`informer`.

## Vérification
- Tests après rechargement : Gorm amène Ilse puis Brune à la galerie et s'arrête atteint ; une personne qui refuse (méfiance)
  laisse l'agenda en sommeil avec sa raison, réveillé par une croyance nouvelle ; route crue coupée : abandon avec cause ;
  la faim désespérée de Gorm passe devant ; même laps d'un bloc ou découpé, même `data`.
- Empreintes 2 h Relais/mine/auberge × quatre graines contre la base (cache) : identiques. Banc rapide 4 h crue × quatre
  graines : PNJ à la galerie quand l'eau gagne, en attente, dans l'eau, passages par heure, aucune usurpation ni boucle
  nouvelle ; `tools/mesure_cout.py` crue 1985 4 h pour le coût en recherches.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-agendas-amener-b` poussée (pas `main`).
`docs/plan-agendas.md` (A4a : fait et reste), `docs/etat-dev.md` (« Branche `codex-agendas-amener-b`, non fusionnée »).
Rapport d'une page : `docs/taches/rapport-codex-146b-agendas-amener.md`.
