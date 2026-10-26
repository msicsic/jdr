# Tâche Codex 146 (A4a, fin) : amener quelqu'un en un lieu

Lot de 30 à 45 minutes (`AGENTS.md`) ; **livraison partielle permise** (dis précisément ce qui reste). Pas de Luna. **Poste :
le PC fixe** (`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent
sur ce poste (dont une vérification d'intégration qui joue des bancs) : au plus 2 processus de calcul, priorité réduite. Ce lot
touche `agendas.py`, `deliberation.py`, `planification.py`, `echanges.py`/`social.py` si besoin, les données de la crue et leurs
tests ; **pas** `mj.py`, `paroles.py`, `narration.py`, `consignes.py`, `couverture_action.py` (lot 147). Termine ton dernier
message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-agendas.md` (§ 4 sorte `amener`, § 6.2 à 6.4, le bilan du lot 144 sous A4), le rapport du lot 144
(`docs/taches/rapport-codex-144-agendas-a4a.md`), puis `agendas.py` (activation, `informer`, `planifier`, `poids`), les
propositions faute de mieux (3e, `pnj_propositions`) et les avis de menace (lot 121, `social`).

## Ce qu'il faut faire
- **La sorte `amener`** (qui, lieu ; manière `sans_violence` par défaut) sur le socle du lot 144, sans règle propre à la crue :
  sous-buts dans l'ordre du plan, chacun passé comme condition à `chercher` (jamais un plan gardé dans l'agenda) :
  1. être à portée de voix de la personne (route crue, comme `informer`) ;
  2. qu'elle croie le lieu préférable : un avis par la parole commune (lots 80, 121), si elle ne le croit pas déjà ;
  3. qu'elle accepte d'y aller : une proposition (3e) ou une demande commune, jugée par elle avec ses propres croyances ;
     un refus est retenu selon sa cause (`retenir_refus`), sans réessai au seul délai ;
  4. l'accompagner : la personne se rend au lieu par **son** planificateur (l'accord crée chez elle un engagement ou un
     rendez-vous existant), l'amenant la suit ou la précède ; aucune téléportation, aucune décision prise à sa place.
- **Atteint** quand l'amenant croit la personne au lieu (vue ou parole) ; **abandonné** si le lieu devient cru impossible
  (route coupée, lieu noyé attendu), cause retenue ; plusieurs personnes : la plus proche d'abord, à égalité par identifiant.
- **Épreuve en données** : Gorm reçoit dans la crue l'agenda d'amener Ilse et Brune à la galerie (données seulement), en
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
Commits signés si une clé est configurée (sinon le dire), branche `codex-agendas-amener` poussée (pas `main`).
`docs/plan-agendas.md` (A4a : fait et reste), `docs/etat-dev.md` (« Branche `codex-agendas-amener`, non fusionnée »).
Rapport d'une page : `docs/taches/rapport-codex-146-agendas-amener.md`.
