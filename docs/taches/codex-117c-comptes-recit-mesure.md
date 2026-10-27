# Tâche Codex 117 c : remesurer les comptes du récit (lot 117 b) sur la base actuelle

Décision de l'utilisateur du 2026-10-27 : **remesurer avant de décider** la fusion de `codex-comptes-recit` (lots 117 et 117 b,
`94a0782`, non fusionnée). Ce lot ne décide pas : il rend la branche à jour et mesurable, puis livre une mesure fiable.

Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le PC fixe** (Luna connectée ; `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`,
copies seulement). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste, deux sur le
laptop : au plus 2 processus de calcul, Luna en **deux exécutions au plus**, priorité réduite. Termine ton dernier message par
`LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/taches/codex-117-comptes-recit.md`, le rapport du lot 117 (et la section 117 b), l'entrée de
`docs/etat-dev.md` (« Branche `codex-comptes-recit`, non fusionnée »), puis le diff `6519588..origin/codex-comptes-recit`
(`narration.py`, `mj.py`).

## Ce qu'il faut faire
1. **Porter** : ta branche `codex-comptes-recit-c` part de l'intégration ; fusionne-y `origin/codex-comptes-recit` et résous les
   conflits sans changer le contrat du lot 117 b (comptes fournis par le moteur, sens fermé et quantité comparés par le moteur).
   Les lots 113, 116, 142, 143 ont touché `mj.py`/`narration.py` depuis : garde leurs contrats. Tests ciblés des comptes et du
   récit verts après rechargement ; aucune autre modification de code.
2. **Mesurer, deux passes Luna**, branche contre **`cdaf371`** (référence en cache depuis le lot 153, relue, jamais rejouée) :
   les quatre scripts de la mesure 117 b, plus `comptes`, `soir-appel`, `ressources` et les quatre bancs de référence.
   Appels et secondes par tour MJ (moyenne et médiane), par fonction (surtout l'audit narratif), relances, refus, replis,
   obstacles narratifs, jetons cachés ; et sur ces parties : inversions de comptes affichées, faux refus de comptes justes.
3. **Rejeu** des cas du lot 117 b (inversion réelle, trois faux refus), cinq fois chacun, critère du lot 95.

## Ce que le rapport doit dire
Le prix en latence et en relances contre le gain de justesse, chiffrés sur deux passes, et si l'écart du lot 117 b
(14,0 → 20,5 s/tour, obstacles 11 → 60) se confirme. Pas de recommandation de fusion à la place de l'utilisateur : les
éléments pour décider.

## Livraison
Branche `codex-comptes-recit-c` poussée (pas `main`), suite complète une fois à la fin (`tools/tests.py --processus 2`) pour
qu'elle soit fusionnable si l'utilisateur le décide. `docs/etat-dev.md` (« Branche `codex-comptes-recit-c`, non fusionnée »).
Rapport d'une page : `docs/taches/rapport-codex-117c-comptes-recit-mesure.md`. Commits signés si une clé est configurée.
