# Tâche Codex 197 (relations 3d) : un besoin d'autrui perçu devient un but de l'empathique

Ordre décidé par l'utilisateur le 2026-10-27 pour la richesse des PNJ : A6 (lots 184, 192, fusionnés) → **3d** → A5. Règle de
`docs/plan-relations.md` § 6.4 et étape 3d, **aucune donnée de scénario nouvelle**. Lot de 30 à 45 minutes (`AGENTS.md`) ;
livraison partielle permise si elle dit ce qui reste. Pas de Luna.

**Poste : le PC fixe** (`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots
calculent sur ce poste (194 : `planification.py`, `biens.py`, `pnj.py`, `moteur.py` ; 195 : `ouie.py`) : au plus 2 processus,
priorité réduite. Fichiers : `deliberation.py` (candidats), `esprits.py` si une lecture du besoin d'autrui y manque, et leurs
tests ; **pas** les fichiers de 194/195, ni `narration.py`/`mj.py`, ni les scénarios. Si une lecture nouvelle entre dans la
recherche, elle va dans `planification._entrees` : dis-le avant de toucher `planification.py` (194 l'a ouvert). **Bruts dans
`C:\Users\msics\donjon\artifacts\empathie-197\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-relations.md` (§ 6.4, étape 3d, épreuves et lectures des relations), les rapports 120 (service
rendu), 167 à 167 c (protéger), 53 (peur transmise), 183 et 187 (richesse, revue vierge), et le correctif `entretenir-feu`
(le protégé nourri en boucle) dans `docs/etat-dev.md`, puis `deliberation._candidats`/`Palier`, la condition `servir`, le feu
entretenu et la compagnie qui rassure.

## L'invariant
**Un besoin d'autrui que le PNJ perçoit (faim ou froid visible au corps, peur lue par les signes, d'après ses seules
perceptions et lectures) devient pour lui un but, s'il n'est pas hostile à cette personne, pondéré par empathie × (affection +
20) / 100 : la nourrir, entretenir un feu pour elle, rester près d'elle si elle a peur. Ce but passe après ses propres besoins
pressants et avant la routine, sur l'échelle commune d'urgence, par les moyens existants ; il cesse quand il voit le besoin
apaisé ou que la personne s'éloigne.** Même règle pour tout PNJ ; le joueur peut en être le bénéficiaire (ses états visibles).
Un secours accompli passe par l'épreuve commune `service_rendu` (lot 120), sans double crédit. Aucune règle propre à un
personnage ou un scénario ; aucune lecture de l'état réel d'autrui que le PNJ n'a pas perçu.

## Vérification
- Tests après rechargement : Mathe sert Lucien qu'elle voit affamé, une fois, puis plus (pas de boucle du protégé nourri) ;
  un autre cas de même nature (un transi près d'un feu à entretenir, ou une peur apaisée par la présence) ; un PNJ hostile ou
  peu empathique n'aide pas ; un besoin non perçu (dos, noir) ne déclenche rien ; propres besoins pressants d'abord ; même laps
  d'un bloc ou découpé ; monde et rendu rechargés identiques.
- Banc rapide 4 h, quatre scénarios et hameau × quatre graines (références du cache) : secours menés à bien, minutes urgentes
  d'autrui apaisées par un autre, minutes sans recours, richesse S/F/D du lot 183
  (`C:/Users/msics/donjon/artifacts/dormants-183/analyser.py`, mêmes définitions) à base identique ; aucune usurpation,
  plantage ni boucle nouvelle ; critère de l'étape 3d : des secours dans la moitié des nuits où un empathique (≥ 70) voit un
  affamé ou un transi, aucun chez qui n'en a pas.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-empathie` poussée (pas `main`) ;
`docs/plan-relations.md` (3d : fait et reste), `docs/etat-dev.md` (« Branche `codex-empathie`, non fusionnée ») ; rapport d'une
page `docs/taches/rapport-codex-197-empathie.md`.
