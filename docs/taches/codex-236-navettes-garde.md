# Tâche Codex 236 : un but de garde ne fait pas faire la navette

La vérification d'intégration 4306c14 (lot 231, `docs/taches/rapport-codex-231-verif-integ.md`, « Alertes nouvelles »)
relève **Anselme, auberge graine 7, 12 h, 420–479 min : 246 passages en une heure**, dont 68 au couloir et 68 à la salle
commune ; à 430–431, des navettes **sous le même but de garde**. Son maximum ancien (`4d4c625`) était 22 passages/h.
Le compteur 219 ne le voit pas : ce n'est pas un retour entre buts, mais un but durable dont le trajet ne progresse pas.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna.

**Poste : le laptop** (l'utilisateur y travaille) : au plus 2 processus, priorité réduite. Les bruts du lot 231 sont sur
l'autre poste : rejoue la nuit (auberge, graine 7, départ tiré, joueur au dortoir comme l'audit `tools/audit_nuits.py`)
jusqu'à 420 min sur un worktree détaché de `4306c14`, puis sur l'intégration actuelle ; une seule nuit à la fois.

**Fichiers** : le plan de garde et sa poursuite (`deliberation`, `planification` : fonctions de garde, de trajet et de
progression du plan en cours) et leurs tests. **Pas** : `biens.services_proteges` et la publication des clôtures (lot 232),
`ouie.py` et `echanges.tenu` (lot 233), `signes.place` et le raccord de `pnj.agir` à l'attitude de place (lot 234),
`social.py` (lot 235), le MJ. Si la cause est dans un de ces fichiers, arrête-toi et pose la `QUESTION`.

**Bruts dans `C:\Users\msics\donjon\artifacts\navettes-236\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou
`QUESTION : …`.

## Ce qu'on te demande
1. Reproduire : capture juste avant 420 min, puis dire minute par minute pourquoi Anselme repart (plan reconstruit, cible
   de garde qui change, lieu cru de sa charge qui bascule, trajet interrompu par un autre geste…). Dire si la même rafale
   existe sur l'intégration actuelle (après 218, 229, 230).
2. **Invariant** : sous un but durable inchangé, un PNJ ne refait pas en sens inverse un trajet qu'il vient de parcourir
   sans entrée nouvelle (croyance, perception, refus, palier) qui le justifie ; un plan reconstruit reprend le progrès
   déjà accompli. Aucune règle propre à Anselme, à l'auberge ou à la garde d'un bien particulier.
3. Corriger le contrat commun en cause ; si la cause est hors des fichiers autorisés, la décrire et poser la `QUESTION`.

## Vérification
- Tests après rechargement : le cas réel (capture) sans rafale, un autre cas de même nature (autre gardien ou autre
  scénario), même laps d'un bloc ou découpé, monde et rendu rechargés identiques.
- Banc rapide 4 h, cinq scénarios × quatre graines, références du cache, compteur 219 : suspects sans hausse, maximum de
  passages par heure dit pour chaque scénario.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
- Branche `codex-navettes-garde` poussée (pas `main`). Si la poussée est bloquée par la revue, laisse le commit local
  et dis-le.
- `docs/etat-dev.md` : « Branche `codex-navettes-garde`, non fusionnée ».
- Rapport d'une page `docs/taches/rapport-codex-236-navettes-garde.md`.
