# Tâche Codex 195 : les pas d'un compagnon connu ne sont pas ceux d'un intrus

Issue de la revue vierge 187 (`docs/taches/rapport-codex-187-revue-vierge-pnj.md`, § 1.2 et P5), décision du 2026-10-27.
Cas relevés dans les nuits de la revue (4 h, départ tiré ; bruts sur le laptop, rejoue-les ici) :
- **Relais, graine 1** : 46 retournements sur 68 gestes ; à 196 et 238 min, Gorm, Ilse et Aubin font 8 à 11 « se retourne au
  bruit » dans la même minute dès qu'un voisin bouge hors de leur cône ;
- **hameau, graine 1** : Maël passe ses 4 h à se retourner (×53) et retient 17 « bruits inconnus » du refuge, derrière la
  cloison, où il sait ses compagnons ;
- **auberge, graine 1** : à chaque ronde d'Hugues dans le couloir de l'étage (40, 92, 135, 187, 239 min), Odile entend un
  bruit inconnu et monte voir.
Cause relevée par la revue : `ouie._crus_la` n'attribue un bruit qu'à une case près (`PRES_DE = 1`) de la dernière case vue.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots calculent sur ce poste (180 c, 194) : au plus 2 processus,
priorité réduite. Fichiers : `ouie.py` et ses tests ; **pas** `planification.py`/`biens.py` (194), `narration.py`/`mj.py`
(180 c), `social.py`. **Bruts dans `C:\Users\msics\donjon\artifacts\pas-195\`.** Termine par `LOT TERMINÉ` (résumé d'une
ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-ouie.md` (dont « Témoins par l'ouïe, le bruit de sa salle, l'examen vain »), les rapports 69 et
188 (indices de recherche, appels), puis `ouie.retentir`, `_crus_la`, l'interprétation d'un bruit et les témoins par l'ouïe.

## L'invariant
**Un bruit ordinaire (pas, geste) entendu d'un lieu où l'auditeur croit qu'un personnage connu se trouve, ou qu'il fait une
ronde connue, et compatible avec le temps écoulé depuis qu'il l'y a perçu (distance qu'il a pu parcourir à la marche), est
attribué à ce personnage, sans retournement ni « bruit inconnu ».** Un bruit inhabituel (fracas, appel, crochetage), plus fort
que ce que ce personnage fait d'ordinaire, ou venant d'un lieu où personne de connu n'est cru, reste inconnu et se traite comme
aujourd'hui. Même règle pour le joueur et les PNJ, d'après les seules croyances de l'auditeur ; une attribution peut être une
méprise (un voleur pris pour un compagnon), c'est voulu. Aucune règle propre à un personnage, une salle ou un scénario.

## Vérification
- Tests après rechargement : les trois cas réels (ou leurs équivalents reproduits) ; un autre cas de même nature ; un bruit
  inhabituel d'un même lieu reste inconnu ; un compagnon cru parti depuis trop longtemps pour être là n'absorbe pas le bruit ;
  le témoin par l'ouïe d'un geste illicite (`plan-ouie.md`) reste établi quand l'auteur était cru là ; même laps d'un bloc ou
  découpé ; monde et rendu rechargés identiques.
- Banc rapide 4 h, quatre scénarios et hameau × quatre graines (références du cache) : retournements, bruits inconnus, « aller
  voir », vols vus ou entendus, avant/après ; aucune usurpation, plantage ni boucle nouvelle ; richesse S/F/D du lot 183
  (`C:/Users/msics/donjon/artifacts/dormants-183/analyser.py`) à base identique.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-pas-compagnons` poussée (pas `main`) ;
`docs/plan-ouie.md` (la règle change), `docs/etat-dev.md` (« Branche `codex-pas-compagnons`, non fusionnée ») ; rapport d'une
page `docs/taches/rapport-codex-195-pas-compagnons.md`.
