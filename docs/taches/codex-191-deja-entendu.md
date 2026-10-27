# Tâche Codex 191 : on ne confie pas à quelqu'un ce qu'il a déjà entendu

Issue de la revue vierge 187 (`docs/taches/rapport-codex-187-revue-vierge-pnj.md`, § 1.3 et P4). Bruts de la revue :
`C:\Users\msics\donjon\artifacts\revue-187\` sur le laptop (absents du PC fixe ; rejoue la nuit). Cas réel : **mine, graine 1,
départ tiré, 4 h** : les quatre occupants du baraquement se répètent **douze fois** « Odon semble guetter la porte du bureau »
(minutes 40, 41, 52, 55, 62, 126, 136, 137, 138, 146, 236), alors que chacun l'a entendu dire en sa présence. Cause relevée par
la revue : `social._sait` répond « non » d'emblée pour un `avis`, et le registre des faits dits (lot 64/108) ne suit que le couple
locuteur/destinataire, sans ce que les témoins présents viennent d'entendre (`retenir_parole`).

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots calculent sur ce poste (180 c, 184 b) : au plus 2 processus,
priorité réduite. Fichiers : `social.py`, `esprits.py` si le registre l'exige (fonctions de faits dits seulement) et leurs tests ;
**pas** `agendas.py`, `deliberation.py` (184 b), `narration.py`, `mj.py` (180 c), `planification.py`, `presence.py` (189).
**Bruts dans `C:\Users\msics\donjon\artifacts\deja-entendu-191\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou
`QUESTION : …`.

Lis `AGENTS.md`, les rapports 64 (déjà dit), 108 (avis redits), 55 (constats partagés), 121 (disputes) et 187, puis
`social.faits_dits`, `_sait`, `_a_dire`, `_deja_dit`, `bavarder`, `nouvelles`, `retenir_parole`, `recevoir`.

## L'invariant
**Un PNJ ne confie spontanément un fait ou un avis qu'à quelqu'un dont il ne croit pas qu'il le sait déjà : ce que l'auditeur a
vu, ce qu'on lui a dit, et ce qu'il a entendu dire en sa présence (avis compris) dans le même état de la chose.** Un changement
de valeur appris rouvre la confidence (règle des lots 64/108). Même registre pour les témoins d'une parole que pour son
destinataire ; ce que le locuteur croit, jamais ce que l'auditeur sait réellement. Les avis contradictoires (dispute, lot 121)
restent possibles : contredire n'est pas redire. Aucune exception de personnage ou de scénario.

Hors lot (à dire dans le rapport) : les constats triviaux sur ce que le locuteur vient lui-même de faire (« les biscuits sont
épuisés » après les avoir mangés) et la pertinence pour l'auditeur ; dis seulement ce que tu en observes.

## Vérification
- Tests après rechargement : la capture réelle (mine graine 1 avant 40 min) ne redit pas l'avis à qui l'a entendu ; un autre cas
  de même nature (un constat matériel entendu par un témoin, autre scénario) ; un auditeur absent lors de la première parole
  l'apprend encore ; un changement de valeur rouvre la confidence ; une dispute reste possible ; même laps d'un bloc ou découpé ;
  monde et rendu rechargés identiques.
- Banc rapide 4 h, quatre scénarios × quatre graines (références du cache) : avertissements/avis redits et répétitions de
  l'audit avant/après, confidences, disputes, avis adoptés ; aucune usurpation, plantage ni boucle nouvelle.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-deja-entendu` poussée (pas `main`) ;
`docs/etat-dev.md` (« Branche `codex-deja-entendu`, non fusionnée ») ; rapport d'une page
`docs/taches/rapport-codex-191-deja-entendu.md`.
