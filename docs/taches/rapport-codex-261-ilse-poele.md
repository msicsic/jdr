# Tâche 261 (diagnostic) : Ilse entretient le poêle 450 minutes malgré sa faim (crue 7)

Diagnostic seul, aucun code du jeu modifié. Bruts : `C:\Users\msics\donjon\artifacts\ilse-261\`.

## Reproduction

Nuit crue, graine 7, départ tiré, joueur passif en `chambre_cloche`, 12 h, sur
l'intégration actuelle (commit 2365125). L'épisode est reproduit : Ilse est dans
la `chambre_cloche` et entretient le poêle du guet de la minute 165 à la fin de
la nuit (720 min), alors que sa faim est pressante de la minute 270. Captures
rechargées aux minutes 160, 165, 270, 275, 400, 600, 720 : monde et rendu
identiques après rechargement.

## Explication du choix d'Ilse

- **Profil** : Ilse n'a qu'un besoin déclaré pressant possible, `securite`
  (départ 65, dérive 2/h), et deux pulsions de ronde (`echoppe`, `antichambre`,
  période ~40 min). Le poêle du guet est une pulsion de garde (`motif: empathie`)
  déclenchée par la proximité, non une pulsion rompue à ces instants.
- **Croyances sur les vivres** : Ilse croit les vivres à la réserve
  (`antichambre`, 2 portions à 270 min, 0 à 600 min), source `savoir`, confiance
  0,9. Elle ne croit pas pouvoir les prendre : la réserve est gardée par le
  marchand (elle est honnête, `ne_blesse_pas`).
- **Minute 270/275** : faim = 71,7/72,2 (seuil 70) → `URGENTS = [faim]`,
  intention = `None`. Les deux recours faim de `deliberation._candidats`
  (`_plan_faim` puis `_plan_enquete`) évaluent à `RIEN`. Le planificateur
  (`planification.planifier`, but `faim`) retourne `None`, issue `epuise`
  (1 nœud examiné) : aucun successeur admissible au-delà de l'état initial.
  La faim presse mais n'a aucun recours admissible d'après ses croyances.
- **Minute 400** : faim = 84,7, toujours `URGENTS = [faim]`, intention = `None`,
  les deux recours faim toujours `RIEN`. Les vivres de la réserve sont passés
  à 1 portion (consommés par le marchand/Brune).
- **Minute 600** : faim = 100 (plafond), intention = `None`, recours faim
  toujours `RIEN`. Vivres à 0 portion.

L'entretien du poêle ne "passe devant" la faim dans aucun classement : la faim
est la seule urgence, mais elle n'a pas de recours admissible, donc Ilse attend.
Pendant l'attente, la pulsion de garde du poêle (routine, `motif: empathie`)
s'exécute parce qu'elle est déjà sur place. Le poêle est un feu qu'elle garde,
non un besoin qui prime sur la faim.

## Verdict

Comportement juste. Aucun recours de faim admissible d'après les croyances
d'Ilse : les vivres qu'elle connaît sont à la réserve (`antichambre`), gardés
par le marchand, et elle ne croit pas pouvoir les prendre (honneteté). Le
planificateur ne trouve donc aucun plan pour manger (`epuise`, 1 nœud). Le
recours qui manque est un vivre qu'elle croit pouvoir prendre sans vol, ou une
permission du gardien pour prendre les vivres de la réserve. Aucun défaut de
fonction ou de règle commune n'est identifié ; le mécanisme commun
(`deliberation._candidats` + `planification.planifier`) classe correctement
la faim comme sans recours et laisse la routine de garde s'exécuter pendant
l'attente.