# Tâche Codex 129 (3c) : calibration des signes selon le critère révisé

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste : au plus 2 processus de calcul,
priorité réduite. Ce lot touche `donjon/signes.py` (constantes de lecture) et ses outils/tests ; **pas** `mj.py`,
`paroles.py`, `consignes.py` (lot 128), ni `deliberation.py`, `pnj.py`, `stratege.py`, `banc_pnj.py` (lot 130).
Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-relations.md` (3c, critère), les rapports `rapport-codex-11-relations-3c.md` et
`rapport-codex-21-signes-calibration.md` (grille de 63 réglages, compromis 4/3/8), puis `donjon/signes.py` (`PENOMBRE`,
`DISSIMULATION`, `BANDE_RIEN`, `interpreter`, `lire`) et l'outil de calibration du lot 21 s'il existe.

## Décision de l'utilisateur (2026-10-26)
Le critère 3c est révisé : **justesse au plus 0,7 à PSY ≤ 9** (au lieu de 0,6) ; restent **méprises < 20 %** de toutes les
lectures et **justesse ≥ 0,8 à PSY ≥ 13**. Réglage **commun** des constantes de lecture (pénombre, dissimulation, largeur de
la zone « rien conclu »), sans réglage par personne, par sorte de signe ni par scénario, et sans changer la règle du jet.

## Ce qu'il faut faire
- Grille sur les trois constantes (autour de 4/3/8), mesurée sur les nuits du banc avec PSY réglées (`banc_pnj --regler`,
  comme au lot 21) : méprises globales, justesse par tranche de PSY, abstention ; choisir le réglage qui tient les trois
  bornes avec la plus faible abstention ; si aucun ne les tient, dire de combien on manque et le meilleur compromis.
- Appliquer le réglage retenu ; mettre à jour le critère dans `docs/plan-relations.md` (3c, décision du 2026-10-26).
- Tests : les tests existants des signes (`test_signes*`) restent verts ou sont adaptés avec la raison écrite (une attente
  de dé ou de seuil, jamais un affaiblissement de ce qu'ils vérifient) ; cas réel du guet (Gorm PSY 14 le lit, PSY 8 non,
  quand le dé le permet) après rechargement.
- Banc rapide 4 h, quatre scénarios × quatre graines contre la base (cache) : méprises, justesse, abstention, aucune
  usurpation ni répétition nouvelle ; suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-signes-critere` poussée (pas `main`).
`docs/etat-dev.md` (« Branche `codex-signes-critere`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-129-signes-critere.md`.
