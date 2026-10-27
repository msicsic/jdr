# Tâche Codex 194 : on demande la clé au gardien avant de forcer sa porte

Issue de la revue vierge 187 (`docs/taches/rapport-codex-187-revue-vierge-pnj.md`, § 1.4 et P2), décision du 2026-10-27 :
**hameau, graine 1, départ tiré, 4 h : Aubin (honnêteté 65, douceur 80) a froid, veut atteindre le poêle du guet derrière la
porte étanche du beffroi verrouillée ; Gorm vient de ramasser la clé à côté de lui (78 min). Aubin prend le pied-de-biche et
force la porte sous ses yeux (79 min).** Cause relevée par la revue : une porte sans `proprietaire` n'a aucune faute ni dégât
(`brise = None`) et se force pour environ 0,05 × n / c minutes, une vingtaine de fois moins cher que demander la clé
(`1 + DEMANDE / chance`). Les bruts de la revue sont sur le laptop ; rejoue la nuit ici (le lot 189 a depuis supprimé les
départs par la digue : la nuit peut différer, cherche le même moment ou un cas équivalent).

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots calculent sur ce poste (180 c, 195) : au plus 2 processus,
priorité réduite. Fichiers : `planification.py` (coût et faute du bris), `biens.py`, `force.py` si la règle commune du bris y
vit, et leurs tests ; **pas** `ouie.py` (195), `narration.py`/`mj.py` (180 c), ni les scénarios. **Bruts dans
`C:\Users\msics\donjon\artifacts\porte-194\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, les rapports 167 à 167 c, 175, 179 (garder et ses fins), 133 (préconditions), « Forcer » dans
`docs/plan-planificateur.md` et `docs/mecaniques.md`, puis le coût du bris dans `planification.gestes`, `biens.py`, `force.py`.

## L'invariant
**Une installation (porte, contenant fixe) d'un lieu dont quelqu'un a la responsabilité crue — il en garde le lieu, en porte
la clé, ou la tient d'un agenda ou d'une pulsion de garde — est un bien protégé pour qui le sait : la forcer est une faute
envers ce responsable, au prix commun de l'honnêteté et de la douceur, avec ses témoins et ses épreuves relationnelles.** Les
moyens sans faute (demander la clé ou l'ouverture au responsable, attendre qu'il ouvre) se comparent alors sur la même échelle
de coût. Même règle pour le joueur et les PNJ, d'après les croyances de celui qui agit ; une porte réellement sans responsable
connu garde son coût actuel. Aucune règle propre à Aubin, Gorm, au beffroi ou au hameau.

## Vérification
- Tests après rechargement : le cas réel (ou équivalent reproduit) : Aubin demande la clé ou l'ouverture à Gorm au lieu de
  forcer ; un autre cas de même nature (autre scénario, autre porte ou contenant d'un lieu gardé) ; sans responsable cru, le bris
  reste possible au coût actuel ; détresse (désespoir) qui lève la précaution selon l'honnêteté ; même laps d'un bloc ou
  découpé ; monde et rendu rechargés identiques.
- Banc rapide 4 h, quatre scénarios et hameau × quatre graines (références du cache) : portes forcées, demandes de clé,
  crochetages, aucune usurpation, plantage ni boucle nouvelle ; `VERIFIER` + `spatial.VERIFICATION` 0,2, hameau 1985, 2 h
  (une lecture nouvelle du planificateur doit entrer dans `_entrees`).
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-porte-lieu-garde` poussée (pas `main`) ;
`docs/etat-dev.md` (« Branche `codex-porte-lieu-garde`, non fusionnée ») ; rapport d'une page
`docs/taches/rapport-codex-194-porte-lieu-garde.md`.
