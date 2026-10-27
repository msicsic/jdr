# Tâche Codex 146 c (A4a, fin) : amener, les sous-buts sociaux

Lot de 30 à 45 minutes (`AGENTS.md`) ; **livraison partielle permise** (dis précisément ce qui reste). Pas de Luna. **Poste :
le PC fixe** (`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce
poste, deux sur le laptop : au plus 2 processus de calcul, priorité réduite. Ce lot touche `agendas.py`, `deliberation.py`,
`planification.py`, `echanges.py`/`social.py` si besoin, les données de la crue et leurs tests ; **pas** `mj.py`, `sources.py`,
les fournisseurs, `narration.py`, `consignes.py`, `couverture_action.py`, `tenir.py`, `operations.py` (lots MJ et force en
cours). Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Déjà livré : le lot 146 (un engagement de déplacement accepté se tient par la marche de son auteur, `confier`) et le lot 146 b
(évaluer un candidat d'agenda n'écrit rien, transitions publiées à la sortie du choix ; fin d'`amener` : atteint sur arrivée
crue, abandonné si la destination est crue noyée). Lis leurs rapports, `docs/plan-agendas.md` (§ 4 `amener`, § 6.2 à 6.4, bilans
144, 146, 146 b), `AGENTS.md`, puis `agendas.py`.

## Ce qu'il faut faire
Les sous-buts d'`amener`, chacun passé comme condition à `chercher` (jamais un plan gardé), sans règle propre à la crue ;
toute transition publiée à la sortie du choix (contrat du lot 146 b) :
1. être à portée de voix de la personne (comme `informer`) ; plusieurs personnes : la plus proche d'abord, à égalité par
   identifiant ;
2. qu'elle croie le lieu préférable : un avis par la parole commune (lots 80, 121), seulement si elle ne le croit pas déjà ;
   si aucun avis commun n'exprime cette préférence, dis-le et utilise l'avis de menace existant pour le lieu quitté ;
3. qu'elle accepte d'y aller : la demande de déplacement commune (`confier`, lot 146), jugée par elle ; un refus est retenu
   selon sa cause (`retenir_refus`), réveil sur croyance nouvelle, jamais au seul délai ;
4. l'accompagner ou la laisser aller : l'amenant ne la déplace jamais ; il peut la suivre ou la précéder.
Abandon aussi pour route crue coupée vers le lieu. **Épreuve en données** : Gorm reçoit dans la crue l'agenda d'amener Ilse et
Brune à la galerie, en plus d'`informer`.

## Vérification
- Tests après rechargement : Gorm amène Ilse puis Brune à la galerie par la parole et la demande (pas de croyance installée par
  le test au-delà du départ), et s'arrête atteint ; une personne qui refuse (méfiance) laisse l'agenda en sommeil avec sa
  raison, réveillé par une croyance nouvelle ; route crue coupée : abandon avec cause ; la faim désespérée de Gorm passe devant ;
  même laps d'un bloc ou découpé, même `data`.
- Empreintes 2 h Relais/mine/auberge × quatre graines contre la base (cache) : identiques. Banc rapide 4 h crue × quatre
  graines : Ilse/Brune à la galerie quand l'eau gagne (base 3/8), en attente, dans l'eau, passages par heure, aucune usurpation
  ni boucle nouvelle ; `VERIFIER` + `spatial.VERIFICATION` 0,2, crue 42, 2 h ; `tools/mesure_cout.py` crue 1985 4 h.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-amener-social` poussée (pas `main`).
`docs/plan-agendas.md` (A4a : fait et reste), `docs/etat-dev.md` (« Branche `codex-amener-social`, non fusionnée »). Rapport
d'une page : `docs/taches/rapport-codex-146c-amener-social.md`.
